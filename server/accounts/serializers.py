from django.contrib.auth.models import Group
from accounts.models.patient import PatientProfile
from accounts.models.doctor import DoctorProfile
from accounts.models.notification import Notification
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models.user import User
from rest_framework.exceptions import AuthenticationFailed


DOCTOR_SPECIALIZATION_CHOICES = [
    ("General Medicine", "General Medicine"),
    ("Cardiology", "Cardiology"),
    ("Dermatology", "Dermatology"),
    ("ENT", "ENT"),
    ("Pediatrics", "Pediatrics"),
    ("Orthopedics", "Orthopedics"),
    ("Neurology", "Neurology"),
    ("Ophthalmology", "Ophthalmology"),
    ("Dentistry", "Dentistry"),
]


class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ['user', 'dateOfBirth', 'gender']
        read_only_fields = ['user']


class DoctorProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = ['id', 'user', 'specialization', 'consultationDuration', 'bio', 'is_approved', 'approved_by_name', 'approved_at']
        read_only_fields = ['id', 'is_approved', 'approved_by_name', 'approved_at']

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'phone': obj.user.phone,
        }

    def get_approved_by_name(self, obj):
        return obj.approved_by.first_name if obj.approved_by else None


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'status', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True, read_only=True)
    roles = serializers.SerializerMethodField(read_only=True)
    patient_profile = PatientProfileSerializer(read_only=True, required=False)
    doctor_profile = DoctorProfileSerializer(read_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone', 'is_active',
            'groups', 'roles', 'patient_profile', 'doctor_profile',
        ]
        read_only_fields = ['id', 'is_active']

    def get_roles(self, obj):
        return [g.name for g in obj.groups.all()]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone']
        read_only_fields = ['email']

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    user_role = serializers.ChoiceField(choices=['patient', 'doctor'])
    specialization = serializers.ChoiceField(
        choices=DOCTOR_SPECIALIZATION_CHOICES,
        required=False,
        allow_blank=True
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'password_confirm', 'user_role', 'specialization']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        if data['user_role'] not in ['patient', 'doctor']:
            raise serializers.ValidationError("user_role must be 'patient' or 'doctor'.")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        
        if data.get("user_role") == "doctor" and not data.get("specialization"):
            raise serializers.ValidationError({
                "specialization": "Specialization is required for doctor registration."
            })
        
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user_role = validated_data.pop('user_role')
        specialization = validated_data.pop('specialization', '')
        validated_data.pop('username', None)

        user = User.create_user(**validated_data)

        if user_role == 'patient':
            group = Group.objects.get(name='Patients')
            user.groups.add(group)
            PatientProfile.createPatient(user)

        elif user_role == 'doctor':
            group = Group.objects.get(name='Doctors')
            user.groups.add(group)
            DoctorProfile.createDoctor(
                user,
                specialization=specialization
            )
            user.is_active = False
            user.save(update_fields=['is_active'])

            admin_users = User.objects.filter(groups__name='Admins')

            Notification.objects.bulk_create([
                Notification(
                    user=admin,
                    message=(
                        f"New doctor registration pending approval: "
                        f"{user.get_full_name() or user.email}"
                    ),
                    status='confirmation',
                )
                for admin in admin_users
            ])

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user and not user.is_active:
            is_doctor = user.groups.filter(name="Doctors").exists()

            if is_doctor and hasattr(user, "doctor_profile") and not user.doctor_profile.is_approved:
                raise AuthenticationFailed(
                    "Your doctor account is pending admin approval."
                )

            raise AuthenticationFailed(
                "Your account is inactive. Please contact the administrator."
            )

        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        data['roles'] = [group.name for group in self.user.groups.all()]
        return data
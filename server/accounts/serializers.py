from django.contrib.auth.models import Group
from accounts.models.patient import PatientProfile
from accounts.models.doctor import DoctorProfile
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models.user import User
from accounts.models.notification import Notification

class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ['user', 'dateOfBirth', 'gender']
        read_only_fields = ['user']

class DoctorProfileSerializer(serializers.ModelSerializer):
    approved_by_name = serializers.SerializerMethodField(read_only=True) 
    
    class Meta:
        model = DoctorProfile
        fields = ['id', 'user', 'specialization', 'consultationDuration', 'bio', 'is_approved', 'approved_by_name', 'approved_at']
        read_only_fields = ['id', 'user', 'is_approved', 'approved_by_name', 'approved_at']
    
    def get_approved_by_name(self, obj): 
        return obj.approved_by.first_name if obj.approved_by else None

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'status', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True, read_only=True)

    patient_profile = PatientProfileSerializer(read_only=True, required=False)
    doctor_profile = DoctorProfileSerializer(read_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'is_active', 'groups', 'patient_profile', 'doctor_profile']
        read_only_fields = ['id', 'is_active']

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

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'password_confirm', 'user_role']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        if data['user_role'] not in ['patient', 'doctor']:
            raise serializers.ValidationError("user_role must be 'patient' or 'doctor'.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user_role = validated_data.pop('user_role')
        validated_data.pop('username', None)
        
        user = User.create_user(**validated_data)        
        
        if user_role == 'patient':
            group = Group.objects.get(name='Patients')
            user.groups.add(group)
            PatientProfile.createPatient(user)
            user.is_active = True
        
        elif user_role == 'doctor':
            group = Group.objects.get(name='Doctors')
            user.groups.add(group)
            DoctorProfile.createDoctor(user)
            user.is_active = False 
        
        user.save()
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        data['roles'] = [group.name for group in self.user.groups.all()]
        return data
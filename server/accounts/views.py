from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny

from rest_framework_simplejwt.views import TokenObtainPairView

from django.utils import timezone
from django.contrib.auth.models import Group

from accounts.serializers import UserRegistrationSerializer, UserProfileSerializer, UserSerializer, CustomTokenObtainPairSerializer, PatientProfileSerializer, DoctorProfileSerializer, NotificationSerializer

from accounts.models.user import User
from accounts.models.doctor import DoctorProfile
from accounts.models.patient import PatientProfile
from accounts.models.notification import Notification
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.isAdmin

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.isDoctor

class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.isPatient

class IsReceptionist(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.isReceptionist

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.patient_profile
            serializer = PatientProfileSerializer(profile)
            return Response(serializer.data)
        except PatientProfile.DoesNotExist:
            return Response({"detail": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if hasattr(request.user, 'patient_profile'):
            return Response({"detail": "Patient profile already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PatientProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            profile = serializer.save(user=request.user)
            return Response(PatientProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        try:
            profile = request.user.patient_profile
            serializer = PatientProfileSerializer(profile, data=request.data, partial=True)
            
            if serializer.is_valid():
                profile = serializer.save()
                return Response(PatientProfileSerializer(profile).data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PatientProfile.DoesNotExist:
            return Response({"detail": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)

class DoctorProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.doctor_profile
            serializer = DoctorProfileSerializer(profile)
            return Response(serializer.data)
        except DoctorProfile.DoesNotExist:
            return Response({"detail": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if hasattr(request.user, 'doctor_profile'):
            return Response({"detail": "Doctor profile already exists. Use PUT to update."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DoctorProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            profile = serializer.save(user=request.user)
            return Response(DoctorProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        try:
            profile = request.user.doctor_profile
            serializer = DoctorProfileSerializer(profile, data=request.data, partial=True)
            
            if serializer.is_valid():
                profile = serializer.save()
                return Response(DoctorProfileSerializer(profile).data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except DoctorProfile.DoesNotExist:
            return Response({"detail": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)

class UserListView(ModelViewSet):
    queryset = User.objects.select_related('patient_profile', 'doctor_profile').prefetch_related('groups')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

class AdminUserCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        phone = request.data.get('phone')
        role = request.data.get('role')
        
        if not all([email, password, first_name, last_name, role]):
            return Response({'detail': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
        if role not in ['admin', 'receptionist']:
            return Response({'detail': 'Role must be admin or receptionist'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'detail': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            username=email
        )
        
        if role == 'admin':
            group = Group.objects.get(name='Admins')
        else:
            group = Group.objects.get(name='Receptionists')
        
        user.groups.add(group)
        user.is_active = True
        user.save()
        
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class ApproveDoctorView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        try:
            doctor_profile = DoctorProfile.objects.get(pk=pk)
        except DoctorProfile.DoesNotExist:
            return Response({'detail': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if doctor_profile.is_approved:
            return Response({'detail': 'Doctor is already approved'}, status=status.HTTP_400_BAD_REQUEST)
        
        doctor_profile.is_approved = True
        doctor_profile.approved_by = request.user
        doctor_profile.approved_at = timezone.now()
        doctor_profile.save()
        
        doctor_profile.user.is_active = True
        doctor_profile.user.save()
        
        return Response({
            'message': 'Doctor approved successfully',
            'doctor': DoctorProfileSerializer(doctor_profile).data
        }, status=status.HTTP_200_OK)


class PendingDoctorsListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        pending_doctors = DoctorProfile.objects.filter(is_approved=False)
        serializer = DoctorProfileSerializer(pending_doctors, many=True)
        return Response(serializer.data)

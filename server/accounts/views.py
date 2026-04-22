from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny

from rest_framework_simplejwt.views import TokenObtainPairView

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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

@method_decorator(csrf_exempt, name='dispatch')
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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
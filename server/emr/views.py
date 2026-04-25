from django.shortcuts import get_object_or_404

from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, permissions, status
from .models import ConsultationRecord
from .serializers import ConsultationRecordSerializer

# Create your views here.

class IsDoctorUser(permissions.BasePermission):
    """1- Allows only doctors
       2- Used for create/update consultation records"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated or not request.user.isDoctor:
            return False
        else:
            return True
        
class IsReceptionistUser(permissions.BasePermission):
    """access denied for receptionist to access EMR"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.isReceptionist:
            return PermissionDenied("Receptionists cannot access medical records.")

class CanViewConsultationRecord(permissions.BasePermission):
    """
    Allows:
    - Doctor assigned to the appointment
    - Patient who owns the appointment

    Blocks:
    - Receptionist
    - Other users
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.isReceptionist:
            return PermissionDenied("Receptionists cannot access medical records")
        if request.user.isDoctor:
            return obj.appointment_id.doctor_id.user == user
        if user.isPatient:
            return obj.appointment_id.patient_id.user == user

        return False
 
class CanUpdateConsultationRecord(permissions.BasePermission):
    """Allow only doctor to update his own consultations"""
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not request.user or not request.user.is_authenticated or not user.isDoctor:
            return False
        if request.user.isDoctor:
            return obj.appointment_id.doctor_id.user == user
     
class CanCreateViewOfConsultationRecord(APIView):
    """Only doctor create consultation record"""
    def post(self, request):
        if not IsDoctorUser().has_permission(request, self):
            raise PermissionDenied("You aren't allowed to create a consultation")

        if not IsAuthenticated().has_permission(request, self):
            raise NotAuthenticated("Authentication is required.")
        
        serializer = ConsultationRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.validated_data["appointment_id"]
        if appointment.doctor_id.user != request.user:
            raise PermissionDenied(
                "You can only create a consultation for your own appointment."
            )
        consultation = serializer.save(created_by=request.user)
        response_serializer = ConsultationRecordSerializer(consultation)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    

class DoctorPatientViewConsultationRecord(APIView):
    """Doctor can view full record.
    Patient can view own record as read-only.
    Receptionist is blocked.
    """
    def get(self, request, appointment_id):
        if not IsAuthenticated().has_permission(request, self):
            raise NotAuthenticated("Authentication is required.")
        
        if request.user.isReceptionist:
            raise PermissionDenied("Receptionists cannot access medical records.")

        consultation = get_object_or_404(
            ConsultationRecord,
            appointment_id=appointment_id
        )
        
        can_view = CanViewConsultationRecord().has_object_permission(request,self,consultation)
        if not can_view:
            raise PermissionDenied("You do not have permission to view this consultation.")

        serializer = ConsultationRecordSerializer(consultation)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        
class ConsultationRecordUpdateView(APIView):
    def put(self, request, pk):
        if not IsAuthenticated().has_permission(request, self):
            raise NotAuthenticated("Authentication is required.")
        if not IsDoctorUser().has_permission(request, self):
            raise PermissionDenied("You aren't allowed to update a consultation")
        
        consultation = get_object_or_404(ConsultationRecord, pk=pk)        
        can_edit=CanUpdateConsultationRecord().has_object_permission( request,self, consultation)
        if not can_edit:
            raise PermissionDenied("You do not have permission to update this consultation.")
        
        serializer = ConsultationRecordSerializer(consultation , data = request.data, partial = True)
        serializer.is_valid(raise_exception=True)
        consultation = serializer.save()
        response_serializer = ConsultationRecordSerializer(consultation)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )

            
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, status
from emr.models import ConsultationRecord
from emr.serializers import ConsultationRecordSerializer

class IsDoctorUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated or not request.user.isDoctor:
            return False
        else:
            return True
        
class IsReceptionistUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.isReceptionist:
            raise PermissionDenied("Receptionists cannot access medical records.")
        
        return True

class CanViewConsultationRecord(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.isReceptionist:
            raise PermissionDenied("Receptionists cannot access medical records")
        if request.user.isDoctor:
            return obj.appointment_id.doctor_id.user == user
        
        if user.isPatient:
            return obj.appointment_id.patient_id.user == user

        return False
 
class CanUpdateConsultationRecord(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
      
        if not request.user or not request.user.is_authenticated or not user.isDoctor:
            return False
      
        if request.user.isDoctor:
            return obj.appointment_id.doctor_id.user == user
     
class CanCreateViewOfConsultationRecord(APIView):
    def post(self, request):
        if not IsAuthenticated().has_permission(request, self):
            raise NotAuthenticated("Authentication is required.")
        
        if not IsDoctorUser().has_permission(request, self):
            raise PermissionDenied("You aren't allowed to create a consultation")

        
        serializer = ConsultationRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
      
        appointmentRecord = serializer.validated_data["appointment_id"]
      
        if appointmentRecord.doctor_id.user != request.user:
            raise PermissionDenied("You can only create a consultation for your own appointment.")
        
        consultationRecord = serializer.save(created_by=request.user)
        
        responseSerializer = ConsultationRecordSerializer(consultationRecord)
        
        return Response(responseSerializer.data, status=status.HTTP_201_CREATED)
    

class DoctorPatientViewConsultationRecord(APIView):
    def get(self, request, appointment_id):
        if not IsAuthenticated().has_permission(request, self):
            raise NotAuthenticated("Authentication is required.")
        
        if request.user.isReceptionist:
            raise PermissionDenied("Receptionists cannot access medical records.")

        if request.user.isDoctor:
            consultationRecord = get_object_or_404(
                ConsultationRecord,
                appointment_id=appointment_id,
                appointment_id__doctor_id__user=request.user
            )

        elif request.user.isPatient:
            consultationRecord = get_object_or_404(
                ConsultationRecord,
                appointment_id=appointment_id,
                appointment_id__patient_id__user=request.user
            )

        else:
            raise PermissionDenied("You do not have permission to view this consultation.")

        serializer = ConsultationRecordSerializer(consultationRecord)
        
        return Response(serializer.data, status=status.HTTP_200_OK)     
        
class ConsultationRecordUpdateView(APIView):
    def get(self, request, pk):
        if not IsAuthenticated().has_permission(request, self):
            raise NotAuthenticated("Authentication is required.")

        if not IsDoctorUser().has_permission(request, self):
            raise PermissionDenied("You aren't allowed to view this consultation for editing.")

        consultationRecord = get_object_or_404(ConsultationRecord, pk=pk)

        canEdit = CanUpdateConsultationRecord().has_object_permission(request, self, consultationRecord)

        if not canEdit:
            raise PermissionDenied("You do not have permission to edit this consultation.")

        serializer = ConsultationRecordSerializer(consultationRecord)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if not IsAuthenticated().has_permission(request, self):
            raise NotAuthenticated("Authentication is required.")

        if not IsDoctorUser().has_permission(request, self):
            raise PermissionDenied("You aren't allowed to update a consultation")
        
        consultationRecord = get_object_or_404(ConsultationRecord, pk=pk)        

        canEdit = CanUpdateConsultationRecord().has_object_permission(request, self, consultationRecord)

        if not canEdit:
            raise PermissionDenied("You do not have permission to update this consultation.")
        
        serializer = ConsultationRecordSerializer(consultationRecord, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        consultationRecord = serializer.save()
        responseSerializer = ConsultationRecordSerializer(consultationRecord)

        return Response(responseSerializer.data, status=status.HTTP_200_OK)
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
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.isDoctor
        )

class CanViewConsultationRecord(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.isReceptionist:
            raise PermissionDenied("Receptionists cannot access medical records.")
        if user.isDoctor:
            return obj.appointment_id.doctor_id.user == user
        if user.isPatient:
            return obj.appointment_id.patient_id.user == user
        return False

class CanUpdateConsultationRecord(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated or not user.isDoctor:
            return False
        return obj.appointment_id.doctor_id.user == user


class CanCreateViewOfConsultationRecord(APIView):
    def post(self, request):
        if not IsAuthenticated().has_permission(request, self):
            raise NotAuthenticated("Authentication is required.")
        if not IsDoctorUser().has_permission(request, self):
            raise PermissionDenied("You aren't allowed to create a consultation.")

        serializer = ConsultationRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment = serializer.validated_data["appointment_id"]
        if appointment.doctor_id.user != request.user:
            raise PermissionDenied("You can only create a consultation for your own appointment.")

        record = serializer.save(created_by=request.user)
        return Response(ConsultationRecordSerializer(record).data, status=status.HTTP_201_CREATED)


class DoctorPatientViewConsultationRecord(APIView):
    def get(self, request, appointment_id):
        if not IsAuthenticated().has_permission(request, self):
            raise NotAuthenticated("Authentication is required.")
        if request.user.isReceptionist:
            raise PermissionDenied("Receptionists cannot access medical records.")

        if request.user.isDoctor:
            record = get_object_or_404(
                ConsultationRecord,
                appointment_id=appointment_id,
                appointment_id__doctor_id__user=request.user,
            )
        elif request.user.isPatient:
            record = get_object_or_404(
                ConsultationRecord,
                appointment_id=appointment_id,
                appointment_id__patient_id__user=request.user,
                appointment_id__status="COMPLETED",
            )
        else:
            raise PermissionDenied("You do not have permission to view this consultation.")

        return Response(ConsultationRecordSerializer(record).data, status=status.HTTP_200_OK)


class ConsultationRecordUpdateView(APIView):
    def get(self, request, pk):
        if not IsAuthenticated().has_permission(request, self):
            raise NotAuthenticated("Authentication is required.")

        record = get_object_or_404(ConsultationRecord, pk=pk)

        if not request.user.isDoctor:
            raise PermissionDenied("You do not have permission to view this consultation.")

        if not CanUpdateConsultationRecord().has_object_permission(request, self, record):
            raise PermissionDenied("You do not have permission to view this consultation.")

        return Response(ConsultationRecordSerializer(record).data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if not IsAuthenticated().has_permission(request, self):
            raise NotAuthenticated("Authentication is required.")
        if not IsDoctorUser().has_permission(request, self):
            raise PermissionDenied("You aren't allowed to update a consultation.")

        record = get_object_or_404(ConsultationRecord, pk=pk)

        if not CanUpdateConsultationRecord().has_object_permission(request, self, record):
            raise PermissionDenied("You do not have permission to update this consultation.")

        serializer = ConsultationRecordSerializer(record, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        record = serializer.save()
        return Response(ConsultationRecordSerializer(record).data, status=status.HTTP_200_OK)
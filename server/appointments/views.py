from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from appointments.models import Appointment, RescheduleHistory, WaitingList
from scheduling.models import TimeSlot
from appointments.permissions import IsPatient, IsDoctor, IsReceptionist, IsDoctorOrReceptionist
from appointments.serializers import (
    AppointmentReadSerializer,
    AppointmentWriteSerializer,
    RescheduleSerializer,
    RescheduleHistorySerializer,
    QueueSerializer,
    WaitingListReadSerializer,
    WaitingListWriteSerializer,
)

TRANSITIONS = {
    "REQUESTED": {
        'confirm': ("CONFIRMED", ['doctor', 'receptionist']),
        'cancel': ("CANCELLED", ['patient', 'doctor', 'receptionist']),
    },
    "CONFIRMED": {
        'check_in': ("CHECKED_IN", ['receptionist']),
        'cancel': ("CANCELLED", ['patient', 'doctor', 'receptionist']),
        'no_show': ("NO_SHOW", ['doctor', 'receptionist']),
    },
    "CHECKED_IN": {
        'complete': ("COMPLETED", ['doctor']),
    },
}


def _user_role(user):
    if user.isDoctor:
        return 'doctor'
    if user.isReceptionist:
        return 'receptionist'
    if user.isPatient:
        return 'patient'
    return None


def _apply_transition(appointment, actionName, user):
    current = appointment.status
    available = TRANSITIONS.get(current, {})

    if actionName not in available:
        return False, f"Cannot perform '{actionName}' on an appointment with status '{current}'."

    nextStatus, allowedRoles = available[actionName]
    role = _user_role(user)

    if role not in allowedRoles:
        return False, f"Your role ('{role}') is not allowed to perform '{actionName}'."

    if actionName == 'complete':
        consultation = getattr(appointment, 'consultationrecord', None)
        if consultation is None:
            return False, "Cannot mark as completed: consultation record is missing."

    appointment.status = nextStatus
    updateFields = ['status', 'updated_at']

    if actionName == 'confirm':
        appointment.confirmed_at = timezone.now()
        updateFields.append('confirmed_at')
    if actionName == 'check_in':
        appointment.checked_in_at = timezone.now()
        updateFields.append('checked_in_at')
    if actionName == 'complete':
        appointment.completed_at = timezone.now()
        updateFields.append('completed_at')

    if actionName in ('cancel', 'no_show'):
        appointment.slot_id.is_available = True
        appointment.slot_id.save(update_fields=['is_available'])

    appointment.save(update_fields=updateFields)
    return True, None


class AppointmentViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        qs = (
            Appointment.objects
            .select_related("doctor_id", "patient_id", "slot_id")
            .order_by("-id")
        )
        if user.isPatient:
            qs = qs.filter(patient_id__user=user)
        elif user.isDoctor:
            qs = qs.filter(doctor_id__user=user)
        elif not (user.isReceptionist or user.isAdmin):
            return qs.none()

        status_param = self.request.query_params.get("status")
        if status_param:
            statuses = [
                item.strip().upper()
                for item in status_param.split(",")
                if item.strip()
            ]
            if statuses:
                qs = qs.filter(status__in=statuses)

        date_param = self.request.query_params.get("date")
        if date_param:
            selected_date = parse_date(date_param)
            if selected_date:
                qs = qs.filter(slot_id__start_datetime__date=selected_date)

        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return AppointmentWriteSerializer
        if self.action == 'queue':
            return QueueSerializer
        if self.action == 'history':
            return RescheduleHistorySerializer
        if self.action == 'reschedule':
            return RescheduleSerializer
        return AppointmentReadSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsPatient()]
        if self.action in ('confirm', 'no_show'):
            return [IsDoctorOrReceptionist()]
        if self.action == 'check_in':
            return [IsReceptionist()]
        if self.action == 'complete':
            return [IsDoctor()]
        if self.action == 'queue':
            return [IsDoctorOrReceptionist()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            appointment = serializer.save()
        return Response(
            AppointmentReadSerializer(appointment, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    def _transition_action(self, request, pk, actionName):
        appointment = self.get_object()
        ok, error = _apply_transition(appointment, actionName, request.user)
        if not ok:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
        return Response(AppointmentReadSerializer(appointment, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        return self._transition_action(request, pk, 'confirm')

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        return self._transition_action(request, pk, 'cancel')

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        return self._transition_action(request, pk, 'check_in')

    @action(detail=True, methods=['post'])
    def no_show(self, request, pk=None):
        return self._transition_action(request, pk, 'no_show')

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        return self._transition_action(request, pk, 'complete')

    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        appointment = self.get_object()

        if appointment.status not in ('REQUESTED', 'CONFIRMED'):
            return Response(
                {'detail': f"Cannot reschedule an appointment with status '{appointment.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RescheduleSerializer(
            data=request.data,
            context={'request': request, 'appointment': appointment},
        )
        serializer.is_valid(raise_exception=True)

        newSlot = get_object_or_404(TimeSlot, pk=serializer.validated_data['new_slot'])
        reason = serializer.validated_data.get('reason', '')
        oldSlot = appointment.slot_id

        with transaction.atomic():
            RescheduleHistory.objects.create(
                appointment_id=appointment,
                old_slot_id=oldSlot,
                new_slot_id=newSlot,
                changed_by=request.user,
                reason=reason,
            )
            oldSlot.is_available = True
            oldSlot.save(update_fields=['is_available'])
            newSlot.is_available = False
            newSlot.save(update_fields=['is_available'])

            appointment.slot_id = newSlot
            appointment.save(update_fields=['slot_id', 'updated_at'])

        return Response(AppointmentReadSerializer(appointment, context={'request': request}).data)

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        appointment = self.get_object()
        qs = appointment.reschedulehistory_set.select_related('old_slot_id', 'new_slot_id', 'changed_by')
        serializer = RescheduleHistorySerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def queue(self, request):
        today = timezone.localdate()
        user = request.user
        qs = (
            Appointment.objects
            .filter(status='CHECKED_IN', slot_id__start_datetime__date=today)
            .select_related('patient_id', 'slot_id')
            .order_by('checked_in_at')
        )
        if user.isDoctor:
            qs = qs.filter(doctor_id__user=user)
        serializer = QueueSerializer(qs, many=True)
        return Response(serializer.data)


class WaitingListViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if user.isPatient:
            return WaitingList.objects.filter(patient_id__user=user).select_related('doctor_id').order_by('created_at')
        if user.isDoctor:
            return WaitingList.objects.filter(doctor_id__user=user).select_related('patient_id').order_by('created_at')
        if user.isReceptionist or user.isAdmin:
            return WaitingList.objects.select_related('patient_id', 'doctor_id').order_by('created_at')
        return WaitingList.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return WaitingListWriteSerializer
        return WaitingListReadSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsPatient()]
        return [IsAuthenticated()]

    def destroy(self, request):
        instance = self.get_object()
        user = request.user
        is_owner = user.isPatient and instance.patient_id.user == user
        is_doctor = user.isDoctor and instance.doctor_id.user == user
        is_staff = user.isReceptionist or user.isAdmin
        if not (is_owner or is_doctor or is_staff):
            return Response({'detail': 'You do not have permission to delete this entry.'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
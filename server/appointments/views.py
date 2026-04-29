from django.shortcuts import render
from django.http import HttpResponse

from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Appointment, RescheduleHistory, WaitingList

from .permissions import (
    IsPatient, IsDoctor, IsReceptionist, IsDoctorOrReceptionist,
)
from .serializers import (
    AppointmentReadSerializer,
    AppointmentWriteSerializer,
    # RescheduleSerializer,
    RescheduleHistorySerializer,
    # QueueSerializer,
    WaitingListReadSerializer,
    WaitingListWriteSerializer,
    
)


# logic : current_state -> action -> (next_status, allowed_roles)
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
    "CHECKED_IN":{
        'complete': ("COMPLETED",  ['doctor']),
    },
}

def _user_role(user):
    """Return the role string used in TRANSITIONS for this user."""
    if user.isDoctor:
        return 'doctor'
    if user.isReceptionist:
        return 'receptionist'
    if user.isPatient:
        return 'patient'
    return None

def _apply_transition(appointment, action_name, user):
    """
    Validate and apply a status transition.
    Returns (success: bool, error_message: str | None).
    """
    current = appointment.status
    available = TRANSITIONS.get(current, {})
    
    if action_name not in available:
        return False, (
            f"Cannot perform '{action_name}' on an appointment "
            f"with status '{current}'."
        )
    
    next_status, allowed_roles = available[action_name]
    role = _user_role(user)
    
    if role not in allowed_roles:
        return False, (f"Your role ('{role}') is not allowed to perform '{action_name}'.")
    
    # Extra guard: COMPLETED requires a consultation record
    
    if action_name == 'COMPELETE':
        consultation = getattr(appointment, 'consultion', None)
        if consultation is None or not getattr(consultation, 'is_completed', False):
            return False, ("Cannot mark as completed: consultation record is missing or incomplete.")
        
    appointment.status = next_status
    #stamp checked_in_at when receptionst checks patient in
    if action_name == 'check_in':
        appointment.checked_in_at = timezone.now()
        
    appointment.save(update_fields=['status', 'checked_in_at', 'updated_at'])
    return True, None

#-------------------------

#Appointment viewset :

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
            return qs.filter(patient=user)
        if user.isDoctor:
            return qs.filter(doctor=user)
        if user.isReceptionist or user.isAdmin:
            return qs
        return qs.none()
    
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
        # cancel, reschedule, history, list, retrieve
        return [IsAuthenticated()]
    
    #1
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            appointment = serializer.save()
        return Response(
            AppointmentReadSerializer(appointment, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )
        
    #2
    def _transition_action(self, request, pk, action_name):
        appointment = self.get_object()
        ok, error = _apply_transition(appointment, action_name, request.user)
        if not ok:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            AppointmentReadSerializer(appointment, context={'request': request}).data
        )
        
    #TRANSITIONS actions
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
    
    #RESchEDULE
    def reschedule(self, request, pk=None):
        appointment = self.get_object()
 
        if appointment.status not in (
            Appointment.Status.REQUESTED,
            Appointment.Status.CONFIRMED,
        ):
            return Response(
                {'detail': f"Cannot reschedule an appointment with status '{appointment.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
 
        serializer = RescheduleSerializer(
            data=request.data,
            context={'request': request, 'appointment': appointment},
        )
        serializer.is_valid(raise_exception=True)
 
        new_slot = serializer.validated_data['new_slot']
        reason   = serializer.validated_data.get('reason', '')
 
        with transaction.atomic():
            RescheduleHistory.objects.create(
                appointment=appointment,
                old_slot=appointment.slot,
                new_slot=new_slot,
                rescheduled_by=request.user,
                reason=reason,
            )
            appointment.slot = new_slot
            appointment.save(update_fields=['slot', 'updated_at'])
 
        return Response(
            AppointmentReadSerializer(appointment, context={'request': request}).data
        )
        
    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        appointment = self.get_object()
        qs = appointment.reschedulehistory_set.select_related(
            'old_slot_id', 'new_slot_id', 'changed_by'
        )
        serializer = RescheduleHistorySerializer(qs, many=True)
        return Response(serializer.data)
    
    #queue (doctor/ receptionist dashboard)--
    @action(detail=False, methods=['get'])
    def queue(self, request):
        today = timezone.localdate()
        user  = request.user
 
        qs = (
            Appointment.objects
            .filter(
                status=Appointment.Status.CHECKED_IN,
                slot__start_time__date=today,
            )
            .select_related('patient', 'slot')
            .order_by('checked_in_at')
        )
        # Doctors only see their own queue
        if user.isDoctor:
            qs = qs.filter(doctor=user)
 
        serializer = QueueSerializer(qs, many=True)
        return Response(serializer.data)
    
#-------------------------
#waiting list viewset

class WaitingListViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    
    def get_queryset(self):
        user = self.request.user
        if user.isPatient:
            return (
                WaitingList.objects
                .filter(patient=user)
                .select_related('doctor')
                .order_by('joined_at')
            )
        if user.isDoctor:
            return (
                WaitingList.objects
                .filter(doctor=user)
                .select_related('patient')
                .order_by('joined_at')
            )
        if user.isReceptionist or user.isAdmin:
            return WaitingList.objects.select_related('patient', 'doctor').order_by('joined_at')
        return WaitingList.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return WaitingListWriteSerializer
        return WaitingListReadSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsPatient()]
        if self.action == 'destroy':
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    

    
# Create your views here.
'''def index(request):
    return HttpResponse("Skeleton")'''
    


import datetime
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from accounts.views import IsAdmin, IsDoctor, IsReceptionist
from scheduling.models import WeeklySchedule, ScheduleException, TimeSlot
from scheduling.serializers import WeeklyScheduleSerializer, ScheduleExceptionSerializer, TimeSlotSerializer
from scheduling.services import generate_slots


class IsAdminOrReceptionist(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.isAdmin or request.user.isReceptionist)
        )


class IsAdminOrReceptionistOrDoctorReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method not in permissions.SAFE_METHODS:
            return request.user.isAdmin or request.user.isReceptionist
        return request.user.isAdmin or request.user.isReceptionist or request.user.isDoctor


@api_view(['POST'])
@permission_classes([IsAdminOrReceptionist])
def generate_slots_view(request):
    doctor_id = request.data.get('doctor')
    start_date_str = request.data.get('start_date')
    end_date_str = request.data.get('end_date')

    if not all([doctor_id, start_date_str, end_date_str]):
        return Response(
            {"error": "doctor, start_date, and end_date are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "Dates must be in YYYY-MM-DD format."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = generate_slots(start_date, end_date, doctor_id)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if "warning" in result:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    return Response(result, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_slots_view(request):
    doctor_id = request.query_params.get('doctor')
    date_str = request.query_params.get('date')

    if not all([doctor_id, date_str]):
        return Response(
            {"error": "doctor and date are required query parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "Date must be in YYYY-MM-DD format."}, status=status.HTTP_400_BAD_REQUEST)

    slots = TimeSlot.getAvailableSlots(doctor_id=doctor_id, date=date)
    serializer = TimeSlotSerializer(slots, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class WeeklyScheduleViewSet(viewsets.ModelViewSet):
    queryset = WeeklySchedule.objects.all()
    serializer_class = WeeklyScheduleSerializer
    permission_classes = [IsAdminOrReceptionistOrDoctorReadOnly]

    def get_queryset(self):
        doctor_id = self.request.query_params.get('doctor')

        if self.request.user.isDoctor and hasattr(self.request.user, 'doctor_profile'):
            return self.queryset.filter(doctor=self.request.user.doctor_profile)

        if doctor_id:
            return self.queryset.filter(doctor_id=doctor_id)

        return self.queryset


class ScheduleExceptionViewSet(viewsets.ModelViewSet):
    queryset = ScheduleException.objects.all()
    serializer_class = ScheduleExceptionSerializer
    permission_classes = [IsAdminOrReceptionistOrDoctorReadOnly]

    def get_queryset(self):
        doctor_id = self.request.query_params.get('doctor')

        if self.request.user.isDoctor and hasattr(self.request.user, 'doctor_profile'):
            return self.queryset.filter(doctor=self.request.user.doctor_profile)

        if doctor_id:
            return self.queryset.filter(doctor_id=doctor_id)

        return self.queryset

    def perform_create(self, serializer):
        exception = serializer.save()

        if exception.type in ['DAY_OFF', 'VACATION']:
            start_of_day = datetime.datetime.combine(exception.exception_date, datetime.time.min)
            if timezone.is_naive(start_of_day):
                start_of_day = timezone.make_aware(start_of_day)
            end_of_day = datetime.datetime.combine(exception.exception_date, datetime.time.max)
            if timezone.is_naive(end_of_day):
                end_of_day = timezone.make_aware(end_of_day)
            TimeSlot.objects.filter(
                doctor=exception.doctor,
                start_datetime__gte=start_of_day,
                end_datetime__lte=end_of_day,
            ).update(is_available=False)

        elif exception.type == 'EXTRA_WORKING':
            duration = datetime.timedelta(minutes=exception.doctor.consultationDuration)
            current = datetime.datetime.combine(exception.exception_date, exception.start_time)
            if timezone.is_naive(current):
                current = timezone.make_aware(current)
            end = datetime.datetime.combine(exception.exception_date, exception.end_time)
            if timezone.is_naive(end):
                end = timezone.make_aware(end)

            slots = []
            while current + duration <= end:
                slots.append(TimeSlot(
                    doctor=exception.doctor,
                    start_datetime=current,
                    end_datetime=current + duration,
                    is_available=True,
                ))
                current += duration

            if slots:
                TimeSlot.objects.bulk_create(slots, ignore_conflicts=True)
import datetime
from django.db import models
from django.utils import timezone

class WeeklySchedule(models.Model):
    doctor = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE)
    day_of_week = models.IntegerField(
        choices=[(i, day) for i, day in enumerate(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        )]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('doctor', 'day_of_week')

class ScheduleException(models.Model):
    doctor = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE)
    exception_date = models.DateField()
    type = models.CharField(
        max_length=20,
        choices=[('DAY_OFF', 'Day Off'), ('VACATION', 'Vacation'), ('EXTRA_WORKING', 'Extra Working')],
    )
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('doctor', 'exception_date')

class TimeSlot(models.Model):
    doctor = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('doctor', 'start_datetime')

    @classmethod
    def getAvailableSlots(cls, doctor_id, date):
        start_of_day = datetime.datetime.combine(date, datetime.time.min)
        if timezone.is_naive(start_of_day):
            start_of_day = timezone.make_aware(start_of_day)

        end_of_day = datetime.datetime.combine(date, datetime.time.max)
        if timezone.is_naive(end_of_day):
            end_of_day = timezone.make_aware(end_of_day)

        return cls.objects.filter(
            doctor=doctor_id,
            start_datetime__gte=start_of_day,
            end_datetime__lte=end_of_day,
            is_available=True,
        )
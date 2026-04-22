
import datetime

from django.db import models
from accounts.models.doctor import DoctorProfile

class WeeklySchedule(models.Model):
    doctor_id = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=[(i, day) for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('doctor_id', 'day_of_week')

    @classmethod
    def generateSlots(cls, startDate, endDate, doctorId):
        slots = []
        current_date = startDate
        doctor = DoctorProfile.objects.get(id=doctorId)
        duration_delta = datetime.timedelta(minutes=doctor.consultationDuration)

        while current_date <= endDate:
            # Check for exceptions (Vacation or Day Off)
            exception = ScheduleException.objects.filter(doctor_id=doctorId, exception_date=current_date).first()
            if exception and exception.type in ['DAY_OFF', 'VACATION']:
                current_date += datetime.timedelta(days=1)
                continue

            # Assuming EXTRA_WORKING doesn't rely solely on WeeklySchedule, 
            # but standard slots generation checks WeeklySchedule:
            day_of_week = current_date.weekday()
            schedule = cls.objects.filter(doctor_id=doctorId, day_of_week=day_of_week, is_active=True).first()
            
            if schedule:
                start_datetime = datetime.datetime.combine(current_date, schedule.start_time)
                end_datetime = datetime.datetime.combine(current_date, schedule.end_time)
                
                while start_datetime < end_datetime:
                    slots.append(TimeSlot(
                        doctor_id_id=doctorId, 
                        start_datetime=start_datetime, 
                        end_datetime=start_datetime + duration_delta
                    ))
                    start_datetime += duration_delta
            
            current_date += datetime.timedelta(days=1)
            
        # Optionally bulk create if needed, or simply return un-saved slot objects.
        # TimeSlot.objects.bulk_create(slots, ignore_conflicts=True)
        return slots

class ScheduleException(models.Model):
    doctor_id = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE)
    exception_date = models.DateField()
    type = models.CharField(max_length=20, choices=[('DAY_OFF', 'Day Off'), ('VACATION', 'Vacation'), ('EXTRA_WORKING', 'Extra Working')])
    note = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('doctor_id', 'exception_date')

class TimeSlot(models.Model):
    doctor_id = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('doctor_id', 'start_datetime')

    @classmethod
    def getAvailableSlots(cls, doctorId, date):
        start_of_day = datetime.datetime.combine(date, datetime.time.min)
        end_of_day = datetime.datetime.combine(date, datetime.time.max)
        return cls.objects.filter(doctor_id=doctorId, start_datetime__gte=start_of_day, end_datetime__lte=end_of_day, is_available=True)


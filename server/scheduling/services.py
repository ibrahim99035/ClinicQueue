import datetime
from django.conf import settings
from django.utils import timezone
from accounts.models.doctor import DoctorProfile
from scheduling.models import ScheduleException, WeeklySchedule, TimeSlot

def generate_slots(start_date, end_date, doctor_id):
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date.")

    doctor = DoctorProfile.objects.get(id=doctor_id)

    today = timezone.now().date()
    if start_date < today:
        return {"warning": "Cannot generate slots for past dates."}

    # FIX: cap range to 90 days to prevent bulk_create abuse
    max_days = 90
    delta_days = (end_date - start_date).days
    if delta_days > max_days:
        raise ValueError(f"Date range cannot exceed {max_days} days.")

    duration = datetime.timedelta(minutes=doctor.consultationDuration)
    buffer_delta = datetime.timedelta(minutes=getattr(settings, 'SLOT_BUFFER_MINUTES', 5))

    finalSlots = []
    skipReasons = []

    for i in range(delta_days + 1):
        currentDate = start_date + datetime.timedelta(days=i)
        workStartTime = None
        workEndTime = None

        exception = ScheduleException.objects.filter(doctor=doctor, exception_date=currentDate).first()
        if exception:
            if exception.type == 'DAY_OFF':
                skipReasons.append(f"Cannot generate slots for {currentDate}: marked as Day Off.")
                continue
            elif exception.type == 'VACATION':
                skipReasons.append(f"Cannot generate slots for {currentDate}: marked as Vacation.")
                continue
            elif exception.type == 'EXTRA_WORKING':
                workStartTime = exception.start_time
                workEndTime = exception.end_time
        else:
            dayInWeek = currentDate.weekday()
            schedule = WeeklySchedule.objects.filter(
                doctor=doctor, day_of_week=dayInWeek, is_active=True
            ).first()
            if schedule:
                workStartTime = schedule.start_time
                workEndTime = schedule.end_time
            else:
                skipReasons.append(f"No active weekly schedule found for {currentDate}.")

        if workStartTime and workEndTime:
            newCurrentDate = datetime.datetime.combine(currentDate, workStartTime) + buffer_delta
            if timezone.is_naive(newCurrentDate):
                newCurrentDate = timezone.make_aware(newCurrentDate)

            endDatetime = datetime.datetime.combine(currentDate, workEndTime) - buffer_delta
            if timezone.is_naive(endDatetime):
                endDatetime = timezone.make_aware(endDatetime)

            while newCurrentDate + duration <= endDatetime:
                slot_end_dt = newCurrentDate + duration
                finalSlots.append(TimeSlot(
                    doctor=doctor,
                    start_datetime=newCurrentDate,
                    end_datetime=slot_end_dt,
                    is_available=True,
                ))
                newCurrentDate = slot_end_dt + buffer_delta

    if finalSlots:
        TimeSlot.objects.bulk_create(finalSlots, ignore_conflicts=True)
        return {"message": "Success", "count": len(finalSlots)}

    if skipReasons:
        return {"warning": skipReasons[0], "count": 0, "reasons": skipReasons}

    return {"warning": "No slots were generated.", "count": 0}
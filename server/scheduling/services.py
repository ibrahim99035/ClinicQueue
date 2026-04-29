import datetime
from django.utils import timezone
from accounts.models.doctor import DoctorProfile
from scheduling.models import ScheduleException, WeeklySchedule, TimeSlot

def generate_slots(start_date, end_date, doctor_id):
    doctor = DoctorProfile.objects.get(id=doctor_id)
    
    today = timezone.now().date()
    if start_date < today:
        return {"warning": "Cannot generate slots for past dates."}
        
    delta_days = (end_date - start_date).days
    
    duration = datetime.timedelta(minutes=doctor.consultationDuration)
    
    finalSlots = []
    skipReasons = []
    
    for i in range(delta_days + 1):
        currentDate = start_date + datetime.timedelta(days=i)
        workStartTime = None
        workEndTime = None
        
        exception = ScheduleException.objects.filter(doctor=doctor, exception_date=currentDate).first()
        if exception:
            if exception.type == 'DAY_OFF':
                skipReasons.append(f"Cannot generate slots for {currentDate} because this date is marked as Day Off.")
                continue

            elif exception.type == 'VACATION':
                skipReasons.append(f"Cannot generate slots for {currentDate} because this date is marked as Vacation.")
                continue

            elif exception.type == 'EXTRA_WORKING':
                workStartTime = exception.start_time
                workEndTime = exception.end_time
        else:
            dayInWeek = currentDate.weekday()
            schedule = WeeklySchedule.objects.filter(doctor=doctor, day_of_week=dayInWeek, is_active=True).first()
            
            if schedule:
                workStartTime = schedule.start_time
                workEndTime = schedule.end_time
            else:
                skipReasons.append(f"No active weekly schedule found for {currentDate}.")
                
        if workStartTime and workEndTime:
            newCurrentDate = datetime.datetime.combine(currentDate, workStartTime)
            
            if timezone.is_naive(newCurrentDate):
                newCurrentDate = timezone.make_aware(newCurrentDate)
                
            endDate = datetime.datetime.combine(currentDate, workEndTime)
            
            if timezone.is_naive(endDate):
                endDate = timezone.make_aware(endDate)
            
            while newCurrentDate + duration <= endDate:
                slot_end_dt = newCurrentDate + duration
                
                finalSlots.append(TimeSlot(
                    doctor=doctor,
                    start_datetime=newCurrentDate,
                    end_datetime=slot_end_dt,
                    is_available=True
                ))
                
                newCurrentDate = slot_end_dt
                
    if finalSlots:
        TimeSlot.objects.bulk_create(finalSlots, ignore_conflicts=True)
        return {"message": "Success", "count": len(finalSlots)}

    if skipReasons:
        return {
            "warning": skipReasons[0],
            "count": 0,
            "reasons": skipReasons
        }

    return {
        "warning": "No slots were generated.",
        "count": 0
    }
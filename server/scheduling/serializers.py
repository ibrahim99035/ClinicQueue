import datetime
from django.utils import timezone
from rest_framework import serializers
from .models import WeeklySchedule, ScheduleException, TimeSlot

class WeeklyScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklySchedule
        fields = '__all__'

    def validate(self, data):
        startTime = data.get('start_time')
        endTime = data.get('end_time')
        doctor = data.get('doctor')

        if startTime and endTime:
            if startTime >= endTime:
                raise serializers.ValidationError({"end_time": "End time must be after start time."})

            if doctor:
                dummyDate = datetime.date(2000, 1, 1)
                startDt = datetime.datetime.combine(dummyDate, startTime)
                endDt = datetime.datetime.combine(dummyDate, endTime)
                durationDelta = datetime.timedelta(minutes=doctor.consultationDuration)

                if (endDt - startDt) < durationDelta:
                    raise serializers.ValidationError({
                        "non_field_errors": f"Time range must be at least {doctor.consultationDuration} minutes long to fit one slot."
                    })

        return data


class ScheduleExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleException
        fields = '__all__'

    def validate(self, data):
        excType = data.get('type')
        startTime = data.get('start_time')
        endTime = data.get('end_time')
        exceptionDate = data.get('exception_date')

        if exceptionDate and exceptionDate < timezone.now().date():
            raise serializers.ValidationError({"exception_date": "Exception date cannot be in the past."})

        if excType == 'EXTRA_WORKING':
            if not startTime or not endTime:
                raise serializers.ValidationError("start_time and end_time are required when type is EXTRA_WORKING.")
            
            if startTime >= endTime:
                raise serializers.ValidationError({"end_time": "End time must be after start time."})
                
        elif excType in ['DAY_OFF', 'VACATION']:
            if startTime is not None or endTime is not None:
                raise serializers.ValidationError("start_time and end_time must be empty for DAY_OFF or VACATION.")

        return data


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'
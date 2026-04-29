from django.utils import timezone
from rest_framework import serializers
from .models import Appointment, RescheduleHistory, WaitingList

##app -> write (booking)
class AppointmentWriteSerializer(serializers.ModelSerializer):
    """
    Used for POST /appointments/ (booking).
    Patient is injected from request — not supplied by the caller.
    Validates the slot is not already taken.
    """
    class Meta:
        model  = Appointment
        fields = ('slot_id', 'doctor_id', 'reason')
    def validate_slot(self, slot):
        if hasattr(slot, 'appointment'):
            raise serializers.ValidationError(
                "This slot is already booked."
            )
        return slot
    def create(self, validated_data):
        validated_data['patient'] = self.context['request'].user
        return super().create(validated_data)
    
    
#app -> read(list/detaiul)

class AppointmentReadSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    slot_time = serializers.DateTimeField(source='slot_id.start_datetime', read_only=True)
    
    class Meta:
        model = Appointment
        fields = (
            'id', 'status',
            'patient_id', 'patient_name',
            'doctor_id',  'doctor_name',
            'slot_id', 'slot_time',
            'reason',
            'checked_in_at',
            'created_at',
        )
        read_only_fields = fields

    def get_patient_name(self, obj):
        user = obj.patient_id.user

        full_name = (user.first_name + " " + user.last_name).strip()

        if full_name:
            return full_name

        return user.email
    
    def get_doctor_name(self, obj):
        user = obj.doctor_id.user

        full_name = (user.first_name + " " + user.last_name).strip()

        if full_name:
            return full_name

        return user.email
    
    def get_waiting_minutes(self, obj):
        if obj.checked_in_at:
            delta = timezone.now() - obj.checked_in_at
            return max(0, int(delta.total_seconds() // 60))
        return None
    
## waiting list
##write
class WaitingListWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = WaitingList
        fields = ('doctor', 'date', 'note')
    
    def validate(self, attrs):
        patient = self.context['request'].user
        if WaitingList.objects.filter(
            patient=patient,
            doctor=attrs['doctor'],
            date=attrs['date'],
        ).exists():
            raise serializers.ValidationError(
                "You are already on the waiting list for this doctor on that date."
            )
        return attrs
    
    def create(self, validated_data):
        validated_data['patient'] = self.context['request'].user
        return super().create(validated_data)
    
##read
class WaitingListReadSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    class Meta:
        model  = WaitingList
        fields = ('id', 'doctor', 'doctor_name', 'date', 'note', 'joined_at')
        read_only_fields = fields
    # def get_doctor_name(self, obj):
    #     user = obj.doctor_id.user

    #     full_name = (user.first_name + " " + user.last_name).strip()

    #     if full_name:
    #         return full_name

    #     return user.email
    
    
class RescheduleHistorySerializer(serializers.ModelSerializer):
        old_slot_start = serializers.DateTimeField(
        source='old_slot_id.start_datetime',
        read_only=True
    )
        new_slot_start = serializers.DateTimeField(
        source='new_slot_id.start_datetime',
        read_only=True
    )
        changed_by_name = serializers.SerializerMethodField()

        class Meta:
            model = RescheduleHistory
            fields = (
                'id',
                'old_slot_id',
                'new_slot_id',
                'old_slot_start',
                'new_slot_start',
                'changed_by',
                'changed_by_name',
            )
            read_only_fields = fields

        def get_changed_by_name(self, obj):
            user = obj.changed_by

            full_name = (user.first_name + " " + user.last_name).strip()

            if full_name:
                return full_name

            return user.email
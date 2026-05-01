from django.utils import timezone
from rest_framework import serializers
from appointments.models import Appointment, RescheduleHistory, WaitingList


class AppointmentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ('slot_id', 'doctor_id', 'reason')

    def validate_slot_id(self, slot):
        if hasattr(slot, 'appointment'):
            raise serializers.ValidationError("This slot is already booked.")
        return slot

    def create(self, validatedData):
        validatedData['patient_id'] = self.context['request'].user.patient_profile
        validatedData['status'] = 'REQUESTED'
        slot = validatedData['slot_id']
        appointment = super().create(validatedData)
        slot.is_available = False
        slot.save(update_fields=['is_available'])
        return appointment


class AppointmentReadSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    slot_time = serializers.DateTimeField(source='slot_id.start_datetime', read_only=True)

    class Meta:
        model = Appointment
        fields = (
            'id', 'status',
            'patient_id', 'patient_name',
            'doctor_id', 'doctor_name',
            'slot_id', 'slot_time',
            'reason',
            'checked_in_at',
            'created_at',
        )
        read_only_fields = fields

    def get_patient_name(self, obj):
        user = obj.patient_id.user
        fullName = (user.first_name + " " + user.last_name).strip()
        return fullName if fullName else user.email

    def get_doctor_name(self, obj):
        user = obj.doctor_id.user
        fullName = (user.first_name + " " + user.last_name).strip()
        return fullName if fullName else user.email

    def get_waiting_minutes(self, obj):
        if obj.checked_in_at:
            delta = timezone.now() - obj.checked_in_at
            return max(0, int(delta.total_seconds() // 60))
        return None


class WaitingListWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitingList
        fields = ('doctor_id', 'preferred_date')

    def validate(self, attrs):
        patient = self.context['request'].user
        if WaitingList.objects.filter(
            patient_id__user=patient,
            doctor_id=attrs['doctor_id'],
            preferred_date=attrs['preferred_date'],
        ).exists():
            raise serializers.ValidationError(
                "You are already on the waiting list for this doctor on that date."
            )
        return attrs

    def create(self, validatedData):
        validatedData['patient_id'] = self.context['request'].user.patient_profile
        return super().create(validatedData)


class WaitingListReadSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = WaitingList
        fields = ('id', 'doctor_id', 'doctor_name', 'preferred_date', 'created_at')
        read_only_fields = fields

    def get_doctor_name(self, obj):
        user = obj.doctor_id.user
        fullName = (user.first_name + " " + user.last_name).strip()
        return fullName if fullName else user.email


class RescheduleHistorySerializer(serializers.ModelSerializer):
    oldSlotStart = serializers.DateTimeField(source='old_slot_id.start_datetime', read_only=True)
    newSlotStart = serializers.DateTimeField(source='new_slot_id.start_datetime', read_only=True)
    changedByName = serializers.SerializerMethodField()

    class Meta:
        model = RescheduleHistory
        fields = (
            'id',
            'old_slot_id',
            'new_slot_id',
            'oldSlotStart',
            'newSlotStart',
            'changed_by',
            'changedByName',
        )
        read_only_fields = fields

    # FIX: was get_changed_by_name — must match field name exactly as get_changedByName
    def get_changedByName(self, obj):
        user = obj.changed_by
        fullName = (user.first_name + " " + user.last_name).strip()
        return fullName if fullName else user.email


class RescheduleSerializer(serializers.Serializer):
    new_slot = serializers.IntegerField()
    reason = serializers.CharField(required=False, allow_blank=True)


class QueueSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ('id', 'patient_id', 'patient_name', 'doctor_id', 'doctor_name', 'checked_in_at')
        read_only_fields = fields

    def get_patient_name(self, obj):
        user = obj.patient_id.user
        fullName = (user.first_name + " " + user.last_name).strip()
        return fullName if fullName else user.email

    def get_doctor_name(self, obj):
        user = obj.doctor_id.user
        fullName = (user.first_name + " " + user.last_name).strip()
        return fullName if fullName else user.email
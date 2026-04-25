from rest_framework import serializers
from django.db import transaction
from .models import ConsultationRecord, PrescriptionItem, RequestedTest


class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = ['id', 'drug_name', 'dose', 'duration']
        read_only_fields = ['id']
      
class RequestedTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestedTest
        fields = ['id', 'test_name', 'notes']
        read_only_fields = ['id']

class ConsultationRecordSerializer(serializers.ModelSerializer):
    prescription_items = PrescriptionItemSerializer(many=True, required=False)
    requested_tests = RequestedTestSerializer(many=True, required=False)

    class Meta:
        model = ConsultationRecord
        fields = [
            'id',
            'appointment_id',
            'created_by',
            'diagnosis',
            'notes',
            'created_at',
            'updated_at',
            'prescription_items',
            'requested_tests',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'created_at',
            'updated_at',
        ]
       
    def validate(self, data):
        appointment = data.get("appointment_id")
        diagnosis = data.get("diagnosis")
        
        if self.instance is None:
            if not appointment:
                raise serializers.ValidationError({
                    "appointment_id": "Appointment is required."
                })

            if appointment.status != "CHECKED_IN":
                raise serializers.ValidationError({
                    "appointment_id": "Consultation can only be created for a CHECKED_IN appointment."
                })

            if ConsultationRecord.objects.filter(appointment_id=appointment).exists():
                raise serializers.ValidationError({ 
                    "appointment_id":"A consultation record already exists for this appointment."
                })

            if not diagnosis or diagnosis.strip() == "":
                raise serializers.ValidationError({
                    "diagnosis": "Diagnosis cannot be empty."
                })

        return data

    def _create_prescription_items(self, consultation, prescription_items_data):
        for item_data in prescription_items_data:
            PrescriptionItem.objects.create(
                consultation_id=consultation,
                drug_name=item_data["drug_name"],
                dose=item_data["dose"],
                duration=item_data["duration"],
            )

    def _create_requested_tests(self, consultation, requested_tests_data):
        for test_data in requested_tests_data:
            RequestedTest.objects.create(
                consultation_id=consultation,
                test_name=test_data["test_name"],
                notes=test_data.get("notes"),
            )



    @transaction.atomic
    def create(self, validated_data):
        prescription_items_data = validated_data.pop('prescription_items', [])
        requested_tests_data = validated_data.pop('requested_tests', [])

        consultation = ConsultationRecord.objects.create(
        appointment_id=validated_data["appointment_id"],
        created_by=validated_data["created_by"],
        diagnosis=validated_data["diagnosis"],
        notes=validated_data["notes"],
    )

        self._create_prescription_items(consultation, prescription_items_data)
        self._create_requested_tests(consultation, requested_tests_data)

        return consultation
    @transaction.atomic
    def update(self, instance, validated_data):
        prescription_items_data = validated_data.pop("prescription_items", None)
        requested_tests_data = validated_data.pop("requested_tests", None)
        
        instance.diagnosis = validated_data.get('diagnosis', instance.diagnosis)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save()
        
        if prescription_items_data is not None:
            instance.prescription_items.all().delete()
            self._create_prescription_items(instance, prescription_items_data)

        if requested_tests_data is not None:
            instance.requested_tests.all().delete()
            self._create_requested_tests(instance, requested_tests_data)

        return instance
    
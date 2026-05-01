from rest_framework import serializers
from django.db import transaction
from emr.models import ConsultationRecord, PrescriptionItem, RequestedTest

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
            'id', 'appointment_id', 'created_by',
            'diagnosis', 'notes',
            'created_at', 'updated_at',
            'prescription_items', 'requested_tests',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate(self, data):
        diagnosis = data.get("diagnosis")

        if self.instance is not None:
            if "appointment_id" in data:
                raise serializers.ValidationError({
                    "appointment_id": "Appointment cannot be changed after consultation creation."
                })

        if "diagnosis" in data:
            if not diagnosis or diagnosis.strip() == "":
                raise serializers.ValidationError({"diagnosis": "Diagnosis cannot be empty."})

        if self.instance is None:
            appointmentRecord = data.get("appointment_id")
            if not appointmentRecord:
                raise serializers.ValidationError({"appointment_id": "Appointment is required."})
            if appointmentRecord.status != "CHECKED_IN":
                raise serializers.ValidationError({
                    "appointment_id": "Consultation can only be created for a CHECKED_IN appointment."
                })
            if ConsultationRecord.objects.filter(appointment_id=appointmentRecord).exists():
                raise serializers.ValidationError({
                    "appointment_id": "A consultation record already exists for this appointment."
                })
            if not diagnosis or diagnosis.strip() == "":
                raise serializers.ValidationError({"diagnosis": "Diagnosis cannot be empty."})

        return data

    def _upsert_prescription_items(self, instance, items_data):
        existing_ids = {item.id for item in instance.prescription_items.all()}
        submitted_ids = {item['id'] for item in items_data if 'id' in item}

        instance.prescription_items.filter(
            id__in=existing_ids - submitted_ids
        ).delete()

        for item_data in items_data:
            item_id = item_data.get('id')
            if item_id and item_id in existing_ids:
                PrescriptionItem.objects.filter(id=item_id).update(
                    drug_name=item_data['drug_name'],
                    dose=item_data['dose'],
                    duration=item_data['duration'],
                )
            else:
                PrescriptionItem.objects.create(consultation_id=instance, **item_data)

    def _upsert_requested_tests(self, instance, tests_data):
        existing_ids = {test.id for test in instance.requested_tests.all()}
        submitted_ids = {test['id'] for test in tests_data if 'id' in test}

        instance.requested_tests.filter(
            id__in=existing_ids - submitted_ids
        ).delete()

        for test_data in tests_data:
            test_id = test_data.get('id')
            if test_id and test_id in existing_ids:
                RequestedTest.objects.filter(id=test_id).update(
                    test_name=test_data['test_name'],
                    notes=test_data.get('notes'),
                )
            else:
                RequestedTest.objects.create(consultation_id=instance, **test_data)

    @transaction.atomic
    def create(self, validatedData):
        prescription_items_data = validatedData.pop('prescription_items', [])
        requested_tests_data = validatedData.pop('requested_tests', [])

        record = ConsultationRecord.objects.create(**validatedData)

        for item in prescription_items_data:
            PrescriptionItem.objects.create(consultation_id=record, **item)
        for test in requested_tests_data:
            RequestedTest.objects.create(consultation_id=record, **test)

        return record

    @transaction.atomic
    def update(self, instance, validatedData):
        prescription_items_data = validatedData.pop("prescription_items", None)
        requested_tests_data = validatedData.pop("requested_tests", None)

        instance.diagnosis = validatedData.get('diagnosis', instance.diagnosis)
        instance.notes = validatedData.get('notes', instance.notes)
        instance.save()

        if prescription_items_data is not None:
            self._upsert_prescription_items(instance, prescription_items_data)

        if requested_tests_data is not None:
            self._upsert_requested_tests(instance, requested_tests_data)

        return instance
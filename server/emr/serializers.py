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
        
        read_only_fields = ['id', 'created_by',  'created_at', 'updated_at',]
       
    def validate(self, data):
        appointmentRecord = data.get("appointment_id")
        diagnosis = data.get("diagnosis")
        
        if self.instance is None:
            if not appointmentRecord:
                raise serializers.ValidationError({"appointment_id": "Appointment is required."})

            if appointmentRecord.status != "CHECKED_IN":
                raise serializers.ValidationError({"appointment_id": "Consultation can only be created for a CHECKED_IN appointment."})

            if ConsultationRecord.objects.filter(appointment_id=appointmentRecord).exists():
                raise serializers.ValidationError({ "appointment_id":"A consultation record already exists for this appointment."})

            if not diagnosis or diagnosis.strip() == "":
                raise serializers.ValidationError({"diagnosis": "Diagnosis cannot be empty."})

        return data

    def createPrescriptionItems(self, consultationRecord, prescriptionItemsData):
        for itemData in prescriptionItemsData:
            PrescriptionItem.objects.create(
                consultation_id=consultationRecord,
                drug_name=itemData["drug_name"],
                dose=itemData["dose"],
                duration=itemData["duration"],
            )

    def createRequestedTests(self, consultationRecord, requestedTestsData):
        for testData in requestedTestsData:
            RequestedTest.objects.create(
                consultation_id=consultationRecord,
                test_name=testData["test_name"],
                notes=testData.get("notes"),
            )



    @transaction.atomic
    def create(self, validatedData):
        prescriptionItemsData = validatedData.pop('prescription_items', [])
        requestedTestsData = validatedData.pop('requested_tests', [])

        consultationRecord = ConsultationRecord.objects.create(
            appointment_id=validatedData["appointment_id"],
            created_by=validatedData["created_by"],
            diagnosis=validatedData["diagnosis"],
            notes=validatedData["notes"],
        )

        self.createPrescriptionItems(consultationRecord, prescriptionItemsData)
        self.createRequestedTests(consultationRecord, requestedTestsData)

        return consultationRecord
    @transaction.atomic
    def update(self, instance, validatedData):
        prescriptionItemsData = validatedData.pop("prescription_items", None)
        requestedTestsData = validatedData.pop("requested_tests", None)
        
        instance.diagnosis = validatedData.get('diagnosis', instance.diagnosis)
        instance.notes = validatedData.get('notes', instance.notes)
        instance.save()
        
        if prescriptionItemsData is not None:
            instance.prescription_items.all().delete()
            self.createPrescriptionItems(instance, prescriptionItemsData)

        if requestedTestsData is not None:
            instance.requested_tests.all().delete()
            self.createRequestedTests(instance, requestedTestsData)

        return instance
    
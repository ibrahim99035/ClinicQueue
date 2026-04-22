from django.db import models
from django.conf import settings

class ConsultationRecord(models.Model):
    appointment_id = models.OneToOneField('appointments.Appointment', on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    diagnosis = models.CharField(max_length=255)
    notes = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PrescriptionItem(models.Model):
    consultation_id = models.ForeignKey(ConsultationRecord, on_delete=models.CASCADE)
    
    drug_name = models.CharField(max_length=255)
    dose = models.CharField(max_length=255)
    duration = models.CharField(max_length=255)

class RequestedTest(models.Model):
    consultation_id = models.ForeignKey(ConsultationRecord, on_delete=models.CASCADE)
    
    test_name = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)
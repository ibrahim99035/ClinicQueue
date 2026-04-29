from django.db import models
from django.conf import settings

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'),
        ('CONFIRMED', 'Confirmed'),
        ('CHECKED_IN', 'Checked In'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]

    TYPE_CHOICES = [
        ('IN_PERSON', 'In Person'),
        ('ONLINE', 'Online'),
    ]

    patient_id = models.ForeignKey('accounts.PatientProfile', on_delete=models.CASCADE)
    doctor_id = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE)
    slot_id = models.OneToOneField('scheduling.TimeSlot', on_delete=models.CASCADE, unique=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='IN_PERSON')
    
    reason = models.TextField(null=True, blank=True)
    
    meeting_link = models.URLField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class RescheduleHistory(models.Model):
    appointment_id = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    
    old_slot_id = models.ForeignKey('scheduling.TimeSlot', related_name='old_slot', on_delete=models.CASCADE)
    new_slot_id = models.ForeignKey('scheduling.TimeSlot', related_name='new_slot', on_delete=models.CASCADE)
    
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    reason = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)

class WaitingList(models.Model):
    patient_id = models.ForeignKey('accounts.PatientProfile', on_delete=models.CASCADE)
    doctor_id = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE)
    
    preferred_date = models.DateField()
    hold_expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('REFUNDED', 'Refunded'),
    ]

    appointment_id = models.OneToOneField(Appointment, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=8, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    
    paid_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
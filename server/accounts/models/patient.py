from django.db import models
from accounts.models.user import User

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    dateOfBirth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')], blank=True, default='')
    
    def __str__(self):
        return f"Patient Profile for {self.user.first_name} {self.user.last_name}"
    
    @classmethod
    def getAllPatients(cls):
        return cls.objects.all()
    
    @classmethod
    def createPatient(cls, user, dateOfBirth=None, gender=''):
        profile = cls(user=user, dateOfBirth=dateOfBirth, gender=gender)
        profile.save()

        return profile

    @classmethod
    def getPatient(cls, user):
        return cls.objects.get(user=user)

    @classmethod
    def updatePatient(cls, user, **updated_fields):
        profile = cls.objects.get(user=user)

        for field, value in updated_fields.items():
            setattr(profile, field, value)
        profile.save()

        return profile

    @classmethod
    def deletePatient(cls, user):
        profile = cls.objects.get(user=user)
        profile.delete()

        return f"Patient profile for {user.email} has been deleted."

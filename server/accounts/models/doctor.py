from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models.user import User

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100, blank=True)
    consultationDuration = models.PositiveIntegerField(default=15, validators=[MinValueValidator(15), MaxValueValidator(120)]) 

    def __str__(self):
        return f"Doctor Profile for {self.user.first_name} {self.user.last_name}"
    
    @classmethod
    def getAllDoctors(cls):
        return cls.objects.all()
    
    @classmethod
    def createDoctor(cls, user, specialization=None, consultationDuration=15):
        profile = cls(user=user, specialization=specialization, consultationDuration=consultationDuration)
        profile.save()

        return profile

    @classmethod
    def getDoctor(cls, user):
        return cls.objects.get(user=user)

    @classmethod
    def updateDoctor(cls, user, **updated_fields):
        profile = cls.objects.get(user=user)

        for field, value in updated_fields.items():
            setattr(profile, field, value)
        profile.save()

        return profile

    @classmethod
    def deleteDoctor(cls, user):
        profile = cls.objects.get(user=user)
        profile.delete()

        return f"Doctor profile for {user.email} has been deleted."


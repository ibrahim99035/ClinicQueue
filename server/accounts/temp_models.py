from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    @property
    def isPatient(self):
        return self.groups.filter(name='Patients').exists()

    @property
    def isDoctor(self):
        return self.groups.filter(name='Doctors').exists()

    @property
    def isReceptionist(self):
        return self.groups.filter(name='Receptionists').exists()

    @property
    def isAdmin(self):
        return self.groups.filter(name='Admins').exists()

    @property
    def isStaff(self):
        return self.isDoctor or self.isReceptionist or self.isAdmin 

    @classmethod
    def create_user(cls, email, password=None, **extra_fields):
        user = cls(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user
    
    @classmethod
    def getAllUsers(cls):
        return cls.objects.all()
    
    @classmethod
    def getUser(cls, email):
        return cls.objects.get(email=email)
    
    @classmethod
    def updateUser(cls, email, **updated_fields):
        user = cls.objects.get(email=email)
        
        for field, value in updated_fields.items():
            setattr(user, field, value)
        user.save()
        
        return user
    
    @classmethod
    def getFullname(cls, email):
        user = cls.objects.get(email=email)

        return f"{user.first_name} {user.last_name}"

    @classmethod
    def deleteUser(cls, email):
        user = cls.objects.get(email=email)
        user.delete()

        return f"User with email {email} has been deleted."


class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    dateOfBirth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')], required=True, blank=True)
    
    def __str__(self):
        return f"Patient Profile for {self.user.first_name} {self.user.last_name}"
    
    @classmethod
    def getAllPatients(cls):
        return cls.objects.all()
    
    @classmethod
    def createPatient(cls, user, dateOfBirth=None, gender=None):
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

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100, blank=True)
    consultationDuration = models.PositiveIntegerField(default=15, min_value=15, max_value=120)  # Duration in minutes, default is 30 minutes

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

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[('confirmation', 'Confirmation'), ('cancellation', 'Cancellation')], default='confirmation')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email} - {'Read' if self.is_read else 'Unread'}"
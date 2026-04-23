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
        if 'username' not in extra_fields:
            extra_fields['username'] = email
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


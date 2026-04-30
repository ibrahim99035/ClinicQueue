from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models.user import User
from accounts.models.patient import PatientProfile
from accounts.models.doctor import DoctorProfile
from accounts.models.notification import Notification

admin.site.register(User)        
admin.site.register(PatientProfile)
admin.site.register(DoctorProfile)
admin.site.register(Notification)
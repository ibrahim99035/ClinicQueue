from django.contrib import admin
from accounts.models.user import User
from accounts.models.patient import PatientProfile
from accounts.models.doctor import DoctorProfile
from accounts.models.notification import Notification
# Register your models here.

admin.site.register(User)
admin.site.register(PatientProfile)
admin.site.register(DoctorProfile)
admin.site.register(Notification)

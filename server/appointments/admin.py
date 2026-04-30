from django.contrib import admin
from appointments.models import Appointment, RescheduleHistory, WaitingList, Payment

admin.site.register(Appointment) 
admin.site.register(RescheduleHistory)
admin.site.register(WaitingList)
admin.site.register(Payment)
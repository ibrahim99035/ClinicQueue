from django.contrib import admin
from scheduling.models import WeeklySchedule, ScheduleException, TimeSlot

admin.site.register(WeeklySchedule)
admin.site.register(ScheduleException)
admin.site.register(TimeSlot)
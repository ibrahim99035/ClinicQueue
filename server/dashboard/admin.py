from django_api_admin.sites import site
from django_api_admin.options import ModelAdmin
from accounts.views import IsAdmin

class AdminOnlyMixin(ModelAdmin):
    permission_classes = [IsAdmin]

from accounts.models.user import User
from accounts.models.patient import PatientProfile
from accounts.models.doctor import DoctorProfile
from accounts.models.notification import Notification

from appointments.models import Appointment, RescheduleHistory, WaitingList, Payment
from scheduling.models import WeeklySchedule, ScheduleException, TimeSlot
from emr.models import ConsultationRecord, PrescriptionItem, RequestedTest

site.register(User, AdminOnlyMixin)
site.register(PatientProfile, AdminOnlyMixin)
site.register(DoctorProfile, AdminOnlyMixin)
site.register(Notification, AdminOnlyMixin)
site.register(Appointment, AdminOnlyMixin)
site.register(RescheduleHistory, AdminOnlyMixin)
site.register(WaitingList, AdminOnlyMixin)
site.register(Payment, AdminOnlyMixin)
site.register(WeeklySchedule, AdminOnlyMixin)
site.register(ScheduleException, AdminOnlyMixin)
site.register(TimeSlot, AdminOnlyMixin)
site.register(ConsultationRecord, AdminOnlyMixin)
site.register(PrescriptionItem, AdminOnlyMixin)
site.register(RequestedTest, AdminOnlyMixin)
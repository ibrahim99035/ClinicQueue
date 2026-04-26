from django.urls import path , include
from appointments.views import index
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, WaitingListViewSet

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'waiting-list', WaitingListViewSet, basename='waitinglist')


urlpatterns = [
    path('', include(router.urls)),
]


#  GET    /appointments/                        → list
#  POST   /appointments/                        → create (book)  [IsPatient]
#  GET    /appointments/{id}/                   → retrieve
#  POST   /appointments/{id}/confirm/           → confirm        [IsDoctorOrReceptionist]
#  POST   /appointments/{id}/cancel/            → cancel         [IsAuthenticated]
#  POST   /appointments/{id}/check_in/          → check_in       [IsReceptionist]
#  POST   /appointments/{id}/no_show/           → no_show        [IsDoctorOrReceptionist]
#  POST   /appointments/{id}/complete/          → complete       [IsDoctor]
#  POST   /appointments/{id}/reschedule/        → reschedule     [IsAuthenticated]
#  GET    /appointments/{id}/history/           → reschedule log [IsAuthenticated]
#  GET    /appointments/queue/                  → today queue    [IsDoctorOrReceptionist]
#
#  GET    /waiting-list/                        → list entries
#  POST   /waiting-list/                        → join           [IsPatient]
#  DELETE /waiting-list/{id}/                   → leave
 
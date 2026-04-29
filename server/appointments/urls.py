from django.urls import path , include
# from appointments.views import index
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, WaitingListViewSet

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'waiting-list', WaitingListViewSet, basename='waitinglist')


urlpatterns = [
    path('', include(router.urls)),
]
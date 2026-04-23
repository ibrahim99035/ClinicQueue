from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    generate_slots_view,
    available_slots_view,
    WeeklyScheduleViewSet,
    ScheduleExceptionViewSet
)

router = DefaultRouter()
router.register(r'weekly-schedule', WeeklyScheduleViewSet, basename='weekly-schedule')
router.register(r'exceptions', ScheduleExceptionViewSet, basename='exceptions')

urlpatterns = [
    path('generate-slots/', generate_slots_view, name='generate-slots'),
    path('slots/', available_slots_view, name='available-slots'),
    path('', include(router.urls)),
]

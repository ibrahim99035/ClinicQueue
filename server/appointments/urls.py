from django.urls import path
from appointments.views import index

urlpatterns = [
    path('', index, name='index'),
]

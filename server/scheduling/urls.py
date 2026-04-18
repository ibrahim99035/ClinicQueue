from django.urls import path
from scheduling.views import index

urlpatterns = [
    path('', index, name='index'),
]

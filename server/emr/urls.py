from django.urls import path
from emr.views import index

urlpatterns = [
    path('', index, name='index'),
]

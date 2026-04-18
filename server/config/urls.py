from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("analytics/", include("analytics.urls")),
    path("appointments/", include("appointments.urls")),
    path("emr/", include("emr.urls")),
    path("scheduling/", include("scheduling.urls")),
    path("api/", include("rest_framework.urls"))
]

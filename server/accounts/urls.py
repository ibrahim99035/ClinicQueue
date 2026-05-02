from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import UserRegistrationView, UserLoginView, UserProfileView, UserListView, PatientProfileView, DoctorProfileView, DoctorsListView, AdminUserCreateView, PendingDoctorsListView, ApproveDoctorView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    
    path('users/', UserListView.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path('users/<int:pk>/', UserListView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='user-detail'),
    
    path('patient-profile/', PatientProfileView.as_view(), name='patient-profile'),
    path('doctor-profile/', DoctorProfileView.as_view(), name='doctor-profile'),
    path('doctors/', DoctorsListView.as_view(), name='doctors-list'),
    
    path('admin/create-staff/', AdminUserCreateView.as_view(), name='create-staff'),
    path('admin/create-internal-user/', AdminUserCreateView.as_view(), name='create-internal-user'),
    path('admin/pending-doctors/', PendingDoctorsListView.as_view(), name='pending-doctors'),
    path('admin/approve-doctor/<int:pk>/', ApproveDoctorView.as_view(), name='approve-doctor'),
]

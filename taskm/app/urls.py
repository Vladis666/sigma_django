from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Default route for the homepage
    path('stat/', views.statistic, name='statistic'),  # Statistics page route
    path('tasks/', views.tasks, name='tasks'),  # Task page route

    # Authentication endpoints
    path('api/register/', views.RegisterView.as_view(), name='register_api'),
    path('api/login/', views.LoginView.as_view(), name='login_api'),
    path('api/logout/', views.LogoutView.as_view(), name='logout_api'),
    path('api/user_status/', views.UserStatusView.as_view(), name='user_status'),
]

# taskm/urls.py
from django.contrib import admin
from django.urls import path, include
from app import views
from app.views import page_not_found

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel route
    path("", include('app.urls')),  # This includes the app's URLs
    path('stat/', views.statistic, name='statistic'),  # Direct route to statistic view
    path('tasks/', views.tasks, name='tasks'),  # Direct route to tasks view
]

# Custom 404 page handler
handler404 = page_not_found

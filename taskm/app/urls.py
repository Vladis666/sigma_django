from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Default route for the homepage
    path('stat/', views.statistic, name='statistic'),  # Statistics page route
    path('tasks/', views.tasks, name='tasks'),  # Task page route
]

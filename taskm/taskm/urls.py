# taskm/urls.py
from django.contrib import admin
from django.urls import path, include
from app import views
from app.views import page_not_found

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel route
    path("", include('app.urls')),  # This includes the app's URLs
    path('employees/', views.employee_list, name='employee_list'),
    path('products/', views.product_list, name='product_list'),
    path('sales/', views.sales_list, name='sales_list'),
    path('add_sale/', views.add_sale, name='add_sale'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('daily_stats/', views.daily_stats, name='daily_stats'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]

# Custom 404 page handler
handler404 = page_not_found

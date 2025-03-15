from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views
from .views import ProductDetailView, ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView, \
    SalesStatisticsView, ProductPerformanceView, EmployeePerformanceView, LeaderboardView, SalesSummaryView

urlpatterns = [
    path('', views.index, name='index'),  # Default route for the homepage
    path('stat/', views.statistic, name='statistic'),  # Statistics page route
    path('tasks/', views.tasks, name='tasks'),  # Task page route

    # Authentication endpoints
    path('api/register/', views.RegisterView.as_view(), name='register_api'),
    path('api/login/', views.LoginView.as_view(), name='login_api'),
    path('api/logout/', views.LogoutView.as_view(), name='logout_api'),
    path('api/user_status/', views.UserStatusView.as_view(), name='user_status'),

# Product endpoints
    path('api/products/', ProductListView.as_view(), name='product_list'),
    path('api/products/create/', ProductCreateView.as_view(), name='product_create'),
    path('api/products/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('api/products/<int:product_id>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('api/products/<int:product_id>/delete/', ProductDeleteView.as_view(), name='product_delete'),

    # SalesStatistics
    path('api/sales/statistics/<str:period>/', SalesStatisticsView.as_view(), name='sales-statistics'),
    path('api/sales/statistics/', SalesStatisticsView.as_view(), name='sales-statistics-default'),

    # ProductPerformance
    path('api/sales/product-performance/', ProductPerformanceView.as_view(), name='product-performance'),

    #EmployeePerformance
    path('api/sales/employee-performance/', EmployeePerformanceView.as_view(), name='employee-performance'),

    # LeaderboardView
    path('api/sales/leaderboard/', LeaderboardView.as_view(), name='leaderboard'),

    # SalesSummary
    path('api/sales/summary/', SalesSummaryView.as_view(), name='sales-summary'),
]

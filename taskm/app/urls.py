from django.urls import path

from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),

    path('employees/', views.employee_list, name='employee_list'),
    path('products/', views.product_list, name='product_list'),
    path('sales/', views.sales_list, name='sales_list'),
    path('add_sale/', views.add_sale, name='add_sale'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('daily_stats/', views.daily_stats, name='daily_stats'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Default route for the homepage
    #path('stat/', views.statistic, name='statistic'),  # Statistics page route
    #path('tasks/', views.tasks, name='tasks'),  # Task page route

    # Authentication endpoints
    path('api/register/', views.RegisterView.as_view(), name='register_api'),
    path('api/login/', views.LoginView.as_view(), name='login_api'),
    path('api/logout/', views.LogoutView.as_view(), name='logout_api'),
    path('api/user_status/', views.UserStatusView.as_view(), name='user_status'),

# Product endpoints
    path('api/products/', views.ProductListView.as_view(), name='product_list'),
    path('api/products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('api/products/<int:product_id>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('api/products/<int:product_id>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('api/products/<int:product_id>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # SalesStatistics
    path('api/sales/statistics/', views.SalesStatisticsView.as_view(), name='sales-statistics'),

    # ProductPerformance
    path('api/sales/product-performance/', views.ProductPerformanceView.as_view(), name='product-performance'),

    #EmployeePerformance
    path('api/sales/employee-performance/', views.EmployeePerformanceView.as_view(), name='employee-performance'),

    # LeaderboardView
    path('api/sales/leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),

    # SalesSummary
    path('api/sales/summary/', views.SalesSummaryView.as_view(), name='sales-summary'),
]

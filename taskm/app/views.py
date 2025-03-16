import json
from datetime import timedelta, datetime

from django.contrib.auth import login, authenticate, logout
from django.db.models import Sum, F, DecimalField, Count
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render
from django.template.defaulttags import now
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils.timezone import now

from app.models import Product, Sale


def index(request):
    return render(request, "index.html")


def statistic(request):
    return render(request, "statistic.html")


def tasks(request):
    return render(request, "tasks.html")


def page_not_found(request, exception):
    return render(request, "notfound.html")


class LoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        return super().dispatch(request, *args, **kwargs)


class StaffRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return JsonResponse({'error': 'Admin access required'}, status=403)
        return super().dispatch(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)

        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'is_staff': user.is_staff
        })


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                'id': user.id,
                'username': user.username,
                'is_staff': user.is_staff
            })
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)


class LogoutView(View):
    def post(self, request):
        logout(request)
        return JsonResponse({'success': True})


class UserStatusView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return JsonResponse({
                'authenticated': True,
                'id': request.user.id,
                'username': request.user.username,
                'is_staff': request.user.is_staff
            })
        else:
            return JsonResponse({'authenticated': False})


# Views для Product
class DateRangeMixin:
    def get_date_range(self, request):
        period = request.GET.get('period', 'week')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        end_date = now()

        # Set default or custom period
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                period = 'custom'
            except ValueError:
                start_date = self._get_start_date(period, end_date)
        else:
            start_date = self._get_start_date(period, end_date)

        return start_date, end_date, period

    def _get_start_date(self, period, end_date):
        return {
            'day': end_date - timedelta(days=1),
            'week': end_date - timedelta(weeks=1),
            'month': end_date - timedelta(days=30)
        }.get(period, end_date - timedelta(days=30))


class ProductListView(View):
    def get(self, request):
        # Use select_related or prefetch_related if needed to optimize queries
        products = Product.objects.all().values('id', 'name', 'description', 'price')
        return JsonResponse({'products': list(products)})


@method_decorator(csrf_exempt, name='dispatch')
class ProductCreateView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            # Validate required fields
            required_fields = ['name', 'price']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

            product = Product.objects.create(
                name=data['name'],
                description=data.get('description', ''),  # Use get with default value
                price=data['price'],
                created_by=request.user
            )

            return JsonResponse({
                'id': product.id,
                'name': product.name,
                'price': product.price
            }, status=201)  # 201 Created status

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            # Use select_related to optimize query
            product = Product.objects.select_related('created_by').get(id=product_id)
            return JsonResponse({
                'id': product.id,
                'name': product.name,
                'price': product.price
            })
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class ProductUpdateView(LoginRequiredMixin, View):
    def put(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)

            try:
                data = json.loads(request.body)

                # Update fields only if they exist in the request
                if 'name' in data:
                    product.name = data['name']
                if 'description' in data:
                    product.description = data['description']
                if 'price' in data:
                    product.price = data['price']

                product.save()

                return JsonResponse({
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': product.price
                })
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)

        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def patch(self, request, product_id):
        return self.put(request, product_id)


@method_decorator(csrf_exempt, name='dispatch')
class ProductDeleteView(LoginRequiredMixin, View):
    def delete(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)

            # Security check
            if not request.user.is_staff:
                return JsonResponse({'error': 'Not authorized to delete products'}, status=403)

            product.delete()
            return JsonResponse({'success': 'Product deleted successfully'}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class SalesStatisticsView(DateRangeMixin, View):
    def get(self, request, period='day'):
        start_date, end_date, period = self.get_date_range(request)

        # Total sales statistics
        total_sales = Sale.objects.filter(date__range=[start_date, end_date]).aggregate(
            total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
        )['total']

        total_transactions = Sale.objects.filter(date__range=[start_date, end_date]).count()

        return JsonResponse({
            'total_sales': total_sales,
            'total_transactions': total_transactions,
            'period': period,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        })


class EmployeePerformanceView(DateRangeMixin, View):
    def get(self, request):
        period = request.GET.get('period', 'week')
        limit = int(request.GET.get('limit', 10))

        start_date, end_date, period = self.get_date_range(request)

        # Employee performance
        employee_performance = Sale.objects.filter(
            date__range=[start_date, end_date]
        ).values(
            'employee__id', 'employee__username'
        ).annotate(
            total_sales=Sum('amount'),
            transactions_count=Count('id'),
            average_sale=Sum('amount') / Count('id')
        ).order_by('-total_sales')[:limit]

        return JsonResponse({
            'employee_performance': list(employee_performance),
            'period': period,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        })


class ProductPerformanceView(DateRangeMixin, View):
    def get(self, request):
        period = request.GET.get('period', 'week')
        limit = int(request.GET.get('limit', 10))

        start_date, end_date, period = self.get_date_range(request)

        # Product performance
        product_performance = Sale.objects.filter(
            date__range=[start_date, end_date]
        ).values(
            'product__id', 'product__name'
        ).annotate(
            total_sales=Sum('amount'),
            units_sold=Sum('quantity'),
            revenue=Sum(F('amount') * F('quantity'))
        ).order_by('-total_sales')[:limit]

        return JsonResponse({
            'product_performance': list(product_performance),
            'period': period,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        })


class LeaderboardView(DateRangeMixin, View):
    def get(self, request):
        period = request.GET.get('period', 'week')
        employee_limit = int(request.GET.get('employee_limit', 5))
        product_limit = int(request.GET.get('product_limit', 5))

        start_date, end_date, period = self.get_date_range(request)

        # Filter sales once to improve performance
        sales_in_period = Sale.objects.filter(date__range=[start_date, end_date])

        # Top employees
        top_employees = sales_in_period.values(
            'employee__id', 'employee__username'
        ).annotate(
            total_sales=Sum('amount'),
            transactions_count=Count('id')
        ).order_by('-total_sales')[:employee_limit]

        # Top products
        top_products = sales_in_period.values(
            'product__id', 'product__name'
        ).annotate(
            total_sales=Sum('amount'),
            units_sold=Sum('quantity')
        ).order_by('-total_sales')[:product_limit]

        return JsonResponse({
            'top_employees': list(top_employees),
            'top_products': list(top_products),
            'period': period,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        })


class SalesSummaryView(DateRangeMixin, View):
    def get(self, request):
        period = request.GET.get('period', 'week')

        start_date, end_date, period = self.get_date_range(request)

        # Filter sales once to improve performance
        sales_data = Sale.objects.filter(date__range=[start_date, end_date])

        # Sales statistics
        total_sales = sales_data.aggregate(
            total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
        )['total']

        total_transactions = sales_data.count()
        average_sale = total_sales / total_transactions if total_transactions > 0 else 0

        # Count unique employees and products
        unique_employees = sales_data.values('employee').distinct().count()
        unique_products = sales_data.values('product').distinct().count()

        return JsonResponse({
            'total_sales': total_sales,
            'total_transactions': total_transactions,
            'average_sale': average_sale,
            'unique_employees': unique_employees,
            'unique_products': unique_products,
            'period': period,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        })
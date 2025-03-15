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

class ProductListView(View):
    def get(self, request):
        products = Product.objects.all().values('id', 'name', 'description', 'price')
        return JsonResponse({'products': list(products)})


@method_decorator(csrf_exempt, name='dispatch')
class ProductCreateView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        product = Product.objects.create(
            name=data.get('name'),
            description=data.get('description'),
            price=data.get('price'),
            created_by=request.user
        )
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price
        })


class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            return JsonResponse({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'created_by': product.created_by.username
            })
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class ProductUpdateView(LoginRequiredMixin, View):
    def put(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)

            if product.created_by != request.user and not request.user.is_staff:
                return JsonResponse({'error': 'Not authorized to update this product'}, status=403)

            data = json.loads(request.body)
            product.name = data.get('name', product.name)
            product.description = data.get('description', product.description)
            product.price = data.get('price', product.price)
            product.save()

            return JsonResponse({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price
            })
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)

    def patch(self, request, product_id):
        return self.put(request, product_id)


@method_decorator(csrf_exempt, name='dispatch')
class ProductDeleteView(LoginRequiredMixin, StaffRequiredMixin, View):
    def delete(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            return JsonResponse({'success': True})
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)


class SalesStatisticsView(View):
    def get(self, request, period='day'):
        # Отримання параметрів для кастомного періоду
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        end_date = now()

        # Встановлення періоду за замовчуванням або кастомного
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                period = 'custom'
            except ValueError:
                # Якщо формат дати неправильний, використовуємо стандартні періоди
                start_date = {
                    'day': end_date - timedelta(days=1),
                    'week': end_date - timedelta(weeks=1),
                    'month': end_date - timedelta(days=30)
                }.get(period, end_date - timedelta(days=30))
        else:
            start_date = {
                'day': end_date - timedelta(days=1),
                'week': end_date - timedelta(weeks=1),
                'month': end_date - timedelta(days=30)
            }.get(period, end_date - timedelta(days=30))

# Загальна статистика продажів
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


class EmployeePerformanceView(View):
    def get(self, request):
        # Отримання параметрів для періоду
        period = request.GET.get('period', 'week')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        limit = int(request.GET.get('limit', 10))  # Кількість найкращих працівників

        end_date = now()

        # Встановлення періоду за замовчуванням або кастомного
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                start_date = {
                    'day': end_date - timedelta(days=1),
                    'week': end_date - timedelta(weeks=1),
                    'month': end_date - timedelta(days=30)
                }.get(period, end_date - timedelta(days=30))
        else:
            start_date = {
                'day': end_date - timedelta(days=1),
                'week': end_date - timedelta(weeks=1),
                'month': end_date - timedelta(days=30)
            }.get(period, end_date - timedelta(days=30))

        # Отримання продуктивності працівників
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


class ProductPerformanceView(View):
    def get(self, request):
        # Отримання параметрів для періоду
        period = request.GET.get('period', 'week')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        limit = int(request.GET.get('limit', 10))  # Кількість найкращих продуктів

        end_date = now()

        # Встановлення періоду за замовчуванням або кастомного
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                start_date = {
                    'day': end_date - timedelta(days=1),
                    'week': end_date - timedelta(weeks=1),
                    'month': end_date - timedelta(days=30)
                }.get(period, end_date - timedelta(days=30))
        else:
            start_date = {
                'day': end_date - timedelta(days=1),
                'week': end_date - timedelta(weeks=1),
                'month': end_date - timedelta(days=30)
            }.get(period, end_date - timedelta(days=30))

        # Отримання продуктивності продуктів
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


class LeaderboardView(View):
    def get(self, request):
        # Отримання параметрів для періоду
        period = request.GET.get('period', 'week')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        employee_limit = int(request.GET.get('employee_limit', 5))
        product_limit = int(request.GET.get('product_limit', 5))

        end_date = now()

        # Встановлення періоду за замовчуванням або кастомного
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                start_date = {
                    'day': end_date - timedelta(days=1),
                    'week': end_date - timedelta(weeks=1),
                    'month': end_date - timedelta(days=30)
                }.get(period, end_date - timedelta(days=30))
        else:
            start_date = {
                'day': end_date - timedelta(days=1),
                'week': end_date - timedelta(weeks=1),
                'month': end_date - timedelta(days=30)
            }.get(period, end_date - timedelta(days=30))

        # Топ працівників
        top_employees = Sale.objects.filter(
            date__range=[start_date, end_date]
        ).values(
            'employee__id', 'employee__username'
        ).annotate(
            total_sales=Sum('amount'),
            transactions_count=Count('id')
        ).order_by('-total_sales')[:employee_limit]

        # Топ продуктів
        top_products = Sale.objects.filter(
            date__range=[start_date, end_date]
        ).values(
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


class SalesSummaryView(View):
    def get(self, request):
        # Отримання параметрів для періоду
        period = request.GET.get('period', 'week')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        end_date = now()

        # Встановлення періоду за замовчуванням або кастомного
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                start_date = {
                    'day': end_date - timedelta(days=1),
                    'week': end_date - timedelta(weeks=1),
                    'month': end_date - timedelta(days=30)
                }.get(period, end_date - timedelta(days=30))
        else:
            start_date = {
                'day': end_date - timedelta(days=1),
                'week': end_date - timedelta(weeks=1),
                'month': end_date - timedelta(days=30)
            }.get(period, end_date - timedelta(days=30))

        # Загальна статистика
        sales_data = Sale.objects.filter(date__range=[start_date, end_date])
        total_sales = sales_data.aggregate(total=Coalesce(Sum('amount'), 0, output_field=DecimalField()))['total']
        total_transactions = sales_data.count()
        average_sale = total_sales / total_transactions if total_transactions > 0 else 0

        # Кількість унікальних продавців і проданих товарів
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

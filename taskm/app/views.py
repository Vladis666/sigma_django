import json
from datetime import timedelta, datetime
from django.contrib.auth import login, authenticate, logout
from django.db.models import Sum, F, DecimalField, Count, Value, Q
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render
from django.template.defaulttags import now
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils import timezone
from app.models import Product, Sale, Employee, SalesPlan
from .forms import SaleForm, SalesFilterForm, ProductForm
from django.contrib import messages
from django.shortcuts import render, redirect

def home(request):
    # Основні показники для головної сторінки
    total_sales = Sale.objects.count()
    total_revenue = Sale.objects.aggregate(total=Sum('product__price'))['total'] or 0
    employees_count = Employee.objects.count()
    products_count = Product.objects.count()

    # Останні продажі
    recent_sales = Sale.objects.order_by('-date')[:5]

    return render(request, 'app/home.html', {
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'employees_count': employees_count,
        'products_count': products_count,
        'recent_sales': recent_sales,
    })


def add_sale(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)  # Зберігаємо, але не записуємо у БД
            id_to_sale=sale.product.id
            product = Product.objects.get(id=id_to_sale)
            # Перевіряємо, чи є достатня кількість товару
            if product.quantity >= sale.quantity:
                product.quantity -= sale.quantity  # Віднімаємо продану кількість
                product.save()  # Оновлюємо товар у БД
                sale.save()  # Зберігаємо продаж
                messages.success(request, 'Продаж успішно додано!')
                return redirect('sales_list')
            else:
                messages.error(request, 'Недостатня кількість товару!')
    else:
        form = SaleForm()

    return render(request, 'app/add_sale.html', {'form': form})


def edit_product(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        print(f"Отриманий ID продукту: {product_id}")
        product = get_object_or_404(Product, id=product_id)

        product.name = request.POST.get('name')
        product.quantity = request.POST.get('quantity')
        product.price = request.POST.get('price')
        product.active = 'active' in request.POST

        product.save()
        return redirect('product_list')  # Направляємо на сторінку зі списком товарів


def add_product(request):
    print("product added")
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успішно додано!')
            print("product added")
            return redirect('product_list')  # Заміни на відповідний шлях
    else:
        form = ProductForm()

    return render(request, 'app/add_product.html', {'form': form})

def admin_dashboard(request):
    total_sales = Sale.objects.count()
    total_revenue = Sale.objects.aggregate(total=Sum('product__price'))['total'] or 0
    employees_count = Employee.objects.count()
    products_count = Product.objects.count()

    # Отримуємо поточну дату і початок місяця
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)

    # Останні продажі
    recent_sales = Sale.objects.order_by('-date')[:5]

    # Топ працівників за останні 30 днів
    top_employees = Employee.objects.filter(sale__date__date__gte=last_30_days) \
                        .annotate(sales_count=Count('sale')) \
                        .order_by('-sales_count')[:5]

    # Активні плани продажів
    active_plans = SalesPlan.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    )

    plans_progress = []
    for plan in active_plans:
        # Обчислюємо кількість продажів для цього товару в період плану
        actual_sales = Sale.objects.filter(
            product=plan.product,
            date__date__gte=plan.start_date,
            date__date__lte=today
        ).aggregate(total=Sum('quantity'))['total'] or 0

        # Рахуємо відсоток виконання плану
        if plan.target_amount > 0:
            progress_percent = (actual_sales / plan.target_amount) * 100
        else:
            progress_percent = 0

        plans_progress.append({
            'plan': plan,
            'actual_sales': actual_sales,
            'progress_percent': progress_percent,
            'days_left': (plan.end_date - today).days
        })

    # Товари з малим запасом
    low_stock_products = Product.objects.filter(active=True, quantity__lt=10).order_by('quantity')[:5]

    return render(request, 'app/admin_dashboard.html', {
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'employees_count': employees_count,
        'products_count': products_count,
        'recent_sales': recent_sales,
        'top_employees': top_employees,
        'plans_progress': plans_progress,
        'low_stock_products': low_stock_products,
    })

def daily_stats(request):
    seven_days_ago = timezone.now().date() - timedelta(days=7)

    daily_data = []
    for days_ago in range(7):
        date = timezone.now().date() - timedelta(days=days_ago)
        sales_count = Sale.objects.filter(date__date=date).count()
        revenue = Sale.objects.filter(date__date=date).aggregate(
            total=Sum('product__price'))['total'] or 0

        daily_data.append({
            'date': date,
            'sales_count': sales_count,
            'revenue': revenue
        })

    daily_data.reverse()  # Щоб показати від старих до нових

    return render(request, 'app/daily_stats.html', {'daily_data': daily_data})


def employee_list(request):
    # Обробка форми при POST-запиті
    if request.method == 'POST' and request.POST.get('action') == 'add_employee':
        try:
            # Створення користувача
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password')

            # Перевірка, чи не існує вже користувач з таким іменем
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Користувач з логіном {username} вже існує')
                return redirect('employee_list')

            # Створюємо нового користувача
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Створення співробітника
            position = request.POST.get('position')
            phone = request.POST.get('phone')

            employee = Employee.objects.create(
                user=user,
                position=position,
                phone=phone
            )

            messages.success(request, f'Співробітник {first_name} {last_name} успішно доданий')
            return redirect('employee_list')

        except Exception as e:
            messages.error(request, f'Помилка при створенні співробітника: {str(e)}')

    # Отримання всіх співробітників для відображення
    employees = Employee.objects.all().select_related('user')

    return render(request, 'app/employee_list.html', {
        'employees': employees
    })


def leaderboard(request):
    thirty_days_ago = timezone.now() - timedelta(days=30)

    leaders = Employee.objects.annotate(
        sales_count=Count('sale', filter=Q(sale__date__gte=thirty_days_ago))
    ).order_by('-sales_count')[:10]

    print(leaders)  # Debugging

    return render(request, 'app/leaderboard.html', {'leaders': leaders})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'app/product_list.html', {'products': products})

def sales_list(request):
    sales = Sale.objects.all().order_by('-date')

    filter_form = SalesFilterForm(request.GET)

    if filter_form.is_valid():
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        employee = filter_form.cleaned_data.get('employee')
        product = filter_form.cleaned_data.get('product')

        if start_date:
            sales = sales.filter(date__date__gte=start_date)
        if end_date:
            sales = sales.filter(date__date__lte=end_date)

        if employee:
            sales = sales.filter(employee=employee)

        if product:
            sales = sales.filter(product=product)

    return render(request, 'app/sales_list.html', {'sales': sales, 'filter_form': filter_form})



def page_not_found(request, exception):
    return render(request, "app/notfound.html")


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
        products = Product.objects.all().values('id', 'name', 'quantity', 'price')
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
                price=data['price'],
                quantity=data.get('quantity', 0)
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
            # Перевіряємо, чи користувач автентифікований
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)

            # Перевіряємо, чи користувач має права адміністратора
            if not request.user.is_staff:
                return JsonResponse({'error': 'Not authorized to delete products'}, status=403)

            product = Product.objects.get(id=product_id)
            product.delete()
            return JsonResponse({'success': 'Product deleted successfully'}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class SalesStatisticsView(DateRangeMixin, View):
    def get(self, request):
        start_date, end_date, period = self.get_date_range(request)

        # Оптимізуємо запити до бази даних, виконуючи один запит з обома агрегаціями
        sales_data = Sale.objects.filter(date__range=[start_date, end_date])
        total_sales = sales_data.aggregate(
            total=Coalesce(Sum(F('product__price') * F('quantity')), Value(0), output_field=DecimalField())
        )['total']

        # Перетворюємо Decimal на float для коректної JSON серіалізації
        total_sales_float = float(total_sales) if total_sales else 0.0
        total_transactions = sales_data.count()

        return JsonResponse({
            'total_sales': total_sales_float,
            'total_transactions': total_transactions,
            'period': period,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        })

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Product  # Замініть на вашу модель

def get_product_info(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return JsonResponse({
        'price': product.price,
        'quantity': product.quantity  # Замініть на вашу змінну для кількості
    })

class EmployeePerformanceView(DateRangeMixin, View):
    def get(self, request):
        period = request.GET.get('period', 'week')
        limit = int(request.GET.get('limit', 10))

        start_date, end_date, period = self.get_date_range(request)

        employee_performance = Sale.objects.filter(
            date__range=[start_date, end_date]
        ).values(
            'employee__id', 'employee__user__username'  # Змінено на правильний шлях до username
        ).annotate(
            total_sales=Sum(F('product__price') * F('quantity')),
            transactions_count=Count('id'),
            average_sale=Sum(F('product__price') * F('quantity')) / Count('id')
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

        product_performance = Sale.objects.filter(
            date__range=[start_date, end_date]
        ).values(
            'product__id', 'product__name'
        ).annotate(
            total_sales=Sum(F('product__price') * F('quantity')),
            units_sold=Sum('quantity'),
            revenue=Sum(F('product__price') * F('quantity'))  # Тут revenue = total_sales
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

        sales_in_period = Sale.objects.filter(date__range=[start_date, end_date])

        top_employees = sales_in_period.values(
            'employee__id', 'employee__user__username'
        ).annotate(
            total_sales=Sum(F('product__price') * F('quantity')),
            transactions_count=Count('id')
        ).order_by('-total_sales')[:employee_limit]

        top_products = sales_in_period.values(
            'product__id', 'product__name'
        ).annotate(
            total_sales=Sum(F('product__price') * F('quantity')),
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

        sales_data = Sale.objects.filter(date__range=[start_date, end_date])

        total_sales = sales_data.aggregate(
            total=Coalesce(Sum(F('product__price') * F('quantity')), 0, output_field=DecimalField())
        )['total']

        total_transactions = sales_data.count()
        average_sale = total_sales / total_transactions if total_transactions > 0 else 0

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
from unittest.mock import patch, MagicMock
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Sale, Product


class SalesStatisticsTests(APITestCase):
    def setUp(self):
        self.url = reverse('sales-statistics')

    @patch('app.views.Sale.objects')
    def test_sales_statistics(self, mock_sales_objects):
        # Setup mocks for filtering and aggregation
        mock_filter_result = MagicMock()
        mock_filter_result.count.return_value = 3
        mock_sales_objects.filter.return_value = mock_filter_result
        mock_sales_objects.filter().aggregate.return_value = {'total': Decimal('80.0')}

        response = self.client.get(self.url)

        # Verify response and mocks
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(float(data['total_sales']), 80.0)
        self.assertEqual(data['total_transactions'], 3)
        mock_sales_objects.filter.assert_called()

    @patch('app.views.Sale.objects')
    def test_sales_statistics_custom_date_range(self, mock_sales_objects):
        # Setup mocks
        mock_filter_result = MagicMock()
        mock_filter_result.count.return_value = 3
        mock_filter_result.aggregate.return_value = {'total': Decimal('50.0')}
        mock_sales_objects.filter.return_value = mock_filter_result

        # Test with date parameters
        start_date = timezone.now().date().isoformat()
        end_date = timezone.now().date().isoformat()
        response = self.client.get(f"{self.url}?start_date={start_date}&end_date={end_date}")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['total_transactions'], 3)
        self.assertEqual(float(data['total_sales']), 50.0)
        mock_sales_objects.filter.assert_called_once()


class LoginViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('login_api')
        self.user_data = {'username': 'testuser', 'password': 'testpass123'}
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    @patch('django.contrib.auth.authenticate')
    def test_login_valid(self, mock_authenticate):
        mock_authenticate.return_value = self.user
        response = self.client.post(self.url, self.user_data, format='json')

        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('id', response_data)
        self.assertEqual(response_data['username'], 'testuser')

    @patch('django.contrib.auth.authenticate')
    def test_login_invalid(self, mock_authenticate):
        # Test with invalid credentials
        mock_authenticate.return_value = None
        invalid_data = {'username': 'testuser', 'password': 'wrongpass'}
        response = self.client.post(self.url, invalid_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())


class ProductCreateViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('product_create')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.product_data = {
            'name': 'New Product',
            'price': 15.0,
            'quantity': 50
        }

    def test_create_product_authenticated(self):
        # Test product creation when authenticated
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url, self.product_data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Product.objects.filter(name='New Product').exists())

    def test_create_product_unauthenticated(self):
        # Test product creation when not authenticated
        response = self.client.post(self.url, self.product_data, format='json')
        self.assertEqual(response.status_code, 401)


class ProductDeleteViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com',
            is_staff=True
        )
        self.product = Product.objects.create(
            name="Test Product",
            price=10.0,
            quantity=100
        )
        self.url = reverse('product_delete', args=[self.product.id])

    def test_delete_product_admin(self):
        # Test deletion by admin user
        self.client.login(username='admin', password='admin123')
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_delete_product_non_admin(self):
        # Test deletion by non-admin user (should fail)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Product.objects.filter(id=self.product.id).exists())
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from portfolio.models import Asset, Transaction, PortfolioAlerts
from portfolio.services.portfolio import PortfolioService
from portfolio.services.alert import AlertService

User = get_user_model()


class AssetModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_create_asset(self):
        asset = Asset.objects.create(
            symbol='BTC',
            amount=Decimal('1.5'),
            avg_price=Decimal('50000.00'),
            user=self.user
        )
        self.assertEqual(asset.symbol, 'BTC')
        self.assertEqual(asset.amount, Decimal('1.5'))
        self.assertEqual(str(asset), 'BTC')


class TransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_create_transaction(self):
        transaction = Transaction.objects.create(
            user=self.user,
            symbol='BTC',
            amount=Decimal('1.0'),
            price=Decimal('50000.00'),
            transaction_type='BUY'
        )
        self.assertEqual(transaction.symbol, 'BTC')
        self.assertEqual(transaction.transaction_type, 'BUY')
        self.assertIn('BUY', str(transaction))


class PortfolioServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_process_buy_new_asset(self):
        transaction = Transaction.objects.create(
            user=self.user,
            symbol='BTC',
            amount=Decimal('1.0'),
            price=Decimal('50000.00'),
            transaction_type='BUY'
        )
        PortfolioService.process_buy(transaction)
        
        asset = Asset.objects.get(user=self.user, symbol='BTC')
        self.assertEqual(asset.amount, Decimal('1.0'))
        self.assertEqual(asset.avg_price, Decimal('50000.00'))

    def test_process_buy_existing_asset(self):
        Asset.objects.create(
            user=self.user,
            symbol='BTC',
            amount=Decimal('1.0'),
            avg_price=Decimal('50000.00')
        )
        transaction = Transaction.objects.create(
            user=self.user,
            symbol='BTC',
            amount=Decimal('1.0'),
            price=Decimal('60000.00'),
            transaction_type='BUY'
        )
        PortfolioService.process_buy(transaction)
        
        asset = Asset.objects.get(user=self.user, symbol='BTC')
        self.assertEqual(asset.amount, Decimal('2.0'))
        self.assertEqual(asset.avg_price, Decimal('55000.00'))

    def test_process_sell_success(self):
        Asset.objects.create(
            user=self.user,
            symbol='BTC',
            amount=Decimal('2.0'),
            avg_price=Decimal('50000.00')
        )
        transaction = Transaction.objects.create(
            user=self.user,
            symbol='BTC',
            amount=Decimal('1.0'),
            price=Decimal('60000.00'),
            transaction_type='SELL'
        )
        PortfolioService.process_sell(transaction)
        
        asset = Asset.objects.get(user=self.user, symbol='BTC')
        self.assertEqual(asset.amount, Decimal('1.0'))

    def test_process_sell_all(self):
        Asset.objects.create(
            user=self.user,
            symbol='BTC',
            amount=Decimal('1.0'),
            avg_price=Decimal('50000.00')
        )
        transaction = Transaction.objects.create(
            user=self.user,
            symbol='BTC',
            amount=Decimal('1.0'),
            price=Decimal('60000.00'),
            transaction_type='SELL'
        )
        PortfolioService.process_sell(transaction)
        
        self.assertFalse(Asset.objects.filter(user=self.user, symbol='BTC').exists())

    def test_process_sell_asset_not_exist(self):
        transaction = Transaction.objects.create(
            user=self.user,
            symbol='BTC',
            amount=Decimal('1.0'),
            price=Decimal('60000.00'),
            transaction_type='SELL'
        )
        with self.assertRaises(ValueError):
            PortfolioService.process_sell(transaction)

    def test_process_sell_insufficient_amount(self):
        Asset.objects.create(
            user=self.user,
            symbol='BTC',
            amount=Decimal('0.5'),
            avg_price=Decimal('50000.00')
        )
        transaction = Transaction.objects.create(
            user=self.user,
            symbol='BTC',
            amount=Decimal('1.0'),
            price=Decimal('60000.00'),
            transaction_type='SELL'
        )
        with self.assertRaises(ValueError):
            PortfolioService.process_sell(transaction)


class AlertServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_check_alert_above(self):
        alert = PortfolioAlerts.objects.create(
            user=self.user,
            symbol='BTC',
            target_price=Decimal('50000.00'),
            alert_type='ABOVE'
        )
        self.assertTrue(AlertService.check_alert(alert, Decimal('51000.00')))
        self.assertFalse(AlertService.check_alert(alert, Decimal('49000.00')))

    def test_check_alert_below(self):
        alert = PortfolioAlerts.objects.create(
            user=self.user,
            symbol='BTC',
            target_price=Decimal('50000.00'),
            alert_type='BELOW'
        )
        self.assertTrue(AlertService.check_alert(alert, Decimal('49000.00')))
        self.assertFalse(AlertService.check_alert(alert, Decimal('51000.00')))


class AssetViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_assets(self):
        Asset.objects.create(
            user=self.user,
            symbol='BTC',
            amount=Decimal('1.0'),
            avg_price=Decimal('50000.00')
        )
        response = self.client.get('/api/v1/portfolio/assets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_assets_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/portfolio/assets/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_only_sees_own_assets(self):
        other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='testpass123'
        )
        Asset.objects.create(
            user=other_user,
            symbol='ETH',
            amount=Decimal('1.0'),
            avg_price=Decimal('3000.00')
        )
        response = self.client.get('/api/v1/portfolio/assets/')
        self.assertEqual(len(response.data), 0)


class TransactionViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_buy_transaction(self):
        data = {
            'symbol': 'BTC',
            'amount': '1.0',
            'price': '50000.00',
            'transaction_type': 'BUY'
        }
        response = self.client.post('/api/v1/portfolio/transactions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Asset.objects.filter(user=self.user, symbol='BTC').exists())

    def test_create_sell_transaction_fails_without_asset(self):
        data = {
            'symbol': 'BTC',
            'amount': '1.0',
            'price': '50000.00',
            'transaction_type': 'SELL'
        }
        response = self.client.post('/api/v1/portfolio/transactions/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_transactions(self):
        Transaction.objects.create(
            user=self.user,
            symbol='BTC',
            amount=Decimal('1.0'),
            price=Decimal('50000.00'),
            transaction_type='BUY'
        )
        response = self.client.get('/api/v1/portfolio/transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class SummaryViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch('portfolio.views.BinanceService.get_price')
    def test_summary_view(self, mock_get_price):
        mock_get_price.return_value = 60000.0
        
        Asset.objects.create(
            user=self.user,
            symbol='BTC',
            amount=Decimal('1.0'),
            avg_price=Decimal('50000.00')
        )
        
        response = self.client.get('/api/v1/portfolio/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('assets', response.data)
        self.assertIn('total_invested', response.data)
        self.assertIn('total_value', response.data)
        self.assertIn('total_pnl', response.data)
        self.assertEqual(len(response.data['assets']), 1)


class PortfolioAlertsViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_alert(self):
        data = {
            'symbol': 'BTC',
            'target_price': '60000.00',
            'alert_type': 'ABOVE'
        }
        response = self.client.post('/api/v1/portfolio/alerts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PortfolioAlerts.objects.filter(user=self.user, symbol='BTC').exists())

    def test_list_alerts(self):
        PortfolioAlerts.objects.create(
            user=self.user,
            symbol='BTC',
            target_price=Decimal('60000.00'),
            alert_type='ABOVE'
        )
        response = self.client.get('/api/v1/portfolio/alerts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_alert(self):
        alert = PortfolioAlerts.objects.create(
            user=self.user,
            symbol='BTC',
            target_price=Decimal('60000.00'),
            alert_type='ABOVE'
        )
        data = {'is_active': False}
        response = self.client.patch(f'/api/v1/portfolio/alerts/{alert.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        alert.refresh_from_db()
        self.assertFalse(alert.is_active)

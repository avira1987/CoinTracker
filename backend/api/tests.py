"""
تست‌های API برای CoinTracker
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from models.coin_models import Cryptocurrency, Settings, MonitoringStatus
from tasks.scheduler import get_scheduler
import json


class APITestCase(TestCase):
    """کلاس پایه برای تست‌های API"""
    
    def setUp(self):
        """تنظیمات اولیه برای هر تست"""
        self.client = APIClient()
        # استفاده از get_settings که خودش get_or_create می‌کند
        settings = Settings.get_settings()
        settings.top_coins_count = 10
        settings.update_interval = 60
        settings.save()
        
        # استفاده از get_status که خودش get_or_create می‌کند
        status_obj = MonitoringStatus.get_status()
        status_obj.is_running = False
        status_obj.last_error = ''
        status_obj.save()

    def tearDown(self):
        """پاکسازی بعد از هر تست"""
        # توقف scheduler در صورت فعال بودن
        try:
            scheduler = get_scheduler()
            if scheduler.is_running:
                scheduler.stop_monitoring()
        except:
            pass


class MonitoringStatusAPITest(APITestCase):
    """تست‌های API وضعیت پایش"""
    
    def test_get_monitoring_status(self):
        """تست دریافت وضعیت پایش"""
        url = reverse('monitoring-status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_running', response.data)
        self.assertIn('last_update', response.data)
        self.assertIn('last_error', response.data)
    
    def test_monitoring_status_structure(self):
        """تست ساختار پاسخ وضعیت پایش"""
        url = reverse('monitoring-status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        # بررسی فیلدهای مورد انتظار
        self.assertIsInstance(data['is_running'], bool)
        if data.get('last_update'):
            self.assertIsInstance(data['last_update'], str)
        if data.get('last_error'):
            self.assertIsInstance(data['last_error'], str)


class StartMonitoringAPITest(APITestCase):
    """تست‌های API شروع پایش"""
    
    def test_start_monitoring_success(self):
        """تست شروع موفق پایش"""
        url = reverse('monitoring-start')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        self.assertIn('message', response.data)
        
        # بررسی تغییر وضعیت در دیتابیس
        status_obj = MonitoringStatus.get_status()
        self.assertTrue(status_obj.is_running)
    
    def test_start_monitoring_already_running(self):
        """تست شروع پایش در حالی که قبلاً فعال است"""
        # شروع اولیه
        url = reverse('monitoring-start')
        response1 = self.client.post(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # تلاش برای شروع مجدد
        response2 = self.client.post(url)
        # باید موفق باشد (scheduler خودش بررسی می‌کند)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
    
    def test_start_monitoring_response_structure(self):
        """تست ساختار پاسخ شروع پایش"""
        url = reverse('monitoring-start')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertIn('success', data)
        self.assertIn('message', data)
        self.assertIsInstance(data['success'], bool)
        self.assertIsInstance(data['message'], str)


class StopMonitoringAPITest(APITestCase):
    """تست‌های API توقف پایش"""
    
    def test_stop_monitoring_success(self):
        """تست توقف موفق پایش"""
        # ابتدا شروع می‌کنیم
        start_url = reverse('monitoring-start')
        self.client.post(start_url)
        
        # سپس توقف می‌کنیم
        stop_url = reverse('monitoring-stop')
        response = self.client.post(stop_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        
        # بررسی تغییر وضعیت در دیتابیس
        status_obj = MonitoringStatus.get_status()
        self.assertFalse(status_obj.is_running)
    
    def test_stop_monitoring_when_not_running(self):
        """تست توقف پایش در حالی که فعال نیست"""
        url = reverse('monitoring-stop')
        response = self.client.post(url)
        
        # باید موفق باشد (scheduler خودش بررسی می‌کند)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_stop_monitoring_response_structure(self):
        """تست ساختار پاسخ توقف پایش"""
        url = reverse('monitoring-stop')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertIn('success', data)
        self.assertIn('message', data)
        self.assertIsInstance(data['success'], bool)
        self.assertIsInstance(data['message'], str)


class ManualUpdateAPITest(APITestCase):
    """تست‌های API به‌روزرسانی دستی"""
    
    def test_manual_update_success(self):
        """تست به‌روزرسانی دستی موفق"""
        url = reverse('manual-update')
        response = self.client.post(url)
        
        # ممکن است خطا بدهد اگر API CoinGecko در دسترس نباشد
        # اما باید ساختار پاسخ صحیح باشد
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ])
        
        self.assertIn('success', response.data)
        self.assertIn('message', response.data)
    
    def test_manual_update_response_structure(self):
        """تست ساختار پاسخ به‌روزرسانی دستی"""
        url = reverse('manual-update')
        response = self.client.post(url)
        
        self.assertIn('success', response.data)
        self.assertIn('message', response.data)
        self.assertIsInstance(response.data['success'], bool)
        self.assertIsInstance(response.data['message'], str)


class CoinsAPITest(APITestCase):
    """تست‌های API لیست کوین‌ها"""
    
    def setUp(self):
        """تنظیمات اولیه با داده‌های نمونه"""
        super().setUp()
        # ایجاد چند کوین نمونه
        for i in range(5):
            Cryptocurrency.objects.create(
                coin_id=f'coin-{i+1}',
                name=f'Coin {i+1}',
                symbol=f'COIN{i+1}',
                rank=i+1,
                current_price=100.0 + i * 10,
                market_cap=1000000 + i * 100000,
                volume_24h=500000 + i * 50000,
                price_change_24h=1.5 + i * 0.1,
                price_change_1h=0.5 + i * 0.05,
                price_change_7d=5.0 + i * 0.5,
                volume_change_24h=2.0 + i * 0.2,
            )
    
    def test_get_coins_list(self):
        """تست دریافت لیست کوین‌ها"""
        url = '/api/coins/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # بررسی ساختار پاسخ
        # ممکن است paginated باشد یا نباشد
        if 'results' in response.data:
            coins = response.data['results']
        else:
            coins = response.data
        
        self.assertIsInstance(coins, list)
        self.assertGreater(len(coins), 0)
    
    def test_coins_list_structure(self):
        """تست ساختار داده‌های کوین‌ها"""
        url = '/api/coins/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        if 'results' in response.data:
            coins = response.data['results']
        else:
            coins = response.data
        
        if len(coins) > 0:
            coin = coins[0]
            # بررسی فیلدهای مهم
            self.assertIn('id', coin)
            self.assertIn('name', coin)
            self.assertIn('symbol', coin)
            self.assertIn('rank', coin)
            self.assertIn('current_price', coin)
    
    def test_coins_ordered_by_rank(self):
        """تست مرتب‌سازی کوین‌ها بر اساس رتبه"""
        url = '/api/coins/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        if 'results' in response.data:
            coins = response.data['results']
        else:
            coins = response.data
        
        if len(coins) > 1:
            ranks = [coin['rank'] for coin in coins]
            self.assertEqual(ranks, sorted(ranks))


class SettingsAPITest(APITestCase):
    """تست‌های API تنظیمات"""
    
    def test_get_settings(self):
        """تست دریافت تنظیمات"""
        url = reverse('settings')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('top_coins_count', response.data)
        self.assertIn('update_interval', response.data)
    
    def test_update_settings(self):
        """تست به‌روزرسانی تنظیمات"""
        url = reverse('settings')
        new_data = {
            'top_coins_count': 20,
            'update_interval': 120
        }
        response = self.client.put(url, data=new_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['top_coins_count'], 20)
        self.assertEqual(response.data['update_interval'], 120)


class IntegrationTest(APITestCase):
    """تست‌های یکپارچه برای جریان کامل"""
    
    def test_full_monitoring_workflow(self):
        """تست جریان کامل: شروع، بررسی وضعیت، توقف"""
        # 1. بررسی وضعیت اولیه
        status_url = reverse('monitoring-status')
        response = self.client.get(status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        initial_status = response.data['is_running']
        
        # 2. شروع پایش
        start_url = reverse('monitoring-start')
        response = self.client.post(start_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 3. بررسی وضعیت بعد از شروع
        response = self.client.get(status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_running'])
        
        # 4. توقف پایش
        stop_url = reverse('monitoring-stop')
        response = self.client.post(stop_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 5. بررسی وضعیت بعد از توقف
        response = self.client.get(status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_running'])
    
    def test_api_endpoints_accessible(self):
        """تست دسترسی به تمام endpoint های مهم"""
        endpoints = [
            ('monitoring-status', 'GET', '/api/monitoring/status/'),
            ('monitoring-start', 'POST', '/api/monitoring/start/'),
            ('monitoring-stop', 'POST', '/api/monitoring/stop/'),
            ('manual-update', 'POST', '/api/monitoring/update/'),
            ('coin-list', 'GET', '/api/coins/'),
            ('settings', 'GET', '/api/settings/'),
        ]
        
        for endpoint_name, method, url_path in endpoints:
            if method == 'GET':
                response = self.client.get(url_path)
            else:
                response = self.client.post(url_path)
            
            # نباید 404 یا 403 باشد (ممکن است 500 باشد اگر API خارجی در دسترس نباشد)
            self.assertNotIn(response.status_code, [
                status.HTTP_404_NOT_FOUND,
                status.HTTP_403_FORBIDDEN
            ], f"Endpoint {endpoint_name} با method {method} قابل دسترسی نیست")

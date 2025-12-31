"""
Background Task Scheduler برای به‌روزرسانی خودکار داده‌ها
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.utils import timezone
from django.apps import apps
from datetime import timedelta
from services.coingecko_service import CoinGeckoService
from services.ranking_service import RankingService
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging
import json

logger = logging.getLogger(__name__)

channel_layer = get_channel_layer()


class SchedulerService:
    """سرویس مدیریت Background Tasks"""

    def __init__(self):
        self.scheduler = None
        self.is_running = False

    def update_task(self):
        """تسک به‌روزرسانی داده‌ها"""
        try:
            logger.info("Starting scheduled update...")
            
            Settings = apps.get_model('models', 'Settings')
            MonitoringStatus = apps.get_model('models', 'MonitoringStatus')
            
            # به‌روزرسانی داده‌ها از API
            coingecko_service = CoinGeckoService()
            coingecko_service.update_cryptocurrencies()
            
            # به‌روزرسانی رتبه‌بندی
            ranking_service = RankingService()
            ranking_service.update_rankings()
            
            # به‌روزرسانی وضعیت
            status_obj = MonitoringStatus.get_status()
            status_obj.last_update = timezone.now()
            settings = Settings.get_settings()
            status_obj.next_update = timezone.now() + timedelta(seconds=settings.update_interval)
            status_obj.last_error = ''
            status_obj.save()
            
            # ارسال به‌روزرسانی از طریق WebSocket
            self.broadcast_update()
            
            logger.info("Scheduled update completed successfully")
            
        except Exception as e:
            logger.error(f"Error in update task: {str(e)}")
            MonitoringStatus = apps.get_model('models', 'MonitoringStatus')
            status_obj = MonitoringStatus.get_status()
            status_obj.last_error = str(e)
            status_obj.save()
            
            # ارسال خطا از طریق WebSocket
            self.broadcast_error(str(e))

    def broadcast_update(self):
        """ارسال به‌روزرسانی به کلاینت‌های WebSocket"""
        try:
            Cryptocurrency = apps.get_model('models', 'Cryptocurrency')
            Settings = apps.get_model('models', 'Settings')
            MonitoringStatus = apps.get_model('models', 'MonitoringStatus')
            from api.serializers import CryptocurrencySerializer, MonitoringStatusSerializer
            
            settings = Settings.get_settings()
            coins = list(Cryptocurrency.objects.all().order_by('rank')[:settings.top_coins_count])
            coin_serializer = CryptocurrencySerializer(coins, many=True)
            
            status_obj = MonitoringStatus.get_status()
            status_serializer = MonitoringStatusSerializer(status_obj)
            
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    'coin_updates',
                    {
                        'type': 'coin_update',
                        'timestamp': timezone.now().isoformat()
                    }
                )
                
                async_to_sync(channel_layer.group_send)(
                    'coin_updates',
                    {
                        'type': 'status_update',
                        'status': status_serializer.data
                    }
                )
        except Exception as e:
            logger.error(f"Error broadcasting update: {str(e)}")

    def broadcast_error(self, error_message):
        """ارسال خطا به کلاینت‌های WebSocket"""
        try:
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    'coin_updates',
                    {
                        'type': 'error',
                        'message': error_message
                    }
                )
        except Exception as e:
            logger.error(f"Error broadcasting error: {str(e)}")

    def start_monitoring(self):
        """شروع پایش خودکار"""
        if self.is_running:
            logger.warning("Monitoring is already running")
            return

        try:
            Settings = apps.get_model('models', 'Settings')
            settings = Settings.get_settings()
            
            # ایجاد scheduler
            self.scheduler = BackgroundScheduler()
            self.scheduler.add_job(
                self.update_task,
                trigger=IntervalTrigger(seconds=settings.update_interval),
                id='coin_update_job',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"Monitoring started with interval: {settings.update_interval} seconds")
            
            # اجرای اولیه
            self.update_task()
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {str(e)}")
            raise

    def stop_monitoring(self):
        """توقف پایش خودکار"""
        if not self.is_running:
            logger.warning("Monitoring is not running")
            return

        try:
            if self.scheduler:
                self.scheduler.shutdown()
                self.scheduler = None
            
            self.is_running = False
            logger.info("Monitoring stopped")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring: {str(e)}")
            raise

    def restart_scheduler(self):
        """راه‌اندازی مجدد scheduler"""
        if self.is_running:
            self.stop_monitoring()
            self.start_monitoring()

# Singleton instance
_scheduler_instance = None

def get_scheduler():
    """دریافت instance سرویس scheduler"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = SchedulerService()
    return _scheduler_instance


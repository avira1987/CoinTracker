from django.db import models
from django.utils import timezone


class Cryptocurrency(models.Model):
    """مدل برای ذخیره اطلاعات اصلی هر ارز دیجیتال"""
    coin_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=20)
    current_price = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    market_cap = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    volume_24h = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    price_change_1h = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    price_change_24h = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    price_change_7d = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    volume_change_24h = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    rank = models.IntegerField(default=0)
    rank_score = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['rank']
        verbose_name = 'ارز دیجیتال'
        verbose_name_plural = 'ارزهای دیجیتال'

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class PriceHistory(models.Model):
    """تاریخچه قیمت‌ها برای محاسبه پایداری"""
    cryptocurrency = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=20, decimal_places=8)
    volume = models.DecimalField(max_digits=30, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    price_change_1h = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    price_change_24h = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    price_change_7d = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    volume_change_24h = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['cryptocurrency', '-timestamp']),
        ]
        verbose_name = 'تاریخچه قیمت'
        verbose_name_plural = 'تاریخچه قیمت‌ها'

    def __str__(self):
        return f"{self.cryptocurrency.name} - {self.timestamp}"


class Settings(models.Model):
    """تنظیمات سیستم - فقط یک رکورد"""
    api_key = models.CharField(max_length=200, default='')
    top_coins_count = models.IntegerField(default=100)
    price_weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.40)
    volume_weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.30)
    stability_weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.20)
    market_cap_weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.10)
    data_history_days = models.IntegerField(default=7)
    update_interval = models.IntegerField(default=60)  # seconds
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تنظیمات'
        verbose_name_plural = 'تنظیمات'

    def save(self, *args, **kwargs):
        # فقط یک رکورد تنظیمات وجود دارد
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'تنظیمات سیستم'


class MonitoringStatus(models.Model):
    """وضعیت پایش سیستم"""
    is_running = models.BooleanField(default=False)
    last_update = models.DateTimeField(null=True, blank=True)
    next_update = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'وضعیت پایش'
        verbose_name_plural = 'وضعیت پایش'

    def save(self, *args, **kwargs):
        # فقط یک رکورد وضعیت وجود دارد
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_status(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"پایش: {'فعال' if self.is_running else 'غیرفعال'}"


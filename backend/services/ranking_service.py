"""
سرویس رتبه‌بندی ارزهای دیجیتال بر اساس فرمول وزنی
"""
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.apps import apps
import statistics
import logging

logger = logging.getLogger(__name__)


class RankingService:
    """سرویس محاسبه رتبه‌بندی کوین‌ها"""

    def __init__(self):
        Settings = apps.get_model('models', 'Settings')
        self.settings = Settings.get_settings()

    def calculate_stability_score(self, cryptocurrency):
        """
        محاسبه نمره پایداری ترکیبی:
        1. واریانس تغییرات قیمت
        2. ثبات روند
        3. ریسک برگشت
        """
        try:
            PriceHistory = apps.get_model('models', 'PriceHistory')
            history_days = self.settings.data_history_days
            cutoff_date = timezone.now() - timedelta(days=history_days)

            # دریافت تاریخچه قیمت
            history = PriceHistory.objects.filter(
                cryptocurrency=cryptocurrency,
                timestamp__gte=cutoff_date
            ).order_by('timestamp')

            if history.count() < 2:
                return Decimal('50')  # نمره متوسط اگر داده کافی نباشد

            # 1. محاسبه واریانس تغییرات قیمت
            price_changes_24h = [float(h.price_change_24h) for h in history if h.price_change_24h]
            if len(price_changes_24h) > 1:
                variance = statistics.variance(price_changes_24h) if len(price_changes_24h) > 1 else 0
                # واریانس کمتر = پایداری بیشتر
                variance_score = max(0, 100 - min(100, variance / 10))
            else:
                variance_score = 50

            # 2. بررسی ثبات روند (تغییرات مداوم در یک جهت)
            if len(price_changes_24h) >= 3:
                # بررسی اینکه آیا تغییرات در یک جهت هستند
                positive_changes = sum(1 for change in price_changes_24h[-5:] if change > 0)
                negative_changes = sum(1 for change in price_changes_24h[-5:] if change < 0)
                
                # اگر تغییرات در یک جهت باشند، پایداری بیشتر
                if abs(positive_changes - negative_changes) >= 3:
                    trend_consistency = 80
                elif abs(positive_changes - negative_changes) >= 2:
                    trend_consistency = 60
                else:
                    trend_consistency = 40
            else:
                trend_consistency = 50

            # 3. ریسک برگشت (بر اساس نوسانات)
            if len(price_changes_24h) > 1:
                max_change = max(abs(change) for change in price_changes_24h)
                min_change = min(abs(change) for change in price_changes_24h)
                
                # اگر نوسانات زیاد باشد، ریسک برگشت بیشتر
                volatility = max_change - min_change if max_change > 0 else 0
                reversion_risk_score = max(0, 100 - min(100, volatility / 5))
            else:
                reversion_risk_score = 50

            # ترکیب سه معیار با وزن مساوی
            stability_score = (Decimal(str(variance_score)) * Decimal('0.4') +
                             Decimal(str(trend_consistency)) * Decimal('0.3') +
                             Decimal(str(reversion_risk_score)) * Decimal('0.3'))

            return stability_score

        except Exception as e:
            logger.error(f"Error calculating stability for {cryptocurrency.name}: {str(e)}")
            return Decimal('50')

    def normalize_price_change(self, price_change):
        """
        نرمال‌سازی تغییرات قیمت به بازه 0-100
        """
        # تغییرات قیمت می‌تواند از -100 تا +infinity باشد
        # نرمال‌سازی: -100% = 0, 0% = 50, +100% = 100, +200% = 100
        if price_change <= -100:
            return Decimal('0')
        elif price_change >= 200:
            return Decimal('100')
        else:
            # تبدیل خطی: -100 تا 200 -> 0 تا 100
            normalized = ((price_change + 100) / 300) * 100
            return max(Decimal('0'), min(Decimal('100'), Decimal(str(normalized))))

    def normalize_volume_change(self, volume_change):
        """
        نرمال‌سازی تغییرات حجم به بازه 0-100
        """
        # تغییرات حجم می‌تواند از -100 تا +infinity باشد
        if volume_change <= -100:
            return Decimal('0')
        elif volume_change >= 500:
            return Decimal('100')
        else:
            normalized = ((volume_change + 100) / 600) * 100
            return max(Decimal('0'), min(Decimal('100'), Decimal(str(normalized))))

    def normalize_market_cap(self, market_cap, all_market_caps):
        """
        نرمال‌سازی حجم بازار به بازه 0-100
        """
        if not all_market_caps or market_cap == 0:
            return Decimal('50')

        max_cap = max(all_market_caps)
        min_cap = min(all_market_caps)

        if max_cap == min_cap:
            return Decimal('50')

        # نرمال‌سازی: بزرگترین = 100, کوچکترین = 0
        normalized = ((market_cap - min_cap) / (max_cap - min_cap)) * 100
        return max(Decimal('0'), min(Decimal('100'), Decimal(str(normalized))))

    def calculate_rank_score(self, cryptocurrency, all_cryptocurrencies):
        """
        محاسبه نمره رتبه‌بندی با فرمول وزنی
        Score = (PriceChange * 0.4) + (VolumeChange * 0.3) + (Stability * 0.2) + (MarketCap * 0.1)
        """
        try:
            # نرمال‌سازی تغییرات قیمت
            price_score = self.normalize_price_change(cryptocurrency.price_change_24h)

            # نرمال‌سازی تغییرات حجم
            volume_score = self.normalize_volume_change(cryptocurrency.volume_change_24h)

            # محاسبه پایداری
            stability_score = self.calculate_stability_score(cryptocurrency)

            # نرمال‌سازی حجم بازار
            all_market_caps = [c.market_cap for c in all_cryptocurrencies if c.market_cap > 0]
            market_cap_score = self.normalize_market_cap(cryptocurrency.market_cap, all_market_caps)

            # اعمال وزن‌ها
            settings = self.settings
            final_score = (
                price_score * settings.price_weight +
                volume_score * settings.volume_weight +
                stability_score * settings.stability_weight +
                market_cap_score * settings.market_cap_weight
            )

            return final_score

        except Exception as e:
            logger.error(f"Error calculating rank score for {cryptocurrency.name}: {str(e)}")
            return Decimal('0')

    def update_rankings(self):
        """
        به‌روزرسانی رتبه‌بندی تمام کوین‌ها
        """
        try:
            Cryptocurrency = apps.get_model('models', 'Cryptocurrency')
            cryptocurrencies = list(Cryptocurrency.objects.all())

            if not cryptocurrencies:
                logger.warning("No cryptocurrencies to rank")
                return

            # محاسبه نمره برای هر کوین
            for coin in cryptocurrencies:
                score = self.calculate_rank_score(coin, cryptocurrencies)
                coin.rank_score = score

            # ذخیره نمره‌ها
            for coin in cryptocurrencies:
                coin.save()

            # مرتب‌سازی بر اساس نمره و تعیین رتبه
            cryptocurrencies.sort(key=lambda x: x.rank_score, reverse=True)

            for rank, coin in enumerate(cryptocurrencies, start=1):
                coin.rank = rank
                coin.save()

            logger.info(f"Updated rankings for {len(cryptocurrencies)} cryptocurrencies")
            return cryptocurrencies

        except Exception as e:
            logger.error(f"Error updating rankings: {str(e)}")
            raise


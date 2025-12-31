"""
سرویس دریافت داده از CoinGecko API
"""
import requests
from django.conf import settings
from decimal import Decimal
from datetime import datetime, timedelta
from models.coin_models import Cryptocurrency, PriceHistory, Settings
import logging

logger = logging.getLogger(__name__)


class CoinGeckoService:
    """سرویس برای دریافت و پردازش داده‌های CoinGecko"""

    def __init__(self):
        self.api_key = settings.COINGECKO_API_KEY
        self.base_url = settings.COINGECKO_API_URL
        self.headers = {
            'x-cg-demo-api-key': self.api_key
        } if self.api_key else {}

    def get_top_coins(self, limit=100):
        """
        دریافت لیست کوین‌های برتر از CoinGecko
        """
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': False,
                'price_change_percentage': '1h,24h,7d'
            }

            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching top coins: {str(e)}")
            raise

    def get_coin_details(self, coin_id):
        """
        دریافت جزئیات یک کوین خاص
        """
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            params = {
                'localization': False,
                'tickers': False,
                'market_data': True,
                'community_data': False,
                'developer_data': False,
                'sparkline': False
            }

            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching coin details for {coin_id}: {str(e)}")
            raise

    def update_cryptocurrencies(self):
        """
        به‌روزرسانی اطلاعات کوین‌ها از API
        """
        settings_obj = Settings.get_settings()
        top_coins_count = settings_obj.top_coins_count

        try:
            coins_data = self.get_top_coins(limit=top_coins_count)
            updated_coins = []

            for coin_data in coins_data:
                coin_id = coin_data.get('id')
                if not coin_id:
                    continue

                # محاسبه تغییرات حجم
                current_volume = Decimal(str(coin_data.get('total_volume', 0)))
                volume_change_24h = Decimal('0')

                # دریافت اطلاعات قبلی برای محاسبه تغییرات حجم
                try:
                    old_coin = Cryptocurrency.objects.get(coin_id=coin_id)
                    if old_coin.volume_24h and old_coin.volume_24h > 0:
                        volume_change_24h = ((current_volume - old_coin.volume_24h) / old_coin.volume_24h) * 100
                except Cryptocurrency.DoesNotExist:
                    pass

                # ایجاد یا به‌روزرسانی کوین
                coin, created = Cryptocurrency.objects.update_or_create(
                    coin_id=coin_id,
                    defaults={
                        'name': coin_data.get('name', ''),
                        'symbol': coin_data.get('symbol', '').upper(),
                        'current_price': Decimal(str(coin_data.get('current_price', 0))),
                        'market_cap': Decimal(str(coin_data.get('market_cap', 0))),
                        'volume_24h': current_volume,
                        'price_change_1h': Decimal(str(coin_data.get('price_change_percentage_1h_in_currency', 0) or 0)),
                        'price_change_24h': Decimal(str(coin_data.get('price_change_percentage_24h_in_currency', 0) or 0)),
                        'price_change_7d': Decimal(str(coin_data.get('price_change_percentage_7d_in_currency', 0) or 0)),
                        'volume_change_24h': volume_change_24h,
                    }
                )

                # ذخیره تاریخچه قیمت
                PriceHistory.objects.create(
                    cryptocurrency=coin,
                    price=coin.current_price,
                    volume=coin.volume_24h,
                    price_change_1h=coin.price_change_1h,
                    price_change_24h=coin.price_change_24h,
                    price_change_7d=coin.price_change_7d,
                    volume_change_24h=coin.volume_change_24h,
                )

                updated_coins.append(coin)

            # حذف کوین‌های قدیمی که دیگر در لیست نیستند
            existing_coin_ids = {coin.coin_id for coin in updated_coins}
            Cryptocurrency.objects.exclude(coin_id__in=existing_coin_ids).delete()

            logger.info(f"Updated {len(updated_coins)} cryptocurrencies")
            return updated_coins

        except Exception as e:
            logger.error(f"Error updating cryptocurrencies: {str(e)}")
            raise


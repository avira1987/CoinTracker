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
        به‌روزرسانی اطلاعات کوین‌ها از CoinGecko API با جزئیات کامل
        در هر بروزرسانی، اطلاعات کامل 100 کوین برتر با جزئیات ذخیره می‌شود
        توجه: داده‌های standing به صورت جداگانه از standing_service دریافت می‌شوند
        """
        settings_obj = Settings.get_settings()
        top_coins_count = settings_obj.top_coins_count

        try:
            coins_data = self.get_top_coins(limit=top_coins_count)
            
            # دریافت standing از دیتابیس (که قبلاً توسط standing_service به‌روزرسانی شده)
            # اگر standing وجود نداشته باشد، None می‌ماند و بعداً به‌روزرسانی می‌شود
            standing_map = {}
            existing_coins = Cryptocurrency.objects.exclude(standing__isnull=True).values('symbol', 'standing')
            for coin in existing_coins:
                standing_map[coin['symbol'].upper()] = coin['standing']
            logger.info(f"Loaded {len(standing_map)} standing records from database")
            
            updated_coins = []
            detailed_fetch_errors = 0

            for idx, coin_data in enumerate(coins_data, 1):
                coin_id = coin_data.get('id')
                if not coin_id:
                    continue

                try:
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

                    # دریافت standing از دیتابیس (نه از API)
                    symbol = coin_data.get('symbol', '').upper()
                    standing_value = standing_map.get(symbol)

                    # دریافت جزئیات کامل کوین از API
                    detailed_data = None
                    try:
                        detailed_data = self.get_coin_details(coin_id)
                        logger.debug(f"Fetched detailed data for {coin_id} ({idx}/{len(coins_data)})")
                    except Exception as e:
                        detailed_fetch_errors += 1
                        logger.warning(f"Could not fetch detailed data for {coin_id}: {str(e)}")
                        # ادامه می‌دهیم با داده‌های پایه

                    # استخراج داده‌های جزئیات از detailed_data
                    market_data = detailed_data.get('market_data', {}) if detailed_data else {}
                    links = detailed_data.get('links', {}) if detailed_data else {}
                    description = detailed_data.get('description', {}) if detailed_data else {}
                    
                    # تابع کمکی برای استخراج مقدار از market_data (پشتیبانی از dict و مقدار مستقیم)
                    def get_market_value(key, default=None):
                        value = market_data.get(key, default)
                        if value is None:
                            return None
                        if isinstance(value, dict):
                            return value.get('usd', default)
                        return value
                    
                    # استخراج description (اولین زبان موجود)
                    description_text = ''
                    if isinstance(description, dict):
                        for lang in ['en', 'fa', 'ar']:
                            if lang in description and description[lang]:
                                description_text = description[lang][:2000]  # محدود کردن طول
                                break
                    elif isinstance(description, str):
                        description_text = description[:2000]

                    # استخراج URL تصویر
                    image_url = ''
                    if detailed_data and 'image' in detailed_data:
                        image_url = detailed_data['image'].get('large', '') or detailed_data['image'].get('small', '') or ''
                    elif coin_data.get('image'):
                        image_url = coin_data.get('image', '')

                    # استخراج URLs
                    homepage_urls = links.get('homepage', []) if links else []
                    blockchain_sites = links.get('blockchain_site', []) if links else []
                    official_forum_urls = links.get('official_forum_url', []) if links else []
                    subreddit_url = links.get('subreddit_url', '') if links else ''
                    github_repos = links.get('repos_url', {}).get('github', []) if links else []
                    twitter_screen_name = links.get('twitter_screen_name', '') if links else ''

                    # استخراج مقادیر market_data با استفاده از تابع کمکی
                    high_24h_val = get_market_value('high_24h')
                    low_24h_val = get_market_value('low_24h')
                    circulating_supply_val = get_market_value('circulating_supply')
                    total_supply_val = get_market_value('total_supply')
                    max_supply_val = get_market_value('max_supply')
                    fully_diluted_val = get_market_value('fully_diluted_valuation')
                    total_value_locked_val = get_market_value('total_value_locked')

                    # ایجاد یا به‌روزرسانی کوین با تمام جزئیات
                    coin, created = Cryptocurrency.objects.update_or_create(
                        coin_id=coin_id,
                        defaults={
                            'name': coin_data.get('name', ''),
                            'symbol': symbol,
                            'current_price': Decimal(str(coin_data.get('current_price', 0))),
                            'market_cap': Decimal(str(coin_data.get('market_cap', 0))),
                            'volume_24h': current_volume,
                            'price_change_1h': Decimal(str(coin_data.get('price_change_percentage_1h_in_currency', 0) or 0)),
                            'price_change_24h': Decimal(str(coin_data.get('price_change_percentage_24h_in_currency', 0) or 0)),
                            'price_change_7d': Decimal(str(coin_data.get('price_change_percentage_7d_in_currency', 0) or 0)),
                            'volume_change_24h': volume_change_24h,
                            'standing': standing_value,
                            # جزئیات بیشتر از market_data
                            'high_24h': Decimal(str(high_24h_val)) if high_24h_val else None,
                            'low_24h': Decimal(str(low_24h_val)) if low_24h_val else None,
                            'circulating_supply': Decimal(str(circulating_supply_val)) if circulating_supply_val else None,
                            'total_supply': Decimal(str(total_supply_val)) if total_supply_val else None,
                            'max_supply': Decimal(str(max_supply_val)) if max_supply_val else None,
                            'market_cap_rank': market_data.get('market_cap_rank') or coin_data.get('market_cap_rank'),
                            'fully_diluted_valuation': Decimal(str(fully_diluted_val)) if fully_diluted_val else None,
                            'total_value_locked': Decimal(str(total_value_locked_val)) if total_value_locked_val else None,
                            # اطلاعات اضافی
                            'image_url': image_url,
                            'description': description_text,
                            'homepage_url': homepage_urls[0] if homepage_urls else '',
                            'blockchain_site': blockchain_sites[0] if blockchain_sites else '',
                            'official_forum_url': official_forum_urls[0] if official_forum_urls else '',
                            'subreddit_url': subreddit_url,
                            'github_url': github_repos[0] if github_repos else '',
                            'twitter_handle': twitter_screen_name,
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

                except Exception as e:
                    logger.error(f"Error processing coin {coin_id}: {str(e)}")
                    continue

            # حذف کوین‌های قدیمی که دیگر در لیست نیستند
            existing_coin_ids = {coin.coin_id for coin in updated_coins}
            Cryptocurrency.objects.exclude(coin_id__in=existing_coin_ids).delete()

            logger.info(f"Updated {len(updated_coins)} cryptocurrencies with full details. Detailed fetch errors: {detailed_fetch_errors}")
            return updated_coins

        except Exception as e:
            logger.error(f"Error updating cryptocurrencies: {str(e)}")
            raise


"""
سرویس برای دریافت و ذخیره داده‌های standing از API خارجی
"""
import requests
import logging
from django.utils import timezone
from datetime import timedelta
from models.coin_models import Cryptocurrency, SocialAPICache

logger = logging.getLogger(__name__)

# مدت زمان cache (ساعت)
CACHE_DURATION_HOURS = 1

# API اول
STANDING_API_URL_1 = 'http://81.168.119.209:8000/standing'
API_KEY_1 = 'FOTHB4y_kZPc08eCcwdSe19bFdYEOGm51zuw6I8V-ek'

# API دوم
STANDING_API_URL_2 = 'http://87.107.108.95:8000/standing'
API_KEY_2 = 'xl29bU5_kE8wfbEXY0w1Pyv-BpjGT3qzXwv7GEHkHqI'

# برای سازگاری با کد قدیمی
STANDING_API_URL = STANDING_API_URL_1
API_KEY = API_KEY_1


class StandingService:
    """سرویس مدیریت داده‌های standing"""
    
    @staticmethod
    def fetch_from_api(api_url, api_key, limit=10000, offset=0, use_cache=True):
        """
        دریافت داده‌های standing از یک API خاص با پشتیبانی از cache و fallback
        """
        # بررسی cache
        if use_cache:
            cache_obj = SocialAPICache.get_cache(api_url)
            if cache_obj.is_cache_valid(CACHE_DURATION_HOURS) and cache_obj.cached_data:
                logger.info(f"Using cached data for {api_url} (last updated: {cache_obj.last_successful_request})")
                return cache_obj.cached_data
        
        # درخواست به API
        try:
            headers = {
                'X-API-Key': api_key,
                'Content-Type': 'application/json'
            }
            
            params = {
                'limit': limit,
                'offset': offset
            }
            
            response = requests.get(api_url, headers=headers, params=params, timeout=120)
            
            if response.status_code != 200:
                logger.warning(f"API {api_url} returned status {response.status_code}: {response.text[:200]}")
                return None
            
            data = response.json()
            indicators = data.get('indicators', [])
            
            if not indicators:
                logger.warning(f"No indicators received from API {api_url}")
                return None
            
            logger.info(f"Received {len(indicators)} indicators from {api_url}")
            
            # ذخیره در cache فقط اگر موفق بود
            if use_cache:
                cache_obj = SocialAPICache.get_cache(api_url)
                cache_obj.update_cache(indicators)
                logger.info(f"Cached data for {api_url}")
            
            return indicators
            
        except requests.exceptions.Timeout:
            logger.warning(f"API {api_url} request timed out")
            return None
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error while fetching from {api_url}")
            return None
        except Exception as e:
            logger.warning(f"Error fetching from {api_url}: {str(e)}")
            return None
    
    @staticmethod
    def merge_indicators(indicators_list):
        """ترکیب داده‌های indicators از چند API (اولویت با API اول)"""
        merged = {}
        
        for indicators in indicators_list:
            if not indicators:
                continue
                
            for indicator in indicators:
                symbol = indicator.get('symbol', '').upper()
                standing = indicator.get('standing')
                
                if not symbol or standing is None:
                    continue
                
                # اگر symbol قبلاً وجود نداشته باشد، اضافه می‌کنیم
                # اگر وجود داشته باشد، از API اول استفاده می‌کنیم (اولویت)
                if symbol not in merged:
                    merged[symbol] = standing
        
        # تبدیل به لیست indicators
        result = []
        for symbol, standing in merged.items():
            result.append({
                'symbol': symbol,
                'standing': standing
            })
        
        return result
    
    @staticmethod
    def fetch_and_update_standing():
        """
        دریافت داده‌های standing فقط از API اول با cache
        """
        try:
            logger.info("Fetching standing data from API 1 only...")
            
            # دریافت از API اول
            logger.info(f"Fetching from API 1: {STANDING_API_URL_1}")
            indicators_1 = StandingService.fetch_from_api(
                STANDING_API_URL_1, 
                API_KEY_1, 
                limit=10000, 
                offset=0,
                use_cache=True
            )
            
            if not indicators_1:
                logger.warning("No indicators received from API 1")
                return False
            
            logger.info(f"✅ API 1 responded successfully with {len(indicators_1)} indicators")
            
            # استفاده مستقیم از داده‌های API اول (بدون ترکیب)
            indicators = indicators_1
            
            if not indicators:
                logger.warning("No indicators after processing")
                return False
            
            logger.info(f"Total {len(indicators)} indicators from API 1")
            
            # به‌روزرسانی standing برای هر کوین
            updated_count = 0
            not_found_count = 0
            
            for indicator in indicators:
                symbol = indicator.get('symbol', '').upper()
                standing = indicator.get('standing')
                
                if not symbol or standing is None:
                    continue
                
                try:
                    # پیدا کردن کوین بر اساس symbol
                    coin = Cryptocurrency.objects.filter(symbol__iexact=symbol).first()
                    
                    if coin:
                        coin.standing = standing
                        coin.save(update_fields=['standing'])
                        updated_count += 1
                    else:
                        not_found_count += 1
                        logger.debug(f"Coin with symbol {symbol} not found in database")
                        
                except Exception as e:
                    logger.error(f"Error updating standing for {symbol}: {str(e)}")
                    continue
            
            logger.info(f"Standing update completed: {updated_count} updated, {not_found_count} not found")
            return True
            
        except Exception as e:
            logger.error(f"Error fetching standing data: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    @staticmethod
    def get_standing_map():
        """دریافت Map از symbol به standing از دیتابیس"""
        standing_map = {}
        coins = Cryptocurrency.objects.exclude(standing__isnull=True).values('symbol', 'standing')
        
        for coin in coins:
            symbol = coin['symbol'].upper()
            standing = coin['standing']
            if symbol and standing is not None:
                standing_map[symbol] = standing
        
        return standing_map

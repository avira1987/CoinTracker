"""
API Views برای CoinTracker
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.sessions.models import Session
from django.utils import timezone
from models.coin_models import Cryptocurrency, Settings, MonitoringStatus
from api.serializers import (
    CryptocurrencySerializer, SettingsSerializer,
    MonitoringStatusSerializer, LoginSerializer
)
from services.coingecko_service import CoinGeckoService
from services.ranking_service import RankingService
from services.standing_service import StandingService
from tasks.scheduler import get_scheduler
import logging
import requests

logger = logging.getLogger(__name__)


class CryptocurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet برای لیست کوین‌ها"""
    queryset = Cryptocurrency.objects.all().order_by('-rank_score')
    serializer_class = CryptocurrencySerializer
    permission_classes = [AllowAny]  # برای نمایش عمومی

    def get_queryset(self):
        queryset = super().get_queryset()
        settings = Settings.get_settings()
        return queryset[:settings.top_coins_count]


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """احراز هویت ساده"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # بررسی اعتبارات
        if username == 'admin34_' and password == '123asd;p+_':
            # ایجاد session
            request.session['authenticated'] = True
            request.session['username'] = username
            return Response({
                'success': True,
                'message': 'ورود موفقیت‌آمیز بود'
            })
        else:
            return Response({
                'success': False,
                'message': 'نام کاربری یا رمز عبور اشتباه است'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_view(request):
    """خروج از سیستم"""
    request.session.flush()
    return Response({'success': True, 'message': 'خروج موفقیت‌آمیز بود'})


@api_view(['GET'])
def check_auth(request):
    """بررسی وضعیت احراز هویت - صفحه لاگین غیرفعال شده است"""
    return Response({
        'authenticated': True,
        'username': 'admin'
    })


def check_admin_auth(request):
    """بررسی احراز هویت ادمین - صفحه لاگین غیرفعال شده است، همیشه True برمی‌گرداند"""
    return True

@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def settings_view(request):
    """دریافت و به‌روزرسانی تنظیمات"""
    if not check_admin_auth(request):
        return Response({'error': 'احراز هویت لازم است'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if request.method == 'GET':
        settings = Settings.get_settings()
        serializer = SettingsSerializer(settings)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        settings = Settings.get_settings()
        serializer = SettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # به‌روزرسانی scheduler در صورت تغییر interval
            scheduler = get_scheduler()
            status_obj = MonitoringStatus.get_status()
            if status_obj.is_running:
                scheduler.restart_scheduler()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def monitoring_status_view(request):
    """دریافت وضعیت پایش"""
    status_obj = MonitoringStatus.get_status()
    serializer = MonitoringStatusSerializer(status_obj)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def start_monitoring_view(request):
    """شروع پایش"""
    if not check_admin_auth(request):
        return Response({'error': 'احراز هویت لازم است'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        from datetime import timedelta
        scheduler = get_scheduler()
        scheduler.start_monitoring()
        
        status_obj = MonitoringStatus.get_status()
        settings = Settings.get_settings()
        status_obj.is_running = True
        status_obj.last_error = ''
        # محاسبه زمان بروزرسانی بعدی
        if status_obj.last_update:
            status_obj.next_update = status_obj.last_update + timedelta(seconds=settings.update_interval)
        else:
            status_obj.next_update = timezone.now() + timedelta(seconds=settings.update_interval)
        status_obj.save()
        
        return Response({
            'success': True,
            'message': 'پایش با موفقیت شروع شد'
        })
    except Exception as e:
        logger.error(f"Error starting monitoring: {str(e)}")
        status_obj = MonitoringStatus.get_status()
        status_obj.last_error = str(e)
        status_obj.save()
        return Response({
            'success': False,
            'message': f'خطا در شروع پایش: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def stop_monitoring_view(request):
    """توقف پایش"""
    if not check_admin_auth(request):
        return Response({'error': 'احراز هویت لازم است'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        scheduler = get_scheduler()
        scheduler.stop_monitoring()
        
        status_obj = MonitoringStatus.get_status()
        status_obj.is_running = False
        status_obj.save()
        
        return Response({
            'success': True,
            'message': 'پایش با موفقیت متوقف شد'
        })
    except Exception as e:
        logger.error(f"Error stopping monitoring: {str(e)}")
        return Response({
            'success': False,
            'message': f'خطا در توقف پایش: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def manual_update_view(request):
    """به‌روزرسانی دستی داده‌ها - اجرای موازی CoinGecko و Standing"""
    if not check_admin_auth(request):
        return Response({'error': 'احراز هویت لازم است'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        import threading
        from datetime import timedelta
        
        # متغیرهای برای ذخیره نتایج و خطاها
        coingecko_error = None
        standing_error = None
        coingecko_completed = threading.Event()
        standing_completed = threading.Event()
        
        def update_coingecko():
            """به‌روزرسانی داده‌های CoinGecko"""
            nonlocal coingecko_error
            try:
                logger.info("🔄 Manual update: Starting CoinGecko update (parallel)...")
                coingecko_service = CoinGeckoService()
                coingecko_service.update_cryptocurrencies()
                logger.info("✅ Manual update: CoinGecko completed")
            except Exception as e:
                logger.error(f"❌ Manual update: CoinGecko error: {str(e)}")
                coingecko_error = str(e)
            finally:
                coingecko_completed.set()
        
        def update_standing():
            """به‌روزرسانی داده‌های Standing"""
            nonlocal standing_error
            try:
                logger.info("🔄 Manual update: Starting Standing update (parallel)...")
                success = StandingService.fetch_and_update_standing()
                if success:
                    logger.info("✅ Manual update: Standing completed")
                else:
                    logger.warning("⚠️ Manual update: Standing returned False")
                    standing_error = "Standing update failed"
            except Exception as e:
                logger.error(f"❌ Manual update: Standing error: {str(e)}")
                standing_error = str(e)
            finally:
                standing_completed.set()
        
        # اجرای موازی CoinGecko و Standing
        thread_coingecko = threading.Thread(target=update_coingecko, daemon=True)
        thread_standing = threading.Thread(target=update_standing, daemon=True)
        
        thread_coingecko.start()
        thread_standing.start()
        
        # انتظار برای اتمام هر دو thread
        thread_coingecko.join()
        thread_standing.join()
        
        # بررسی خطاها
        if coingecko_error:
            logger.error(f"Manual update: CoinGecko failed: {coingecko_error}")
        if standing_error:
            logger.warning(f"Manual update: Standing failed: {standing_error}")
        
        # به‌روزرسانی رتبه‌بندی (بعد از دریافت داده‌های CoinGecko)
        if not coingecko_error:
            try:
                logger.info("🔄 Manual update: Starting ranking update...")
                ranking_service = RankingService()
                ranking_service.update_rankings()
                logger.info("✅ Manual update: Ranking completed")
            except Exception as e:
                logger.error(f"❌ Manual update: Ranking error: {str(e)}")
        
        status_obj = MonitoringStatus.get_status()
        settings = Settings.get_settings()
        status_obj.last_update = timezone.now()
        
        # اگر پایش فعال است، زمان بروزرسانی بعدی را محاسبه کن
        if status_obj.is_running:
            status_obj.next_update = timezone.now() + timedelta(seconds=settings.update_interval)
        
        # اگر هر دو موفق بودند، خطا را پاک کن
        if not coingecko_error and not standing_error:
            status_obj.last_error = ''
        else:
            errors = []
            if coingecko_error:
                errors.append(f"CoinGecko: {coingecko_error}")
            if standing_error:
                errors.append(f"Standing: {standing_error}")
            status_obj.last_error = ' | '.join(errors)
        
        status_obj.save()
        
        # ساخت پیام پاسخ
        if coingecko_error and standing_error:
            message = f'خطا در به‌روزرسانی: CoinGecko: {coingecko_error}, Standing: {standing_error}'
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif coingecko_error:
            message = f'CoinGecko به‌روزرسانی نشد: {coingecko_error}'
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif standing_error:
            # اگر فقط standing خطا داشت، موفقیت نسبی برمی‌گردانیم
            return Response({
                'success': True,
                'message': f'داده‌های قیمت به‌روزرسانی شدند. خطا در standing: {standing_error}'
            })
        else:
            return Response({
                'success': True,
                'message': 'داده‌ها با موفقیت به‌روزرسانی شدند'
            })
            
    except Exception as e:
        logger.error(f"Error in manual update: {str(e)}")
        return Response({
            'success': False,
            'message': f'خطا در به‌روزرسانی: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def standing_proxy_view(request):
    """دریافت داده‌های standing ذخیره شده در دیتابیس با اطلاعات منبع"""
    try:
        from services.standing_service import StandingService, STANDING_API_URL_1
        from models.coin_models import SocialAPICache
        
        # دریافت اطلاعات cache برای API اول
        cache_obj = SocialAPICache.get_cache(STANDING_API_URL_1)
        source_info = {
            'api_url': STANDING_API_URL_1,
            'api_name': 'API اول (81.168.119.209)',
            'last_fetch': cache_obj.last_successful_request.isoformat() if cache_obj.last_successful_request else None,
            'from_cache': cache_obj.is_cache_valid() if cache_obj.last_successful_request else False
        }
        
        # تبدیل به فرمت مورد نیاز frontend
        indicators = []
        coins = Cryptocurrency.objects.exclude(standing__isnull=True).values('id', 'symbol', 'name', 'standing', 'last_updated')
        
        for coin in coins:
            indicators.append({
                'id': coin['id'],
                'symbol': coin['symbol'],
                'name': coin['name'],
                'standing': coin['standing'],
                'last_updated': coin['last_updated'].isoformat() if coin['last_updated'] else None
            })
        
        # سورت بر اساس standing (بزرگترین به کوچکترین)
        indicators.sort(key=lambda x: x['standing'] if x['standing'] is not None else -1, reverse=True)
        
        return Response({
            'indicators': indicators,
            'total': len(indicators),
            'timestamp': timezone.now().isoformat(),
            'source': source_info
        })
        
    except Exception as e:
        logger.error(f"Error in standing proxy: {str(e)}")
        return Response({
            'error': f'خطا در دریافت داده‌ها: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_standing_view(request):
    """به‌روزرسانی دستی داده‌های standing از API خارجی"""
    if not check_admin_auth(request):
        return Response({'error': 'احراز هویت لازم است'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        success = StandingService.fetch_and_update_standing()
        if success:
            return Response({
                'success': True,
                'message': 'داده‌های standing با موفقیت به‌روزرسانی شدند'
            })
        else:
            return Response({
                'success': False,
                'message': 'خطا در به‌روزرسانی داده‌های standing'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error updating standing: {str(e)}")
        return Response({
            'success': False,
            'message': f'خطا در به‌روزرسانی: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def fetch_social_data_view(request):
    """
    دریافت مستقیم داده‌های سوشال از هر دو API خارجی با cache و fallback
    - اگر یک API جواب نداد، از API بعدی استفاده می‌شود
    - هر یک ساعت یکبار فقط API‌هایی که پاسخ داده‌اند درخواست می‌شوند
    """
    try:
        from services.standing_service import (
            STANDING_API_URL_1, API_KEY_1,
            STANDING_API_URL_2, API_KEY_2,
            StandingService
        )
        from models.coin_models import SocialAPICache
        
        # دریافت پارامترهای query
        limit = int(request.GET.get('limit', 10000))
        offset = int(request.GET.get('offset', 0))
        symbol = request.GET.get('symbol', None)
        use_both = request.GET.get('use_both', 'true').lower() == 'true'
        force_refresh = request.GET.get('force_refresh', 'false').lower() == 'true'
        
        indicators_1 = None
        indicators_2 = None
        api1_from_cache = False
        api2_from_cache = False
        
        # بررسی cache برای API اول
        cache1 = SocialAPICache.get_cache(STANDING_API_URL_1)
        if not force_refresh and cache1.is_cache_valid() and cache1.cached_data:
            indicators_1 = cache1.cached_data
            api1_from_cache = True
            logger.info(f"Using cached data for API 1")
        else:
            # دریافت از API اول
            logger.info(f"Fetching from API 1: {STANDING_API_URL_1}")
            indicators_1 = StandingService.fetch_from_api(
                STANDING_API_URL_1, 
                API_KEY_1, 
                limit=limit, 
                offset=offset,
                use_cache=True
            )
        
        # دریافت از API دوم (اگر use_both=True باشد)
        if use_both:
            # بررسی cache برای API دوم
            cache2 = SocialAPICache.get_cache(STANDING_API_URL_2)
            if not force_refresh and cache2.is_cache_valid() and cache2.cached_data:
                indicators_2 = cache2.cached_data
                api2_from_cache = True
                logger.info(f"Using cached data for API 2")
            else:
                # دریافت از API دوم (فقط اگر API اول جواب نداد یا برای تکمیل)
                logger.info(f"Fetching from API 2: {STANDING_API_URL_2}")
                indicators_2 = StandingService.fetch_from_api(
                    STANDING_API_URL_2, 
                    API_KEY_2, 
                    limit=limit, 
                    offset=offset,
                    use_cache=True
                )
        
        # ترکیب داده‌ها
        indicators_list = []
        if indicators_1:
            indicators_list.append(indicators_1)
        if indicators_2:
            indicators_list.append(indicators_2)
        
        if not indicators_list:
            # اگر هیچ داده‌ای دریافت نشد، خطا برمی‌گردانیم
            return Response({
                'error': 'هیچ داده‌ای از API‌های خارجی دریافت نشد',
                'api1_status': 'success' if indicators_1 else 'failed',
                'api2_status': 'success' if indicators_2 else 'failed' if use_both else 'not_used'
            }, status=status.HTTP_502_BAD_GATEWAY)
        
        indicators = StandingService.merge_indicators(indicators_list)
        
        if not indicators:
            return Response({
                'error': 'هیچ داده‌ای پس از ترکیب دریافت نشد',
                'api1_status': 'success' if indicators_1 else 'failed',
                'api2_status': 'success' if indicators_2 else 'failed' if use_both else 'not_used'
            }, status=status.HTTP_502_BAD_GATEWAY)
        
        # فیلتر بر اساس symbol در صورت وجود
        if symbol:
            symbol_upper = symbol.upper()
            indicators = [ind for ind in indicators if ind.get('symbol', '').upper() == symbol_upper]
        
        # اطلاعات منبع و cache
        sources = []
        cache_info = {}
        if indicators_1:
            sources.append('api1')
            cache_info['api1'] = {
                'from_cache': api1_from_cache,
                'last_update': cache1.last_successful_request.isoformat() if cache1.last_successful_request else None
            }
        if indicators_2:
            sources.append('api2')
            cache_info['api2'] = {
                'from_cache': api2_from_cache,
                'last_update': cache2.last_successful_request.isoformat() if cache2.last_successful_request else None
            }
        
        return Response({
            'indicators': indicators,
            'total': len(indicators),
            'timestamp': timezone.now().isoformat(),
            'sources': sources,
            'api1_count': len(indicators_1) if indicators_1 else 0,
            'api2_count': len(indicators_2) if indicators_2 else 0,
            'merged_count': len(indicators),
            'cache_info': cache_info,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logger.error(f"Error fetching social data: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'error': f'خطا در دریافت داده‌های سوشال: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


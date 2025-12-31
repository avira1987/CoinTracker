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
from tasks.scheduler import get_scheduler
import logging

logger = logging.getLogger(__name__)


class CryptocurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet برای لیست کوین‌ها"""
    queryset = Cryptocurrency.objects.all().order_by('rank')
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
    """بررسی وضعیت احراز هویت"""
    return Response({
        'authenticated': True,
        'username': request.session.get('username', '')
    })


def check_admin_auth(request):
    """بررسی احراز هویت ادمین"""
    return request.session.get('authenticated', False)

@api_view(['GET', 'PUT'])
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
def start_monitoring_view(request):
    """شروع پایش"""
    if not check_admin_auth(request):
        return Response({'error': 'احراز هویت لازم است'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        scheduler = get_scheduler()
        scheduler.start_monitoring()
        
        status_obj = MonitoringStatus.get_status()
        status_obj.is_running = True
        status_obj.last_error = ''
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
def manual_update_view(request):
    """به‌روزرسانی دستی داده‌ها"""
    if not check_admin_auth(request):
        return Response({'error': 'احراز هویت لازم است'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        coingecko_service = CoinGeckoService()
        coingecko_service.update_cryptocurrencies()
        
        ranking_service = RankingService()
        ranking_service.update_rankings()
        
        status_obj = MonitoringStatus.get_status()
        status_obj.last_update = timezone.now()
        status_obj.save()
        
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


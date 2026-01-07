"""
URLs برای API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    CryptocurrencyViewSet,
    login_view,
    logout_view,
    check_auth,
    settings_view,
    monitoring_status_view,
    start_monitoring_view,
    stop_monitoring_view,
    manual_update_view,
    standing_proxy_view,
    update_standing_view,
    fetch_social_data_view,
)

router = DefaultRouter()
router.register(r'coins', CryptocurrencyViewSet, basename='coin')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/check/', check_auth, name='check-auth'),
    path('settings/', settings_view, name='settings'),
    path('monitoring/status/', monitoring_status_view, name='monitoring-status'),
    path('monitoring/start/', start_monitoring_view, name='monitoring-start'),
    path('monitoring/stop/', stop_monitoring_view, name='monitoring-stop'),
    path('monitoring/update/', manual_update_view, name='manual-update'),
    path('standing/', standing_proxy_view, name='standing-proxy'),
    path('standing/update/', update_standing_view, name='standing-update'),
    path('social/fetch/', fetch_social_data_view, name='fetch-social-data'),
]


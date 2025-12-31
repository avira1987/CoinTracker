from rest_framework import serializers
from models.coin_models import Cryptocurrency, Settings, MonitoringStatus


class CryptocurrencySerializer(serializers.ModelSerializer):
    """Serializer برای ارزهای دیجیتال"""
    rank_reason = serializers.SerializerMethodField()

    class Meta:
        model = Cryptocurrency
        fields = [
            'id', 'coin_id', 'name', 'symbol', 'current_price', 'market_cap',
            'volume_24h', 'price_change_1h', 'price_change_24h', 'price_change_7d',
            'volume_change_24h', 'rank', 'rank_score', 'last_updated', 'rank_reason'
        ]

    def get_rank_reason(self, obj):
        """توضیح دلیل رتبه‌بندی"""
        reasons = []
        
        if obj.price_change_24h > 5:
            reasons.append(f"تغییرات {obj.price_change_24h:.2f}% در قیمت طی 24 ساعت گذشته")
        elif obj.price_change_24h < -5:
            reasons.append(f"کاهش {abs(obj.price_change_24h):.2f}% در قیمت طی 24 ساعت گذشته")
        
        if obj.volume_change_24h > 50:
            reasons.append(f"حجم معاملات {obj.volume_change_24h:.2f}% افزایش یافته است")
        elif obj.volume_change_24h < -50:
            reasons.append(f"حجم معاملات {abs(obj.volume_change_24h):.2f}% کاهش یافته است")
        
        if obj.rank_score > 70:
            reasons.append("نوسانات قیمت پایدارتر از سایر کوین‌ها")
        
        if not reasons:
            reasons.append("رتبه‌بندی بر اساس معیارهای ترکیبی")
        
        return " | ".join(reasons)


class SettingsSerializer(serializers.ModelSerializer):
    """Serializer برای تنظیمات"""
    class Meta:
        model = Settings
        fields = [
            'api_key', 'top_coins_count', 'price_weight', 'volume_weight',
            'stability_weight', 'market_cap_weight', 'data_history_days',
            'update_interval', 'updated_at'
        ]


class MonitoringStatusSerializer(serializers.ModelSerializer):
    """Serializer برای وضعیت پایش"""
    class Meta:
        model = MonitoringStatus
        fields = ['is_running', 'last_update', 'next_update', 'last_error', 'updated_at']


class LoginSerializer(serializers.Serializer):
    """Serializer برای لاگین"""
    username = serializers.CharField()
    password = serializers.CharField()


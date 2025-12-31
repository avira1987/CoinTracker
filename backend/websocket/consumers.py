"""
WebSocket Consumers برای ارسال به‌روزرسانی‌های Real-time
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from models.coin_models import Cryptocurrency, MonitoringStatus, Settings
from api.serializers import CryptocurrencySerializer, MonitoringStatusSerializer
import asyncio


class CoinConsumer(AsyncWebsocketConsumer):
    """Consumer برای ارسال به‌روزرسانی‌های کوین‌ها"""

    async def connect(self):
        await self.accept()
        self.room_group_name = 'coin_updates'
        
        # اضافه کردن به گروه
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # ارسال داده اولیه
        await self.send_initial_data()

    async def disconnect(self, close_code):
        # حذف از گروه
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """دریافت پیام از کلاینت"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'get_coins':
                await self.send_initial_data()
            elif message_type == 'get_status':
                await self.send_status()
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_initial_data(self):
        """ارسال داده اولیه"""
        coins = await self.get_coins()
        status = await self.get_status()
        
        await self.send(text_data=json.dumps({
            'type': 'initial_data',
            'coins': coins,
            'status': status
        }))

    async def send_status(self):
        """ارسال وضعیت پایش"""
        status = await self.get_status()
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': status
        }))

    async def coin_update(self, event):
        """ارسال به‌روزرسانی کوین‌ها"""
        coins_data = await self.get_coins()
        await self.send(text_data=json.dumps({
            'type': 'coin_update',
            'coins': coins_data,
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))

    async def status_update(self, event):
        """ارسال به‌روزرسانی وضعیت"""
        status_data = await self.get_status()
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': status_data
        }))

    @database_sync_to_async
    def get_coins(self):
        """دریافت لیست کوین‌ها از دیتابیس"""
        settings = Settings.get_settings()
        coins = Cryptocurrency.objects.all().order_by('rank')[:settings.top_coins_count]
        serializer = CryptocurrencySerializer(coins, many=True)
        return serializer.data

    @database_sync_to_async
    def get_status(self):
        """دریافت وضعیت پایش از دیتابیس"""
        status_obj = MonitoringStatus.get_status()
        serializer = MonitoringStatusSerializer(status_obj)
        return serializer.data


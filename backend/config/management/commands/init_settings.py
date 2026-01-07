"""
دستور Django برای مقداردهی اولیه تنظیمات از settings.json
"""
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from models.coin_models import Settings


class Command(BaseCommand):
    help = 'مقداردهی اولیه تنظیمات از settings.json'

    def handle(self, *args, **options):
        settings_file = Path(__file__).resolve().parent.parent.parent.parent.parent / 'settings.json'
        
        if not settings_file.exists():
            self.stdout.write(self.style.WARNING(f'فایل {settings_file} یافت نشد'))
            return

        with open(settings_file, 'r', encoding='utf-8') as f:
            settings_data = json.load(f)

        settings = Settings.get_settings()
        settings.api_key = settings_data.get('coingecko_api_key', settings.api_key)
        settings.top_coins_count = settings_data.get('default_top_coins', settings.top_coins_count)
        
        weights = settings_data.get('default_weights', {})
        settings.price_weight = weights.get('price_change', settings.price_weight)
        settings.volume_weight = weights.get('volume_change', settings.volume_weight)
        settings.stability_weight = weights.get('stability', settings.stability_weight)
        settings.market_cap_weight = weights.get('market_cap', settings.market_cap_weight)
        settings.social_weight = weights.get('social', settings.social_weight)
        
        settings.data_history_days = settings_data.get('default_data_history_days', settings.data_history_days)
        settings.update_interval = settings_data.get('update_interval_seconds', settings.update_interval)
        
        settings.save()

        self.stdout.write(self.style.SUCCESS('تنظیمات با موفقیت بارگذاری شدند'))


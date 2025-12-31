from django.apps import AppConfig


class ConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'config'

    def ready(self):
        """مقداردهی اولیه تنظیمات هنگام راه‌اندازی"""
        try:
            import json
            from pathlib import Path
            from django.apps import apps
            
            settings_file = Path(__file__).resolve().parent.parent.parent / 'settings.json'
            
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)

                Settings = apps.get_model('models', 'Settings')
                settings = Settings.get_settings()
                
                # فقط در صورت خالی بودن فیلدها، از settings.json استفاده کن
                if not settings.api_key:
                    settings.api_key = settings_data.get('coingecko_api_key', '')
                
                if settings.top_coins_count == 100:  # مقدار پیش‌فرض
                    settings.top_coins_count = settings_data.get('default_top_coins', 100)
                
                weights = settings_data.get('default_weights', {})
                if settings.price_weight == 0.40:  # مقدار پیش‌فرض
                    settings.price_weight = weights.get('price_change', 0.40)
                    settings.volume_weight = weights.get('volume_change', 0.30)
                    settings.stability_weight = weights.get('stability', 0.20)
                    settings.market_cap_weight = weights.get('market_cap', 0.10)
                
                if settings.data_history_days == 7:  # مقدار پیش‌فرض
                    settings.data_history_days = settings_data.get('default_data_history_days', 7)
                
                if settings.update_interval == 60:  # مقدار پیش‌فرض
                    settings.update_interval = settings_data.get('update_interval_seconds', 60)
                
                settings.save()
        except Exception as e:
            # در صورت خطا، ادامه بده (ممکن است در migration اجرا شود)
            pass


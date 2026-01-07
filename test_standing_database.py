"""
تست نمایش داده‌های standing از دیتابیس
"""
import os
import sys
import django
import io

# تنظیم encoding برای Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# تنظیم Django
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from models.coin_models import Cryptocurrency
from services.standing_service import StandingService
from django.utils import timezone

def test_database_standing():
    """تست نمایش داده‌های standing از دیتابیس"""
    print("="*80)
    print("تست داده‌های Standing از دیتابیس")
    print("="*80)
    
    # بررسی تعداد کوین‌های با standing
    coins_with_standing = Cryptocurrency.objects.exclude(standing__isnull=True)
    total_coins = Cryptocurrency.objects.count()
    
    print(f"\n📊 آمار دیتابیس:")
    print(f"   تعداد کل کوین‌ها: {total_coins}")
    print(f"   تعداد کوین‌های با standing: {coins_with_standing.count()}")
    
    if coins_with_standing.exists():
        print(f"\n📋 نمونه داده‌های Standing در دیتابیس:")
        print(f"{'='*80}")
        print(f"{'ID':<6} {'Symbol':<10} {'Name':<25} {'Standing':<12}")
        print(f"{'-'*6} {'-'*10} {'-'*25} {'-'*12}")
        
        for coin in coins_with_standing[:20]:
            print(f"{coin.id:<6} {coin.symbol:<10} {coin.name[:23]:<25} {coin.standing:<12}")
        
        # آمار standing
        standings = [coin.standing for coin in coins_with_standing if coin.standing]
        if standings:
            print(f"\n📊 آمار Standing:")
            print(f"   حداقل: {min(standings)}")
            print(f"   حداکثر: {max(standings)}")
            print(f"   میانگین: {sum(standings) / len(standings):.2f}")
        
        # کوین‌های با standing بالا
        high_standing = coins_with_standing.filter(standing__gt=500).order_by('-standing')[:10]
        print(f"\n📈 کوین‌های با Standing بالا (>500):")
        for coin in high_standing:
            print(f"   {coin.symbol}: {coin.standing}")
    else:
        print(f"\n⚠️  هیچ داده‌ای در دیتابیس وجود ندارد")
        print(f"   در حال دریافت داده‌ها از API...")
        
        # دریافت داده‌ها از API
        success = StandingService.fetch_and_update_standing()
        if success:
            print(f"✅ داده‌ها با موفقیت دریافت و ذخیره شدند")
            # نمایش مجدد
            coins_with_standing = Cryptocurrency.objects.exclude(standing__isnull=True)
            print(f"\n📋 داده‌های Standing بعد از دریافت:")
            print(f"{'='*80}")
            print(f"{'ID':<6} {'Symbol':<10} {'Name':<25} {'Standing':<12}")
            print(f"{'-'*6} {'-'*10} {'-'*25} {'-'*12}")
            
            for coin in coins_with_standing[:20]:
                print(f"{coin.id:<6} {coin.symbol:<10} {coin.name[:23]:<25} {coin.standing:<12}")
        else:
            print(f"❌ خطا در دریافت داده‌ها از API")

def test_standing_service():
    """تست سرویس standing"""
    print("\n" + "="*80)
    print("تست سرویس Standing")
    print("="*80)
    
    print("\n🔄 در حال دریافت داده‌ها از API...")
    success = StandingService.fetch_and_update_standing()
    
    if success:
        print("✅ داده‌ها با موفقیت دریافت شدند")
        
        # دریافت Map
        standing_map = StandingService.get_standing_map()
        print(f"\n📊 Standing Map:")
        print(f"   تعداد entries: {len(standing_map)}")
        print(f"\n📋 نمونه داده‌ها:")
        for i, (symbol, standing) in enumerate(list(standing_map.items())[:10], 1):
            print(f"   {i}. {symbol}: {standing}")
    else:
        print("❌ خطا در دریافت داده‌ها")

def main():
    """اجرای تست‌ها"""
    print("\n" + "="*80)
    print("شروع تست‌های Standing Database")
    print("="*80)
    print(f"زمان: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # تست 1: نمایش داده‌های موجود در دیتابیس
    test_database_standing()
    
    # تست 2: تست سرویس
    test_standing_service()
    
    print("\n" + "="*80)
    print("تست‌ها کامل شد!")
    print("="*80)

if __name__ == "__main__":
    main()

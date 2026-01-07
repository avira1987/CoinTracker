"""
تست سرویس standing در backend
"""
import sys
import os
import django
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.standing_service import StandingService

def test_backend_standing():
    """تست سرویس standing"""
    print("=" * 60)
    print("تست سرویس Standing در Backend")
    print("=" * 60)
    
    try:
        print("در حال دریافت داده از API...")
        success = StandingService.fetch_and_update_standing()
        
        if success:
            print("✅ داده‌ها با موفقیت دریافت و به‌روزرسانی شدند!")
            
            # دریافت map از standing
            standing_map = StandingService.get_standing_map()
            print(f"\nتعداد کوین‌های دارای standing: {len(standing_map)}")
            
            if standing_map:
                print("\nنمونه داده‌ها:")
                sample_items = list(standing_map.items())[:5]
                for symbol, standing in sample_items:
                    print(f"  {symbol}: {standing}")
            
            print("\n✅ تست موفقیت‌آمیز بود!")
            return True
        else:
            print("❌ خطا در دریافت یا به‌روزرسانی داده‌ها")
            return False
            
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_backend_standing()
    exit(0 if success else 1)

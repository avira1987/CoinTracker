"""
تست ساده API بدون نیاز به Django test framework
برای تست سریع endpoint های API
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from models.coin_models import Settings, MonitoringStatus
import json

def test_endpoint(name, method, url_name=None, url_path=None, data=None):
    """تست یک endpoint"""
    print(f"\n{'='*60}")
    print(f"تست: {name}")
    print(f"{'='*60}")
    
    client = Client()
    
    try:
        if url_name:
            url = reverse(url_name)
        else:
            url = url_path
        
        if method == 'GET':
            response = client.get(url)
        elif method == 'POST':
            response = client.post(url, json.dumps(data) if data else None, content_type='application/json')
        elif method == 'PUT':
            response = client.put(url, json.dumps(data) if data else None, content_type='application/json')
        
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        
        try:
            response_data = json.loads(response.content)
            print(f"Response:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        except:
            print(f"Response (text): {response.content.decode('utf-8')}")
        
        if response.status_code in [200, 201]:
            print("✅ موفق")
            return True
        else:
            print(f"❌ خطا - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """اجرای تمام تست‌ها"""
    print("="*60)
    print("تست API های CoinTracker")
    print("="*60)
    
    # آماده‌سازی داده‌ها
    print("\nآماده‌سازی داده‌ها...")
    settings = Settings.get_settings()
    settings.top_coins_count = 10
    settings.update_interval = 60
    settings.save()
    
    status_obj = MonitoringStatus.get_status()
    status_obj.is_running = False
    status_obj.save()
    print("✅ داده‌ها آماده شدند")
    
    results = []
    
    # تست‌های GET
    results.append(("دریافت وضعیت پایش", test_endpoint(
        "دریافت وضعیت پایش",
        "GET",
        url_name='monitoring-status'
    )))
    
    results.append(("دریافت تنظیمات", test_endpoint(
        "دریافت تنظیمات",
        "GET",
        url_name='settings'
    )))
    
    # تست‌های POST
    results.append(("شروع پایش", test_endpoint(
        "شروع پایش",
        "POST",
        url_name='monitoring-start'
    )))
    
    results.append(("بررسی وضعیت بعد از شروع", test_endpoint(
        "بررسی وضعیت بعد از شروع",
        "GET",
        url_name='monitoring-status'
    )))
    
    results.append(("توقف پایش", test_endpoint(
        "توقف پایش",
        "POST",
        url_name='monitoring-stop'
    )))
    
    results.append(("بررسی وضعیت بعد از توقف", test_endpoint(
        "بررسی وضعیت بعد از توقف",
        "GET",
        url_name='monitoring-status'
    )))
    
    # خلاصه نتایج
    print("\n" + "="*60)
    print("خلاصه نتایج:")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ موفق" if result else "❌ ناموفق"
        print(f"{status}: {name}")
    
    print(f"\nنتیجه کلی: {passed}/{total} تست موفق")
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

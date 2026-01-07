"""
تست API endpoint برای standing
"""
import requests
import json
import sys
import io
from datetime import datetime

# تنظیم encoding برای Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# تنظیمات
BASE_URL = "http://87.107.108.95:8000"
API_KEY = "xl29bU5_kE8wfbEXY0w1Pyv-BpjGT3qzXwv7GEHkHqI"

def test_standing_endpoint(limit=10, offset=0, symbol=None):
    """تست endpoint standing"""
    print(f"\n{'='*70}")
    print(f"تست API Endpoint: /standing")
    print(f"{'='*70}")
    
    # ساخت URL با query parameters
    # امتحان هر دو مسیر ممکن
    url = f"{BASE_URL}/standing"
    # اگر این کار نکرد، می‌توانیم /api/standing را هم امتحان کنیم
    params = {}
    
    if limit:
        params['limit'] = limit
    if offset:
        params['offset'] = offset
    if symbol:
        params['symbol'] = symbol
    
    # هدرهای درخواست
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    print(f"\n📡 درخواست:")
    print(f"   URL: {url}")
    print(f"   Method: GET")
    print(f"   Query Parameters: {params}")
    print(f"   Headers: X-API-Key: {API_KEY[:20]}...")
    
    try:
        # ارسال درخواست
        response = requests.get(url, params=params, headers=headers, timeout=60)
        
        print(f"\n📥 پاسخ:")
        print(f"   Status Code: {response.status_code}")
        
        # بررسی وضعیت پاسخ
        if response.status_code == 200:
            try:
                data = response.json()
                
                # بررسی ساختار پاسخ
                print(f"\n✅ درخواست موفق!")
                
                # بررسی اینکه آیا داده‌ها در indicators هستند یا مستقیماً لیست هستند
                indicators = data.get('indicators', data) if isinstance(data, dict) else data
                total = data.get('total', len(indicators) if isinstance(indicators, list) else 0) if isinstance(data, dict) else len(data) if isinstance(data, list) else 0
                timestamp = data.get('timestamp', 'N/A') if isinstance(data, dict) else 'N/A'
                
                print(f"\n📊 اطلاعات دریافت شده:")
                print(f"   تعداد رکوردها: {len(indicators) if isinstance(indicators, list) else 0}")
                if isinstance(data, dict) and 'total' in data:
                    print(f"   کل رکوردها: {total}")
                if timestamp != 'N/A':
                    print(f"   زمان: {timestamp}")
                
                # نمایش داده‌ها
                if isinstance(indicators, list) and len(indicators) > 0:
                    print(f"\n{'='*70}")
                    print(f"جزئیات داده‌ها:")
                    print(f"{'='*70}")
                    
                    # نمایش هدر جدول
                    print(f"\n{'ID':<8} {'Symbol':<12} {'Name':<25} {'Standing':<12} {'Created At':<20}")
                    print(f"{'-'*8} {'-'*12} {'-'*25} {'-'*12} {'-'*20}")
                    
                    # نمایش هر رکورد
                    for item in indicators:
                        item_id = item.get('id', 'N/A')
                        item_symbol = item.get('symbol', 'N/A')
                        item_name = item.get('name', 'N/A')
                        item_standing = item.get('standing', 'N/A')
                        item_created_at = item.get('created_at', 'N/A')
                        
                        # فرمت کردن created_at اگر timestamp است
                        if isinstance(item_created_at, (int, float)):
                            try:
                                item_created_at = datetime.fromtimestamp(item_created_at).strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                pass
                        
                        print(f"{str(item_id):<8} {str(item_symbol):<12} {str(item_name)[:25]:<25} {str(item_standing):<12} {str(item_created_at):<20}")
                    
                    # نمایش JSON کامل
                    print(f"\n{'='*70}")
                    print(f"JSON کامل پاسخ:")
                    print(f"{'='*70}")
                    if isinstance(data, dict):
                        # نمایش فقط indicators برای خوانایی بهتر
                        print(json.dumps({'indicators': indicators, 'total': total, 'timestamp': timestamp}, indent=2, ensure_ascii=False))
                    else:
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                    # بررسی فیلدهای مورد نیاز
                    print(f"\n{'='*70}")
                    print(f"بررسی فیلدهای مورد نیاز:")
                    print(f"{'='*70}")
                    required_fields = ['id', 'symbol', 'name', 'standing', 'created_at']
                    first_item = indicators[0] if indicators else {}
                    
                    for field in required_fields:
                        if field in first_item:
                            print(f"   ✅ {field}: موجود")
                        else:
                            print(f"   ❌ {field}: موجود نیست")
                    
                elif isinstance(data, dict):
                    print(f"\n📄 پاسخ (Dictionary):")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                else:
                    print(f"\n⚠️  پاسخ خالی یا نامعتبر")
                    print(f"   نوع داده: {type(data)}")
                    print(f"   محتوا: {data}")
                
            except json.JSONDecodeError:
                print(f"\n❌ خطا: پاسخ JSON معتبر نیست")
                print(f"   محتوای پاسخ: {response.text[:500]}")
        else:
            print(f"\n❌ خطا: Status Code {response.status_code}")
            try:
                error_data = response.json()
                print(f"   پیام خطا:")
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print(f"   محتوای پاسخ: {response.text[:500]}")
        
        return response
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ خطا: اتصال به سرور برقرار نشد")
        print(f"   لطفاً مطمئن شوید که سرور در آدرس {BASE_URL} در حال اجرا است")
        return None
    except requests.exceptions.Timeout:
        print(f"\n❌ خطا: درخواست timeout شد")
        return None
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """اجرای تست‌ها"""
    print("="*70)
    print("تست API Endpoint: /standing")
    print("="*70)
    
    # تست 1: درخواست با limit=10
    print("\n" + "🔍 تست 1: درخواست با limit=10")
    test_standing_endpoint(limit=10)
    
    # تست 2: درخواست با limit=5
    print("\n" + "🔍 تست 2: درخواست با limit=5")
    test_standing_endpoint(limit=5)
    
    # تست 3: درخواست با offset
    print("\n" + "🔍 تست 3: درخواست با limit=5 و offset=5")
    test_standing_endpoint(limit=5, offset=5)
    
    print("\n" + "="*70)
    print("تست‌ها کامل شد!")
    print("="*70)


if __name__ == "__main__":
    main()

"""
تست سریع API standing
"""
import requests
import json
import sys
import io

# تنظیم encoding برای Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# تنظیمات
BASE_URL = "http://87.107.108.95:8000/standing"
API_KEY = "xl29bU5_kE8wfbEXY0w1Pyv-BpjGT3qzXwv7GEHkHqI"

def test_api():
    """تست API با فرمت ارائه شده"""
    print("="*80)
    print("تست API Standing با فرمت ارائه شده")
    print("="*80)
    print(f"\nBase URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:20]}...")
    
    # تست با limit=10
    print("\n" + "-"*80)
    print("تست: GET /standing?limit=10")
    print("-"*80)
    
    headers = {
        'X-API-Key': API_KEY
    }
    
    params = {
        'limit': 10
    }
    
    try:
        print(f"\n📡 ارسال درخواست...")
        print(f"   URL: {BASE_URL}")
        print(f"   Method: GET")
        print(f"   Headers: X-API-Key: {API_KEY[:20]}...")
        print(f"   Params: limit=10")
        
        response = requests.get(BASE_URL, headers=headers, params=params, timeout=90)
        
        print(f"\n📥 پاسخ:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ درخواست موفق!")
            print(f"\n📊 ساختار پاسخ:")
            print(f"   نوع: {type(data)}")
            
            if isinstance(data, dict):
                print(f"   کلیدها: {list(data.keys())}")
                
                indicators = data.get('indicators', [])
                total = data.get('total', 'N/A')
                timestamp = data.get('timestamp', 'N/A')
                
                print(f"\n📈 اطلاعات کلی:")
                print(f"   تعداد indicators: {len(indicators)}")
                print(f"   Total: {total}")
                print(f"   Timestamp: {timestamp}")
                
                if indicators:
                    print(f"\n📋 داده‌های دریافت شده (10 رکورد اول):")
                    print(f"{'='*80}")
                    print(f"{'ID':<6} {'Symbol':<10} {'Name':<25} {'Standing':<12} {'Created At':<25}")
                    print(f"{'-'*6} {'-'*10} {'-'*25} {'-'*12} {'-'*25}")
                    
                    for ind in indicators:
                        ind_id = ind.get('id', 'N/A')
                        symbol = ind.get('symbol', 'N/A')
                        name = ind.get('name', 'N/A')
                        standing = ind.get('standing', 'N/A')
                        created_at = ind.get('created_at', 'N/A')
                        
                        # کوتاه کردن
                        if len(name) > 23:
                            name = name[:20] + "..."
                        if len(str(created_at)) > 23:
                            created_at = str(created_at)[:20] + "..."
                        
                        print(f"{ind_id:<6} {symbol:<10} {name:<25} {standing:<12} {str(created_at):<25}")
                    
                    # بررسی فیلدهای مورد نیاز
                    print(f"\n✅ بررسی فیلدهای Response:")
                    first = indicators[0] if indicators else {}
                    required_fields = ['id', 'symbol', 'name', 'standing', 'created_at']
                    
                    for field in required_fields:
                        if field in first:
                            value = first[field]
                            print(f"   ✅ {field}: موجود (مثال: {value})")
                        else:
                            print(f"   ❌ {field}: موجود نیست")
                    
                    # نمایش JSON کامل برای یک رکورد
                    print(f"\n📄 JSON کامل یک رکورد نمونه:")
                    print(f"{'='*80}")
                    print(json.dumps(indicators[0], indent=2, ensure_ascii=False))
                    
            else:
                print(f"\n⚠️  پاسخ لیست است (نه dictionary)")
                print(f"   تعداد آیتم‌ها: {len(data) if isinstance(data, list) else 'N/A'}")
                if isinstance(data, list) and len(data) > 0:
                    print(f"\n📄 نمونه داده:")
                    print(json.dumps(data[0], indent=2, ensure_ascii=False))
            
            return True
        else:
            print(f"\n❌ خطا: Status Code {response.status_code}")
            print(f"   Response Text: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n❌ خطا: درخواست timeout شد (بیش از 30 ثانیه)")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ خطا: اتصال به سرور برقرار نشد")
        print(f"   لطفاً مطمئن شوید که API در دسترس است")
        return False
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api()
    print("\n" + "="*80)
    if success:
        print("✅ تست موفق بود!")
    else:
        print("❌ تست ناموفق بود!")
    print("="*80)
    sys.exit(0 if success else 1)

"""
اسکریپت تست دستی API برای CoinTracker
برای تست سریع endpoint های API
"""
import requests
import json

# تنظیمات
BASE_URL = "http://localhost:8000/api"

def test_endpoint(name, method, url, data=None):
    """تست یک endpoint"""
    print(f"\n{'='*50}")
    print(f"تست: {name}")
    print(f"Method: {method} | URL: {url}")
    print(f"{'='*50}")
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)
        
        if response.status_code in [200, 201]:
            print("✅ موفق")
        else:
            print("❌ خطا")
            
    except requests.exceptions.ConnectionError:
        print("❌ خطا: سرور در دسترس نیست. مطمئن شوید که backend در حال اجرا است.")
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
    
    return response.status_code if 'response' in locals() else None


def main():
    """اجرای تمام تست‌ها"""
    print("="*60)
    print("تست API های CoinTracker")
    print("="*60)
    
    # تست‌های GET
    test_endpoint(
        "دریافت وضعیت پایش",
        "GET",
        f"{BASE_URL}/monitoring/status/"
    )
    
    test_endpoint(
        "دریافت لیست کوین‌ها",
        "GET",
        f"{BASE_URL}/coins/"
    )
    
    test_endpoint(
        "دریافت تنظیمات",
        "GET",
        f"{BASE_URL}/settings/"
    )
    
    # تست‌های POST
    test_endpoint(
        "شروع پایش",
        "POST",
        f"{BASE_URL}/monitoring/start/"
    )
    
    test_endpoint(
        "بررسی وضعیت بعد از شروع",
        "GET",
        f"{BASE_URL}/monitoring/status/"
    )
    
    test_endpoint(
        "توقف پایش",
        "POST",
        f"{BASE_URL}/monitoring/stop/"
    )
    
    test_endpoint(
        "بررسی وضعیت بعد از توقف",
        "GET",
        f"{BASE_URL}/monitoring/status/"
    )
    
    print("\n" + "="*60)
    print("تست‌ها کامل شد!")
    print("="*60)


if __name__ == "__main__":
    main()

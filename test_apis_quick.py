"""
Quick test for Social APIs status
"""
import requests
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API 1
API1_URL = "http://81.168.119.209:8000/standing"
API1_KEY = "FOTHB4y_kZPc08eCcwdSe19bFdYEOGm51zuw6I8V-ek"

# API 2
API2_URL = "http://87.107.108.95:8000/standing"
API2_KEY = "xl29bU5_kE8wfbEXY0w1Pyv-BpjGT3qzXwv7GEHkHqI"

# Backend API
BACKEND_API_URL = "http://localhost:8000/api/social/fetch/"

def quick_test(api_url, api_key=None, api_name="API"):
    """Quick test for an API"""
    try:
        headers = {}
        if api_key:
            headers = {
                'X-API-Key': api_key,
                'Content-Type': 'application/json'
            }
        
        response = requests.get(api_url, headers=headers, params={'limit': 5}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            indicators = data.get('indicators', [])
            return True, len(indicators), None
        else:
            return False, 0, f"HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        return False, 0, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, 0, "Connection Error"
    except Exception as e:
        return False, 0, str(e)

def main():
    print("=" * 60)
    print("Social APIs Quick Test")
    print("=" * 60)
    
    # Test API 1
    print("\nTesting API 1...", end=" ")
    success1, count1, error1 = quick_test(API1_URL, API1_KEY, "API 1")
    if success1:
        print(f"OK ({count1} indicators)")
    else:
        print(f"FAILED: {error1}")
    
    # Test API 2
    print("Testing API 2...", end=" ")
    success2, count2, error2 = quick_test(API2_URL, API2_KEY, "API 2")
    if success2:
        print(f"OK ({count2} indicators)")
    else:
        print(f"FAILED: {error2}")
    
    # Test Backend API
    print("Testing Backend API...", end=" ")
    success3, count3, error3 = quick_test(BACKEND_API_URL, None, "Backend API")
    if success3:
        print(f"OK ({count3} indicators)")
    else:
        print(f"FAILED: {error3}")
        if "Connection Error" in error3:
            print("   Note: Make sure backend is running")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  API 1: {'OK' if success1 else 'FAILED'}")
    print(f"  API 2: {'OK' if success2 else 'FAILED'}")
    print(f"  Backend API: {'OK' if success3 else 'FAILED'}")
    
    all_ok = success1 and success2 and success3
    if all_ok:
        print("\nAll APIs are working!")
    else:
        print("\nSome APIs are not working!")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

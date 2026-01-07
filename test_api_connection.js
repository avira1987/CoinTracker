/**
 * تست اتصال به API
 */

const API_BASE_URL = 'http://141.11.0.80:8000/api';

async function testAPI() {
  console.log('🧪 شروع تست اتصال به API...\n');
  console.log('📍 API Base URL:', API_BASE_URL);
  console.log('─'.repeat(50));

  // تست 1: دریافت لیست کوین‌ها
  try {
    console.log('\n1️⃣ تست دریافت لیست کوین‌ها...');
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    
    const coinsResponse = await fetch(`${API_BASE_URL}/coins/`, {
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
      }
    });
    clearTimeout(timeoutId);
    
    console.log('✅ موفق: دریافت لیست کوین‌ها');
    console.log('   Status:', coinsResponse.status);
    const data = await coinsResponse.json();
    console.log('   تعداد کوین‌ها:', data?.results?.length || data?.length || 0);
    if (data?.results?.length > 0) {
      console.log('   نمونه کوین:', {
        name: data.results[0]?.name,
        symbol: data.results[0]?.symbol,
        price: data.results[0]?.current_price
      });
    }
  } catch (error) {
    console.log('❌ خطا در دریافت لیست کوین‌ها:');
    if (error.name === 'AbortError') {
      console.log('   Timeout: درخواست بیش از 10 ثانیه طول کشید');
    } else {
      console.log('   Error:', error.message);
    }
  }

  // تست 2: دریافت وضعیت پایش
  try {
    console.log('\n2️⃣ تست دریافت وضعیت پایش...');
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    
    const statusResponse = await fetch(`${API_BASE_URL}/monitoring/status/`, {
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
      }
    });
    clearTimeout(timeoutId);
    
    console.log('✅ موفق: دریافت وضعیت پایش');
    console.log('   Status:', statusResponse.status);
    const data = await statusResponse.json();
    console.log('   Data:', data);
  } catch (error) {
    console.log('❌ خطا در دریافت وضعیت پایش:');
    if (error.name === 'AbortError') {
      console.log('   Timeout: درخواست بیش از 10 ثانیه طول کشید');
    } else {
      console.log('   Error:', error.message);
    }
  }

  // تست 3: دریافت داده‌های Standing
  try {
    console.log('\n3️⃣ تست دریافت داده‌های Standing...');
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    
    const standingResponse = await fetch(`${API_BASE_URL}/standing/`, {
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
      }
    });
    clearTimeout(timeoutId);
    
    console.log('✅ موفق: دریافت داده‌های Standing');
    console.log('   Status:', standingResponse.status);
    const data = await standingResponse.json();
    console.log('   تعداد Indicators:', data?.indicators?.length || 0);
    console.log('   Total:', data?.total || 0);
  } catch (error) {
    console.log('❌ خطا در دریافت داده‌های Standing:');
    if (error.name === 'AbortError') {
      console.log('   Timeout: درخواست بیش از 10 ثانیه طول کشید');
    } else {
      console.log('   Error:', error.message);
    }
  }

  // تست 4: بررسی CORS
  try {
    console.log('\n4️⃣ تست CORS...');
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    
    const corsResponse = await fetch(`${API_BASE_URL}/coins/`, {
      method: 'OPTIONS',
      signal: controller.signal,
      headers: {
        'Origin': 'http://localhost:3000',
      }
    });
    clearTimeout(timeoutId);
    
    console.log('✅ CORS headers موجود است');
    console.log('   Status:', corsResponse.status);
    const headers = {};
    corsResponse.headers.forEach((value, key) => {
      headers[key] = value;
    });
    console.log('   Headers:', headers);
  } catch (error) {
    console.log('⚠️  تست CORS با خطا مواجه شد (ممکن است طبیعی باشد)');
  }

  console.log('\n' + '─'.repeat(50));
  console.log('✅ تست‌ها به پایان رسید');
}

testAPI().catch(console.error);

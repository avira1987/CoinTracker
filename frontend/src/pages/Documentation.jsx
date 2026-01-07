import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Documentation.css';

function Documentation() {
  const [activeSection, setActiveSection] = useState('intro');
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredSections, setFilteredSections] = useState([]);

  const sections = [
    { id: 'intro', title: 'معرفی پروژه', icon: '📘' },
    { id: 'architecture', title: 'معماری سیستم', icon: '🏗️' },
    { id: 'how-it-works', title: 'نحوه عملکرد', icon: '⚙️' },
    { id: 'api-structure', title: 'ساختار API', icon: '🔌' },
    { id: 'ranking-algorithm', title: 'الگوریتم رتبه‌بندی', icon: '📊' },
    { id: 'websocket', title: 'ارتباطات Real-Time', icon: '🔄' },
    { id: 'database', title: 'مدل‌های دیتابیس', icon: '💾' },
    { id: 'deployment', title: 'راه‌اندازی و استقرار', icon: '🚀' },
    { id: 'troubleshooting', title: 'رفع مشکلات', icon: '🔧' },
  ];

  useEffect(() => {
    if (searchTerm) {
      const filtered = sections.filter(section =>
        section.title.includes(searchTerm)
      );
      setFilteredSections(filtered);
    } else {
      setFilteredSections(sections);
    }
  }, [searchTerm]);

  const scrollToSection = (sectionId) => {
    setActiveSection(sectionId);
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="documentation-page" dir="rtl">
      <div className="doc-header">
        <div className="header-content">
          <Link to="/" className="back-button">
            ← بازگشت به داشبورد
          </Link>
          <h1>📚 مستندات کامل CoinTracker</h1>
          <p className="subtitle">راهنمای جامع سیستم رتبه‌بندی هوشمند ارزهای دیجیتال</p>
        </div>
      </div>

      <div className="doc-container">
        <aside className="doc-sidebar">
          <div className="search-box">
            <input
              type="text"
              placeholder="🔍 جستجو در مستندات..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <nav className="doc-nav">
            <h3>فهرست مطالب</h3>
            <ul>
              {filteredSections.map(section => (
                <li
                  key={section.id}
                  className={activeSection === section.id ? 'active' : ''}
                  onClick={() => scrollToSection(section.id)}
                >
                  <span className="nav-icon">{section.icon}</span>
                  {section.title}
                </li>
              ))}
            </ul>
          </nav>
          <div className="doc-actions">
            <a 
              href="/DOCUMENTATION_FA.md" 
              download 
              className="download-btn"
            >
              📥 دانلود PDF
            </a>
            <Link to="/tutorial" className="tutorial-btn">
              🎓 آموزش تصویری
            </Link>
          </div>
        </aside>

        <main className="doc-content">
          {/* معرفی پروژه */}
          <section id="intro" className="doc-section">
            <h2>📘 معرفی پروژه</h2>
            <div className="content-card">
              <p>
                <strong>CoinTracker</strong> یک سیستم هوشمند رتبه‌بندی ارزهای دیجیتال است که با استفاده از الگوریتم وزن‌دار پیشرفته، 
                ارزهای دیجیتال را بر اساس معیارهای مختلف رتبه‌بندی می‌کند.
              </p>

              <h3>ویژگی‌های کلیدی</h3>
              <ul className="feature-list">
                <li><strong>رتبه‌بندی دینامیک:</strong> الگوریتم وزن‌دار قابل تنظیم</li>
                <li><strong>به‌روزرسانی Real-Time:</strong> استفاده از WebSocket</li>
                <li><strong>رابط کاربری فارسی:</strong> پشتیبانی کامل از زبان فارسی</li>
                <li><strong>احراز هویت:</strong> سیستم Session-based Authentication</li>
                <li><strong>نظارت خودکار:</strong> شروع/توقف خودکار به‌روزرسانی‌ها</li>
                <li><strong>تنظیمات پیشرفته:</strong> قابلیت تنظیم وزن‌ها و پارامترها</li>
              </ul>

              <h3>تکنولوژی‌های استفاده شده</h3>
              <div className="tech-stack">
                <div className="tech-category">
                  <h4>Backend</h4>
                  <ul>
                    <li>Django 4.2</li>
                    <li>Django REST Framework</li>
                    <li>Django Channels</li>
                    <li>APScheduler</li>
                    <li>SQLite</li>
                    <li>Python 3.11+</li>
                  </ul>
                </div>
                <div className="tech-category">
                  <h4>Frontend</h4>
                  <ul>
                    <li>React 18</li>
                    <li>Vite</li>
                    <li>React Router</li>
                    <li>Axios</li>
                    <li>Reconnecting WebSocket</li>
                  </ul>
                </div>
                <div className="tech-category">
                  <h4>DevOps</h4>
                  <ul>
                    <li>Docker</li>
                    <li>Docker Compose</li>
                    <li>Nginx</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>

          {/* معماری سیستم */}
          <section id="architecture" className="doc-section">
            <h2>🏗️ معماری سیستم</h2>
            <div className="content-card">
              <h3>نمای کلی معماری</h3>
              <div className="architecture-diagram">
                <pre>{`
┌─────────────┐
│   کاربر     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Nginx    │ (Reverse Proxy)
└──────┬──────┘
       │
       ├─────────────────┬─────────────────┐
       ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   React     │   │   Django    │   │  WebSocket  │
│  Frontend   │   │   Backend   │   │   Server    │
└─────────────┘   └──────┬──────┘   └─────────────┘
                         │
                         ├─────────────┬─────────────┐
                         ▼             ▼             ▼
                  ┌─────────────┐ ┌──────────┐ ┌──────────┐
                  │  CoinGecko  │ │  SQLite  │ │ Standing │
                  │     API     │ │    DB    │ │   APIs   │
                  └─────────────┘ └──────────┘ └──────────┘
                `}</pre>
              </div>

              <h3>جریان داده (Data Flow)</h3>
              <ol className="flow-list">
                <li><strong>کاربر</strong> درخواست را به Nginx ارسال می‌کند</li>
                <li><strong>Nginx</strong> درخواست را به سرور مناسب (Frontend/Backend/WebSocket) هدایت می‌کند</li>
                <li><strong>Backend</strong> داده را از CoinGecko API و Standing APIs دریافت می‌کند</li>
                <li><strong>داده پردازش</strong> شده و در SQLite ذخیره می‌شود</li>
                <li><strong>الگوریتم رتبه‌بندی</strong> اجرا می‌شود</li>
                <li><strong>به‌روزرسانی‌ها</strong> از طریق WebSocket به تمام کلاینت‌ها ارسال می‌شود</li>
              </ol>
            </div>
          </section>

          {/* نحوه عملکرد */}
          <section id="how-it-works" className="doc-section">
            <h2>⚙️ نحوه عملکرد سیستم</h2>
            <div className="content-card">
              <h3>مرحله اول: دریافت داده</h3>
              <ul>
                <li>Scheduler هر 5 دقیقه (پیش‌فرض) اجرا می‌شود</li>
                <li>CoinGeckoService درخواست به API CoinGecko می‌فرستد</li>
                <li>داده‌های Top Coins دریافت می‌شود</li>
                <li>StandingService به APIهای خارجی Social Standing درخواست می‌فرستد</li>
                <li>داده‌های Standing (رتبه اجتماعی) دریافت و Cache می‌شود</li>
              </ul>

              <h3>مرحله دوم: پردازش و ذخیره‌سازی</h3>
              <ul>
                <li>برای هر Coin، اطلاعات تفصیلی دریافت می‌شود</li>
                <li>محاسبه Volume Change 24h</li>
                <li>ذخیره در مدل Cryptocurrency</li>
                <li>ذخیره تاریخچه در مدل PriceHistory</li>
              </ul>

              <h3>مرحله سوم: رتبه‌بندی</h3>
              <ul>
                <li>RankingService فعال می‌شود</li>
                <li>محاسبه Stability Score بر اساس تاریخچه</li>
                <li>نرمال‌سازی تمام معیارها (0-100)</li>
                <li>محاسبه Rank Score با فرمول وزن‌دار</li>
                <li>مرتب‌سازی و اختصاص رتبه</li>
              </ul>

              <h3>مرحله چهارم: انتشار</h3>
              <ul>
                <li>ذخیره در Database</li>
                <li>ارسال به تمام کلاینت‌های WebSocket متصل</li>
                <li>به‌روزرسانی UI به صورت Real-Time</li>
              </ul>
            </div>
          </section>

          {/* ساختار API */}
          <section id="api-structure" className="doc-section">
            <h2>🔌 ساختار درخواست‌های API</h2>
            <div className="content-card">
              <h3>Base URL</h3>
              <div className="code-block">
                <code>
                  توسعه: http://localhost:8000/api<br/>
                  تولید: http://your-domain.com/api
                </code>
              </div>

              <h3>احراز هویت (Authentication)</h3>
              <div className="api-example">
                <h4>ورود (Login)</h4>
                <div className="code-block">
                  <code>
                    POST /api/auth/login/<br/>
                    Content-Type: application/json<br/><br/>
                    {`{
  "username": "admin",
  "password": "admin123"
}`}
                  </code>
                </div>
              </div>

              <h3>Cryptocurrencies</h3>
              <div className="api-example">
                <h4>دریافت لیست ارزها</h4>
                <div className="code-block">
                  <code>
                    GET /api/cryptocurrencies/<br/>
                    Query Parameters:<br/>
                    - page: شماره صفحه (پیش‌فرض: 1)<br/>
                    - page_size: تعداد آیتم (پیش‌فرض: 50)
                  </code>
                </div>
              </div>

              <h3>Monitoring</h3>
              <div className="api-example">
                <h4>شروع نظارت</h4>
                <div className="code-block">
                  <code>POST /api/monitoring/start/</code>
                </div>
                <h4>توقف نظارت</h4>
                <div className="code-block">
                  <code>POST /api/monitoring/stop/</code>
                </div>
                <h4>به‌روزرسانی دستی</h4>
                <div className="code-block">
                  <code>POST /api/monitoring/manual-update/</code>
                </div>
              </div>

              <h3>Settings</h3>
              <div className="api-example">
                <h4>دریافت تنظیمات</h4>
                <div className="code-block">
                  <code>GET /api/settings/</code>
                </div>
                <h4>به‌روزرسانی تنظیمات</h4>
                <div className="code-block">
                  <code>
                    PUT /api/settings/<br/>
                    Content-Type: application/json<br/><br/>
                    {`{
  "top_coins_count": 150,
  "price_weight": 30.0,
  "volume_weight": 25.0
}`}
                  </code>
                </div>
              </div>
            </div>
          </section>

          {/* الگوریتم رتبه‌بندی */}
          <section id="ranking-algorithm" className="doc-section">
            <h2>📊 الگوریتم رتبه‌بندی</h2>
            <div className="content-card">
              <h3>فرمول کلی</h3>
              <div className="formula-box">
                <code>
                  Rank Score = (W₁ × Price Change) + (W₂ × Volume Change) + 
                  (W₃ × Stability) + (W₄ × Market Cap) + (W₅ × Social Standing)
                </code>
              </div>

              <h3>وزن‌های پیش‌فرض</h3>
              <ul className="weight-list">
                <li><strong>Price Change:</strong> 25%</li>
                <li><strong>Volume Change:</strong> 20%</li>
                <li><strong>Stability:</strong> 25%</li>
                <li><strong>Market Cap:</strong> 15%</li>
                <li><strong>Social Standing:</strong> 15%</li>
              </ul>

              <h3>محاسبه Stability Score</h3>
              <p>Stability Score یک معیار ترکیبی است که شامل:</p>
              <ul>
                <li><strong>Variance Score (40%):</strong> واریانس تغییرات قیمت 24 ساعته</li>
                <li><strong>Trend Consistency (30%):</strong> ثبات روند</li>
                <li><strong>Reversion Risk (30%):</strong> ریسک بازگشت قیمت</li>
              </ul>

              <div className="alert-info">
                <strong>💡 نکته:</strong> تمام معیارها به مقیاس 0-100 نرمال‌سازی می‌شوند تا وزن‌دهی منصفانه باشد.
              </div>
            </div>
          </section>

          {/* WebSocket */}
          <section id="websocket" className="doc-section">
            <h2>🔄 ارتباطات Real-Time</h2>
            <div className="content-card">
              <h3>اتصال به WebSocket</h3>
              <div className="code-block">
                <code>
                  {`const ws = new WebSocket('ws://localhost:8000/ws/coins/');

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  handleWebSocketMessage(data);
};`}
                </code>
              </div>

              <h3>انواع پیام‌های WebSocket</h3>
              <div className="message-types">
                <div className="message-type">
                  <h4>Coin Update</h4>
                  <p>به‌روزرسانی لیست ارزها</p>
                </div>
                <div className="message-type">
                  <h4>Status Update</h4>
                  <p>به‌روزرسانی وضعیت نظارت</p>
                </div>
                <div className="message-type">
                  <h4>Error</h4>
                  <p>اطلاع‌رسانی خطاها</p>
                </div>
              </div>
            </div>
          </section>

          {/* Database */}
          <section id="database" className="doc-section">
            <h2>💾 مدل‌های دیتابیس</h2>
            <div className="content-card">
              <h3>Cryptocurrency</h3>
              <p>ذخیره اطلاعات کامل هر ارز دیجیتال</p>
              <ul>
                <li>اطلاعات شناسایی: coin_id, symbol, name</li>
                <li>اطلاعات قیمت: current_price, price_change_24h, ...</li>
                <li>حجم معاملات: volume_24h, volume_change_24h</li>
                <li>رتبه‌بندی: rank, rank_score, standing</li>
              </ul>

              <h3>PriceHistory</h3>
              <p>ذخیره تاریخچه قیمت برای محاسبه ثبات</p>
              <ul>
                <li>price, volume</li>
                <li>price_change_24h</li>
                <li>timestamp</li>
              </ul>

              <h3>Settings</h3>
              <p>تنظیمات سیستم (Singleton)</p>
              <ul>
                <li>api_key</li>
                <li>top_coins_count, update_interval</li>
                <li>وزن‌های رتبه‌بندی</li>
              </ul>

              <h3>MonitoringStatus</h3>
              <p>وضعیت نظارت سیستم (Singleton)</p>
              <ul>
                <li>is_running</li>
                <li>last_update, last_error</li>
              </ul>

              <h3>SocialAPICache</h3>
              <p>Cache برای APIهای Standing</p>
              <ul>
                <li>api_url</li>
                <li>cached_data</li>
                <li>last_successful_request</li>
              </ul>
            </div>
          </section>

          {/* راه‌اندازی */}
          <section id="deployment" className="doc-section">
            <h2>🚀 راه‌اندازی و استقرار</h2>
            <div className="content-card">
              <h3>نصب با Docker (توصیه شده)</h3>
              <div className="code-block">
                <code>
                  {`# Clone repository
git clone https://github.com/yourusername/CoinTracker.git
cd CoinTracker

# ساخت و اجرای containers
docker-compose up --build

# دسترسی
# Frontend: http://localhost
# Backend API: http://localhost/api
# WebSocket: ws://localhost/ws`}
                </code>
              </div>

              <h3>نصب Local</h3>
              <h4>Backend</h4>
              <div className="code-block">
                <code>
                  {`cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py init_settings
python manage.py runserver`}
                </code>
              </div>

              <h4>Frontend</h4>
              <div className="code-block">
                <code>
                  {`cd frontend
npm install
npm run dev`}
                </code>
              </div>

              <div className="alert-warning">
                <strong>⚠️ توجه:</strong> قبل از اجرا، فایل settings.json را با API Key خود تنظیم کنید.
              </div>
            </div>
          </section>

          {/* رفع مشکلات */}
          <section id="troubleshooting" className="doc-section">
            <h2>🔧 رفع مشکلات</h2>
            <div className="content-card">
              <h3>مشکلات رایج و راه‌حل‌ها</h3>
              
              <div className="troubleshoot-item">
                <h4>WebSocket قطع می‌شود</h4>
                <p><strong>راه‌حل:</strong> از ReconnectingWebSocket استفاده کنید</p>
              </div>

              <div className="troubleshoot-item">
                <h4>خطای CORS</h4>
                <p><strong>راه‌حل:</strong> CORS_ALLOWED_ORIGINS را در settings.py تنظیم کنید</p>
              </div>

              <div className="troubleshoot-item">
                <h4>Rate Limit در CoinGecko API</h4>
                <p><strong>راه‌حل:</strong> از API Key استفاده کنید یا update_interval را افزایش دهید</p>
              </div>

              <div className="troubleshoot-item">
                <h4>دیتابیس خالی است</h4>
                <p><strong>راه‌حل:</strong> به‌روزرسانی دستی را اجرا کنید</p>
                <div className="code-block">
                  <code>curl -X POST http://localhost:8000/api/monitoring/manual-update/</code>
                </div>
              </div>

              <div className="troubleshoot-item">
                <h4>Scheduler متوقف شده</h4>
                <p><strong>راه‌حل:</strong> Scheduler را از طریق Django shell ری‌استارت کنید</p>
              </div>
            </div>
          </section>

          {/* پایان */}
          <section className="doc-section">
            <div className="content-card footer-card">
              <h3>📞 تماس و پشتیبانی</h3>
              <p>برای سوالات و پشتیبانی:</p>
              <ul>
                <li><strong>GitHub:</strong> <a href="https://github.com/yourusername/CoinTracker">Repository Link</a></li>
                <li><strong>Email:</strong> support@cointracker.com</li>
              </ul>
              <hr/>
              <p className="version-info">
                <strong>نسخه:</strong> 1.0.0 | <strong>آخرین به‌روزرسانی:</strong> 7 ژانویه 2025
              </p>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default Documentation;

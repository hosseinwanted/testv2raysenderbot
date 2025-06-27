import requests
import os
import time

# --- تنظیمات اصلی ---
# این مقادیر از GitHub Secrets خوانده می‌شوند
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# آدرس فایل حاوی پروکسی‌ها
PROXIES_URL = "https://raw.githubusercontent.com/MhdiTaheri/ProxyCollector/main/proxy.txt"

# آدرس API تلگرام
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# فایلی برای ذخیره محتوای آخرین لیست پروکسی ارسال شده برای جلوگیری از ارسال تکراری
LAST_CONTENT_FILE = "last_content.txt"

def fetch_proxies():
    """پروکسی‌ها را از آدرس مشخص شده دریافت می‌کند."""
    try:
        response = requests.get(PROXIES_URL, timeout=10)
        response.raise_for_status()  # بررسی وضعیت پاسخ HTTP
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching proxies: {e}")
        return None

def get_last_content():
    """محتوای آخرین ارسال موفق را از فایل می‌خواند."""
    if os.path.exists(LAST_CONTENT_FILE):
        with open(LAST_CONTENT_FILE, "r") as f:
            return f.read()
    return ""

def save_last_content(content):
    """محتوای جدید را در فایل ذخیره می‌کند."""
    with open(LAST_CONTENT_FILE, "w") as f:
        f.write(content)

def send_to_telegram(proxies_text):
    """پروکسی‌ها را به کانال تلگرام ارسال می‌کند."""
    # تقسیم پروکسی‌ها به دسته‌های کوچکتر برای جلوگیری از طولانی شدن پیام
    proxies_list = proxies_text.strip().split("\n")
    # می‌توانید چند پروکسی برتر را انتخاب کنید یا همه را بفرستید
    # در اینجا ۱۰ پروکسی اول را انتخاب می‌کنیم
    message_text = "✅ چند پروکسی جدید و فعال:\n\n" + "\n".join(proxies_list[:10])
    
    payload = {
        'chat_id': CHAT_ID,
        'text': message_text,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(TELEGRAM_API_URL, data=payload, timeout=10)
        response.raise_for_status()
        print("Proxies sent successfully to Telegram.")
        return True
    except requests.RequestException as e:
        print(f"Error sending to Telegram: {e}")
        # در صورت خطا، محتوای پاسخ را نمایش بده تا بهتر دیباگ کنی
        if e.response:
            print(f"Telegram API Response: {e.response.text}")
        return False

if __name__ == "__main__":
    print("Starting proxy collector bot...")
    
    new_proxies = fetch_proxies()
    
    if new_proxies:
        last_content = get_last_content()
        
        # فقط در صورتی ارسال کن که محتوای جدید با محتوای قبلی متفاوت باشد
        if new_proxies != last_content:
            print("New proxies found. Sending to Telegram...")
            if send_to_telegram(new_proxies):
                # اگر ارسال موفق بود، محتوای جدید را ذخیره کن
                save_last_content(new_proxies)
        else:
            print("No new proxies found. Skipping.")
    else:
        print("Failed to fetch proxies. Exiting.")

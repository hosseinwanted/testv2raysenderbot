import requests
import os
import random

# --- تنظیمات اصلی ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
PROXIES_URL = "https://raw.githubusercontent.com/MhdiTaheri/ProxyCollector/main/proxy.txt"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# --- تنظیمات حافظه ربات ---
RECENT_PROXIES_FILE = "recent_proxies.txt"  # نام فایل حافظه
MEMORY_SIZE = 50  # تعداد پروکسی‌هایی که در حافظه می‌ماند

def fetch_proxies():
    """لیست کامل پروکسی‌ها را از منبع دریافت می‌کند."""
    try:
        response = requests.get(PROXIES_URL, timeout=15)
        response.raise_for_status()
        proxies = [line for line in response.text.strip().split('\n') if '://' in line]
        return proxies
    except requests.RequestException as e:
        print(f"Error fetching proxies: {e}")
        return []

def get_recent_proxies():
    """پروکسی‌های اخیر را از فایل حافظه می‌خواند."""
    if not os.path.exists(RECENT_PROXIES_FILE):
        return []
    with open(RECENT_PROXIES_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def save_recent_proxies(proxies):
    """لیست جدید حافظه را در فایل ذخیره می‌کند."""
    with open(RECENT_PROXIES_FILE, "w") as f:
        f.write("\n".join(proxies))
    print(f"Saved {len(proxies)} recent proxies to memory.")

def send_single_proxy(proxy):
    """یک پروکسی را به تلگرام ارسال می‌کند."""
    message_text = (
        f"✅ <b>Smart-Random Proxy</b>\n\n"
        f"<code>{proxy}</code>\n\n"
        f"#proxy #smart_random"
    )
    payload = {'chat_id': CHAT_ID, 'text': message_text, 'parse_mode': 'HTML'}
    try:
        response = requests.post(TELEGRAM_API_URL, data=payload, timeout=10)
        response.raise_for_status()
        print(f"Successfully sent proxy: {proxy[:30]}...")
        return True
    except requests.RequestException as e:
        print(f"Error sending to Telegram: {e}")
        if e.response: print(f"Telegram API Response: {e.response.text}")
        return False

if __name__ == "__main__":
    all_proxies = fetch_proxies()
    if not all_proxies:
        print("No proxies found. Exiting.")
    else:
        recent_proxies = get_recent_proxies()
        
        # ایجاد لیستی از پروکسی‌های جدید که اخیرا ارسال نشده‌اند
        available_proxies = [p for p in all_proxies if p not in recent_proxies]
        
        # اگر هیچ پروکسی جدیدی نبود، حافظه را نادیده بگیر تا ربات متوقف نشود
        if not available_proxies:
            print("All available proxies have been sent recently. Resetting memory for this run.")
            available_proxies = all_proxies

        # انتخاب یک پروکسی تصادفی از لیست موجود
        chosen_proxy = random.choice(available_proxies)
        
        print("Sending a non-repeating random proxy...")
        if send_single_proxy(chosen_proxy):
            # اگر ارسال موفق بود، پروکسی جدید را به حافظه اضافه کن
            recent_proxies.append(chosen_proxy)
            
            # حافظه را به‌روز کن و فقط 50 تای آخر را نگه دار
            updated_memory = recent_proxies[-MEMORY_SIZE:]
            
            # لیست جدید حافظه را ذخیره کن
            save_recent_proxies(updated_memory)

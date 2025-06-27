import requests
import os

# --- تنظیمات اصلی ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
PROXIES_URL = "https://raw.githubusercontent.com/MhdiTaheri/ProxyCollector/main/proxy.txt"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# فایلی برای ذخیره شماره ردیف (ایندکس) آخرین پروکسی ارسال شده
STATE_FILE = "state.txt"

def fetch_proxies():
    """لیست کامل پروکسی‌ها را دریافت می‌کند."""
    try:
        response = requests.get(PROXIES_URL, timeout=15)
        response.raise_for_status()
        # فقط خطوطی که با 'ss://', 'vmess://', 'trojan://' و ... شروع می‌شوند را نگه دار
        proxies = [line for line in response.text.strip().split('\n') if '://' in line]
        return proxies
    except requests.RequestException as e:
        print(f"Error fetching proxies: {e}")
        return []

def get_last_index():
    """شماره ردیف آخرین پروکسی ارسال شده را از فایل می‌خواند."""
    if not os.path.exists(STATE_FILE):
        return -1  # اگر فایل وجود نداشت، از اول شروع کن
    try:
        with open(STATE_FILE, "r") as f:
            return int(f.read().strip())
    except (ValueError, FileNotFoundError):
        return -1 # اگر فایل خالی یا خراب بود، از اول شروع کن

def save_next_index(index):
    """شماره ردیف جدید را در فایل ذخیره می‌کند."""
    with open(STATE_FILE, "w") as f:
        f.write(str(index))
    print(f"Saved next index for next run: {index}")


def send_single_proxy(proxy):
    """یک پروکسی مشخص را به تلگرام ارسال می‌کند."""
    message_text = (
        f"✅ **New Proxy**\n\n"
        f"`{proxy}`\n\n"
        f"#proxy"
    )
    
    payload = {
        'chat_id': CHAT_ID,
        'text': message_text,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(TELEGRAM_API_URL, data=payload, timeout=10)
        response.raise_for_status()
        print(f"Successfully sent proxy: {proxy[:30]}...")
        return True
    except requests.RequestException as e:
        print(f"Error sending to Telegram: {e}")
        if e.response:
            print(f"Telegram API Response: {e.response.text}")
        return False

if __name__ == "__main__":
    proxies_list = fetch_proxies()
    
    if not proxies_list:
        print("No proxies found or failed to fetch. Exiting.")
    else:
        last_index = get_last_index()
        print(f"Last sent index was: {last_index}")
        
        # محاسبه ایندکس بعدی و چرخیدن به اول لیست در صورت رسیدن به انتها
        next_index = (last_index + 1) % len(proxies_list)
        print(f"Calculated next index: {next_index}")
        
        proxy_to_send = proxies_list[next_index]
        
        if send_single_proxy(proxy_to_send):
            # فقط در صورت ارسال موفق، ایندکس را برای دفعه بعد ذخیره کن
            save_next_index(next_index)

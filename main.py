import requests
import os
import random
import json

# --- تنظیمات اصلی ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
PROXIES_URL = "https://raw.githubusercontent.com/MhdiTaheri/ProxyCollector/main/proxy.txt"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
SENTENCES_FILE = "sentences.txt" # فایل جملات

# !!! مهم: لینک کانال‌های خود را اینجا وارد کنید !!!
TELEGRAM_PROXY_CHANNEL_URL = "https://t.me/YourTelegramProxyChannel" # لینک کانال پروکسی تلگرام
V2RAY_CHANNEL_URL = "https://t.me/YourV2rayChannel" # لینک کانال V2ray

def fetch_data(url):
    """یک تابع عمومی برای دریافت اطلاعات از یک آدرس"""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text.strip().split('\n')
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return []

def send_message_with_layout(sentence, proxies_list):
    """
    یک پیام با ساختار جدید (جمله + دکمه‌های چند ردیفی) ارسال می‌کند.
    """
    # --- ساخت دکمه‌ها ---
    # ردیف اول: ۳ دکمه برای پروکسی‌ها
    proxy_buttons = []
    for i, proxy_link in enumerate(proxies_list):
        proxy_buttons.append({"text": f"✅ Proxy {i + 1}", "url": proxy_link})

    # ردیف دوم: ۲ دکمه ثابت برای لینک کانال‌ها
    channel_buttons = [
        {"text": "🚀 کانال پروکسی تلگرام", "url": TELEGRAM_PROXY_CHANNEL_URL},
        {"text": "⚡️ کانال V2ray رایگان", "url": V2RAY_CHANNEL_URL}
    ]
    
    # ترکیب ردیف‌ها برای ساخت کیبورد نهایی
    keyboard = [
        proxy_buttons,    # ردیف اول
        channel_buttons   # ردیف دوم
    ]
    
    reply_markup = {"inline_keyboard": keyboard}

    # استفاده از جمله تصادفی به عنوان متن اصلی پیام
    message_text = sentence

    payload = {
        'chat_id': CHAT_ID,
        'text': message_text,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps(reply_markup)
    }
    
    try:
        response = requests.post(TELEGRAM_API_URL, data=payload, timeout=10)
        response.raise_for_status()
        print("Successfully sent the new layout message.")
        return True
    except requests.RequestException as e:
        print(f"Error sending message to Telegram: {e}")
        if e.response: print(f"Telegram API Response: {e.response.text}")
        return False

# --- منطق اصلی برنامه ---
if __name__ == "__main__":
    # ۱. یک جمله تصادفی انتخاب کن
    sentences = fetch_data(SENTENCES_FILE)
    if not sentences:
        # اگر فایلی نبود، از یک جمله پیش‌فرض استفاده کن
        chosen_sentence = "بهترین راه برای پیش‌بینی آینده، ساختن آن است."
    else:
        chosen_sentence = random.choice(sentences)
    
    # ۲. سه پروکسی تصادفی انتخاب کن
    all_proxies = [line for line in fetch_data(PROXIES_URL) if '://' in line]
    if len(all_proxies) < 3:
        print("Not enough proxies found to send. Exiting.")
    else:
        selected_proxies = random.sample(all_proxies, 3)
        
        # ۳. پیام را با ساختار جدید ارسال کن
        send_message_with_layout(chosen_sentence, selected_proxies)

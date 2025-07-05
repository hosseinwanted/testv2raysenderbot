import requests
import os
import random
import json
import jdatetime
from datetime import datetime, timezone, timedelta # وارد کردن کتابخانه استاندارد زمان

# --- تنظیمات اصلی ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
PROXIES_URL = "https://raw.githubusercontent.com/MhdiTaheri/ProxyCollector/main/proxy.txt"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
SENTENCES_FILE = "sentences.txt"

# --- خواندن امن کلیدهای API ناوید از سکرت گیت‌هاب ---
api_keys_str = os.environ.get("NAVASAN_API_KEYS", "")
API_KEYS = [key.strip() for key in api_keys_str.split('\n') if key.strip()]

PRICE_API_URL = "http://api.navasan.tech/latest/?api_key={}"

# !!! مهم: لینک کانال‌های خود را اینجا وارد کنید !!!
TELEGRAM_PROXY_CHANNEL_URL = "https://t.me/YourTelegramProxyChannel"
V2RAY_CHANNEL_URL = "https://t.me/YourV2rayChannel"


def format_number(value):
    """اعداد را به صورت سه‌رقم سه‌رقم با کاما جدا می‌کند."""
    try:
        numeric_value = int(float(str(value).replace(',', '')))
        return f"{numeric_value:,}"
    except (ValueError, TypeError):
        return value

def get_prices_from_api():
    """قیمت‌ها را از API سایت Navasan با استفاده از یک کلید تصادفی می‌خواند."""
    try:
        if not API_KEYS:
            raise ValueError("NAVASAN_API_KEYS secret is not set or is empty.")

        print("Fetching currency prices from Navasan JSON API...")
        random_api_key = random.choice(API_KEYS)
        url = PRICE_API_URL.format(random_api_key)
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        prices = {
            'usd': data.get('usd_sell', {}).get('value', 'N/A'),
            'eur': data.get('eur', {}).get('value', 'N/A'),
            'sekeh': data.get('sekkeh', {}).get('value', 'N/A'),
            '18ayar': data.get('18ayar', {}).get('value', 'N/A'),
            'usdt': data.get('usdt', {}).get('value', 'N/A')
        }
        
        print(f"Prices fetched successfully: {prices}")
        return prices
    except Exception as e:
        print(f"An exception occurred in get_prices_from_api: {e}")
        return None

def fetch_list_from_file(filename):
    """اطلاعات را از یک فایل محلی می‌خواند."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Warning: Could not read file {filename}: {e}")
        return []

def send_final_message(sentence, prices, proxies_list, time_str):
    """پیام نهایی و ترکیبی را با قالب هوشمند و مقاوم ارسال می‌کند."""
    price_items = []
    if prices:
        sekeh_raw = prices.get('sekeh', 'N/A')
        sekeh_corrected = sekeh_raw
        try:
            numeric_sekeh = int(float(str(sekeh_raw).replace(',', '')))
            if 0 < numeric_sekeh < 1000000:
                sekeh_corrected = numeric_sekeh * 1000
            else:
                sekeh_corrected = numeric_sekeh
        except (ValueError, TypeError):
            sekeh_corrected = sekeh_raw

        price_items.append(f"💵 دلار: <code>{format_number(prices.get('usd', 'N/A'))}</code>")
        price_items.append(f"🇪🇺 یورو: <code>{format_number(prices.get('eur', 'N/A'))}</code>")
        price_items.append(f"🪙 سکه: <code>{format_number(sekeh_corrected)}</code>")
        price_items.append(f"🌟 طلا ۱۸: <code>{format_number(prices.get('18ayar', 'N/A'))}</code>")
        price_items.append(f"₮ تتر: <code>{format_number(prices.get('usdt', 'N/A'))}</code>")
        
        price_line = " | ".join(price_items)
        price_section = f"📊 <b>آخرین قیمت‌ها:</b>\n{price_line}"
    else:
        price_section = "📊 در حال حاضر قیمت‌ها در دسترس نیستند."
        
    proxy_buttons = [{"text": f"✅ Proxy {i + 1}", "url": p} for i, p in enumerate(proxies_list)]
    channel_buttons = [
        {"text": "🚀 کانال پروکسی تلگرام", "url": TELEGRAM_PROXY_CHANNEL_URL},
        {"text": "⚡️ کانال V2ray رایگان", "url": V2RAY_CHANNEL_URL}
    ]
    keyboard = [proxy_buttons, channel_buttons]
    reply_markup = json.dumps({"inline_keyboard": keyboard})

    message_text = (
        f"{sentence}\n\n"
        f"{price_section}\n"
        f"📅 {time_str}\n\n"
        f"👇 برای اتصال، یکی از سرورهای زیر را انتخاب کنید:"
    )
    
    payload = {'chat_id': CHAT_ID, 'text': message_text, 'parse_mode': 'HTML', 'reply_markup': reply_markup}
    
    requests.post(TELEGRAM_API_URL, data=payload, timeout=10)
    print("Final combined message sent to Telegram.")


if __name__ == "__main__":
    # --- بخش اصلاح شده برای مدیریت زمان ---
    # ۱. گرفتن زمان فعلی به وقت جهانی (UTC) با استفاده از کتابخانه استاندارد
    now_utc = datetime.now(timezone.utc)
    
    # ۲. تعریف منطقه زمانی تهران (۳:۳۰+ از UTC)
    tehran_tz = timezone(timedelta(hours=3, minutes=30))
    
    # ۳. تبدیل زمان UTC به زمان تهران
    now_tehran_gregorian = now_utc.astimezone(tehran_tz)
    
    # ۴. تبدیل زمان میلادی تهران به زمان جلالی (شمسی)
    now_jalali = jdatetime.datetime.fromgregorian(datetime=now_tehran_gregorian)
    
    # ۵. فرمت کردن تاریخ و ساعت شمسی برای نمایش
    current_time_str = now_jalali.strftime("%Y/%m/%d - %H:%M")
    # --- پایان بخش اصلاح شده ---

    sentences = fetch_list_from_file(SENTENCES_FILE)
    chosen_sentence = random.choice(sentences) if sentences else "موفقیت، نتیجه‌ی تلاش‌های کوچک و روزمره است."

    current_prices = get_prices_from_api()

    try:
        proxies_text = requests.get(PROXIES_URL, timeout=15).text
        all_proxies = [p for p in proxies_text.strip().split('\n') if '://' in p]
        
        if len(all_proxies) >= 3:
            selected_proxies = random.sample(all_proxies, 3)
            # ارسال زمان فرمت‌شده به تابع ارسال پیام
            send_final_message(chosen_sentence, current_prices, selected_proxies, current_time_str)
        else:
            print("Not enough proxies found to send.")
    except Exception as e:
        print(f"Failed to fetch proxies: {e}")

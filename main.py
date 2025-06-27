import requests
import os
import random
import json

# --- تنظیمات اصلی ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
PROXIES_URL = "https://raw.githubusercontent.com/MhdiTaheri/ProxyCollector/main/proxy.txt"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
SENTENCES_FILE = "sentences.txt"

api_keys_str = os.environ.get("NAVASAN_API_KEYS", "")
API_KEYS = [key.strip() for key in api_keys_str.split('\n') if key.strip()]
PRICE_API_URL = "http://api.navasan.tech/latest/?api_key={}"

TELEGRAM_PROXY_CHANNEL_URL = "https://t.me/YourTelegramProxyChannel"
V2RAY_CHANNEL_URL = "https://t.me/YourV2rayChannel"

# --- تابع جدید برای قالب‌بندی اعداد ---
def format_number(value):
    """اعداد را به صورت سه‌رقم سه‌رقم با کاما جدا می‌کند."""
    try:
        # ابتدا هرگونه کاما را حذف کرده و به عدد تبدیل می‌کنیم
        numeric_value = int(float(str(value).replace(',', '')))
        # سپس با فرمت جدید برمی‌گردانیم
        return f"{numeric_value:,}"
    except (ValueError, TypeError):
        # اگر مقدار ورودی عدد نبود (مثلا N/A)، همان را برگردان
        return value

def get_prices_from_api():
    """قیمت ۵ دارایی محبوب را از API جدید Navasan می‌خواند."""
    try:
        if not API_KEYS:
            raise ValueError("NAVASAN_API_KEYS secret is not set or is empty.")

        print("Fetching popular assets from Navasan JSON API...")
        random_api_key = random.choice(API_KEYS)
        url = PRICE_API_URL.format(random_api_key)
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # استخراج ۵ دارایی محبوب
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
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Warning: Could not read file {filename}: {e}")
        return []

def send_final_message(sentence, prices, proxies_list):
    """پیام نهایی و ترکیبی را با قالب جدید ارسال می‌کند."""
    price_items = []
    if prices:
        # استفاده از تابع format_number برای هر قیمت
        price_items.append(f"💵 دلار: <code>{format_number(prices.get('usd'))}</code>")
        price_items.append(f"🇪🇺 یورو: <code>{format_number(prices.get('eur'))}</code>")
        price_items.append(f"🪙 سکه: <code>{format_number(prices.get('sekeh'))}</code>")
        price_items.append(f"🌟 طلا ۱۸: <code>{format_number(prices.get('18ayar'))}</code>")
        price_items.append(f"₮ تتر: <code>{format_number(prices.get('usdt'))}</code>")
        
        # ترکیب همه موارد در یک خط با جداکننده
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
        f"{price_section}\n\n"
        f"👇 برای اتصال، یکی از سرورهای زیر را انتخاب کنید:"
    )

    payload = {'chat_id': CHAT_ID, 'text': message_text, 'parse_mode': 'HTML', 'reply_markup': reply_markup}
    
    requests.post(TELEGRAM_API_URL, data=payload, timeout=10)
    print("Final combined message sent to Telegram.")


if __name__ == "__main__":
    sentences = fetch_list_from_file(SENTENCES_FILE)
    chosen_sentence = random.choice(sentences) if sentences else "موفقیت، نتیجه‌ی تلاش‌های کوچک و روزمره است."

    current_prices = get_prices_from_api()

    try:
        proxies_text = requests.get(PROXIES_URL, timeout=15).text
        all_proxies = [p for p in proxies_text.strip().split('\n') if '://' in p]
        
        if len(all_proxies) >= 3:
            selected_proxies = random.sample(all_proxies, 3)
            send_final_message(chosen_sentence, current_prices, selected_proxies)
        else:
            print("Not enough proxies found to send.")
    except Exception as e:
        print(f"Failed to fetch proxies: {e}")

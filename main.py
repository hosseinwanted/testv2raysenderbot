import requests
import os
import random
import json
import codecs # کتابخانه کمکی برای پردازش متن
from bs4 import BeautifulSoup

# --- تنظیمات اصلی ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
PROXIES_URL = "https://raw.githubusercontent.com/MhdiTaheri/ProxyCollector/main/proxy.txt"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
SENTENCES_FILE = "sentences.txt"

# --- آدرس جدید و بهینه برای قیمت‌ها ---
# ما فقط ارزهایی را درخواست می‌کنیم که نیاز داریم تا سرعت بالاتر برود
PRICE_API_URL = "https://www.navasan.tech/wp-navasan.php?usd&eur&sekkeh"

# !!! مهم: لینک کانال‌های خود را اینجا وارد کنید !!!
TELEGRAM_PROXY_CHANNEL_URL = "https://t.me/YourTelegramProxyChannel"
V2RAY_CHANNEL_URL = "https://t.me/YourV2rayChannel"

def fetch_list_from_file(filename):
    """اطلاعات را از یک فایل محلی می‌خواند."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return []

def get_prices_from_api():
    """قیمت‌ها را از API غیررسمی Navasan می‌خواند و خطایابی بهتری دارد."""
    prices = {}
    try:
        print("Fetching currency prices from Navasan API...")
        url = "https://www.navasan.tech/wp-navasan.php?usd&eur&sekkeh"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        raw_js = response.text
        start = raw_js.find("('\"") + 3
        end = raw_js.rfind("\"')")
        if start == 2 or end == -1:
            raise ValueError("Could not find the start/end pattern in the JS response.")
            
        html_escaped_string = raw_js[start:end]
        
        # --- بخش اصلاح شده برای رفع خطا ---
        # اگر رشته با یک بک‌اسلش تنها تمام شده بود، آن را حذف کن
        if html_escaped_string.endswith('\\'):
            html_escaped_string = html_escaped_string[:-1]
        # --- پایان بخش اصلاح شده ---

        html_string = codecs.decode(html_escaped_string, 'unicode_escape')
        soup = BeautifulSoup(html_string, 'lxml')
        
        targets = {'usd': "tr#usd", 'eur': "tr#eur", 'sekeh': "tr#sekkeh"}
        for name, selector in targets.items():
            element = soup.select_one(f"{selector} > td.val")
            if element:
                prices[name] = element.text.strip()
            else:
                print(f"Warning: Could not find the element for '{name}'.")
                prices[name] = "N/A"
        
        if all(value == "N/A" for value in prices.values()):
             raise ValueError("Failed to extract any prices. HTML structure likely changed.")

        print(f"Prices fetched successfully: {prices}")
        return prices
    except Exception as e:
        print(f"An exception occurred in get_prices_from_api: {e}")
        return None

def send_final_message(sentence, prices, proxies_list):
    """پیام نهایی و ترکیبی را ارسال می‌کند."""
    # بخش قیمت‌ها
    price_text = "📊 **آخرین نرخ ارز و طلا:**\n\n"
    if prices:
        # استفاده از تگ <code> برای نمایش بهتر اعداد
        price_text += (
            f"💵 دلار آمریکا: <code>{prices.get('usd', 'N/A')}</code>\n"
            f"🇪🇺 یورو: <code>{prices.get('eur', 'N/A')}</code>\n"
            f"🪙 سکه امامی: <code>{prices.get('sekeh', 'N/A')}</code>"
        )
    else:
        price_text += "در حال حاضر قیمت‌ها در دسترس نیستند."
        
    # بخش دکمه‌ها
    proxy_buttons = [{"text": f"✅ Proxy {i + 1}", "url": p} for i, p in enumerate(proxies_list)]
    channel_buttons = [
        {"text": "🚀 کانال پروکسی تلگرام", "url": TELEGRAM_PROXY_CHANNEL_URL},
        {"text": "⚡️ کانال V2ray رایگان", "url": V2RAY_CHANNEL_URL}
    ]
    keyboard = [proxy_buttons, channel_buttons]
    reply_markup = json.dumps({"inline_keyboard": keyboard})

    # ترکیب نهایی پیام
    message_text = (
        f"{sentence}\n\n"
        f"------------------------------\n"
        f"{price_text}\n\n"
        f"👇 برای اتصال، یکی از سرورهای زیر را انتخاب کنید:"
    )

    payload = {'chat_id': CHAT_ID, 'text': message_text, 'parse_mode': 'HTML', 'reply_markup': reply_markup}
    
    requests.post(TELEGRAM_API_URL, data=payload, timeout=10)
    print("Final combined message sent to Telegram.")

# --- منطق اصلی برنامه ---
if __name__ == "__main__":
    # ۱. خواندن جملات
    sentences = fetch_list_from_file(SENTENCES_FILE)
    chosen_sentence = random.choice(sentences) if sentences else "موفقیت، نتیجه‌ی تلاش‌های کوچک و روزمره است."

    # ۲. دریافت قیمت‌ها از API جدید
    current_prices = get_prices_from_api()

    # ۳. دریافت پروکسی‌ها
    try:
        proxies_text = requests.get(PROXIES_URL, timeout=15).text
        all_proxies = [p for p in proxies_text.strip().split('\n') if '://' in p]
        
        if len(all_proxies) >= 3:
            selected_proxies = random.sample(all_proxies, 3)
            # ۴. ارسال پیام نهایی
            send_final_message(chosen_sentence, current_prices, selected_proxies)
        else:
            print("Not enough proxies found.")
    except Exception as e:
        print(f"Failed to fetch proxies: {e}")

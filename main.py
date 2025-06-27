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

# --- تنظیمات API جدید BrsApi ---
# خواندن کلیدها از سکرت گیت‌هاب
api_keys_str = os.environ.get("BRS_API_KEY", "")
API_KEYS = [key.strip() for key in api_keys_str.split('\n') if key.strip()]
PRICE_API_URL = f"https://BrsApi.ir/Api/Market/Gold_Currency.php?key={{}}"

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
    """قیمت‌ها را از BrsApi.ir با یک کلید تصادفی می‌خواند."""
    try:
        if not API_KEYS:
            raise ValueError("BRS_API_KEY secret is not set or is empty.")

        print("Fetching prices from BrsApi.ir...")
        random_api_key = random.choice(API_KEYS)
        url = PRICE_API_URL.format(random_api_key)
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        api_data = response.json()
        
        prices = {}
        # نمادهای مورد نظر ما برای استخراج
        target_symbols = {"USD": "usd", "EUR": "eur", "IR_COIN_EMAMI": "sekeh", "IR_GOLD_18": "18ayar", "USDT": "usdt"}
        
        for item in api_data:
            if item['symbol'] in target_symbols:
                key = target_symbols[item['symbol']]
                # قیمت به تومان است (بر اساس مستندات)
                prices[key] = item['price']

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
    """پیام نهایی و ترکیبی را با قالب بهینه ارسال می‌کند."""
    price_items = []
    if prices:
        price_items.append(f"💵 دلار: <code>{format_number(prices.get('usd', 'N/A'))}</code>")
        price_items.append(f"🇪🇺 یورو: <code>{format_number(prices.get('eur', 'N/A'))}</code>")
        price_items.append(f"🪙 سکه: <code>{format_number(prices.get('sekeh', 'N/A'))}</code>")
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

    message_text = (f"{sentence}\n\n{price_section}\n\n👇 برای اتصال، یکی از سرورهای زیر را انتخاب کنید:")
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

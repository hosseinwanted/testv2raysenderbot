import requests
import os
import random
import json

# --- تنظیمات اصلی ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
BRS_API_KEY_STR = os.environ.get("BRS_API_KEY", "")
API_KEYS = [key.strip() for key in BRS_API_KEY_STR.split('\n') if key.strip()]
PRICE_API_URL = f"https://BrsApi.ir/Api/Market/Gold_Currency.php?key={{}}"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def get_prices_for_final_debug():
    """
    تلاش برای دریافت قیمت و برگرداندن اطلاعات کامل خطا در صورت شکست.
    """
    result = {"prices": None, "error": "Unknown error"}
    try:
        if not API_KEYS:
            raise ValueError("BRS_API_KEY secret is not set or is empty.")

        random_api_key = random.choice(API_KEYS)
        url = PRICE_API_URL.format(random_api_key)
        
        print(f"Attempting to connect to: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        result["prices"] = response.json()
        result["error"] = None # No error
        print("Successfully fetched data from BrsApi.")

    except requests.exceptions.RequestException as e:
        # ثبت دقیق خطای شبکه
        error_message = f"Network Error: {type(e).__name__} - {e}"
        result["error"] = error_message
        print(error_message)
    except Exception as e:
        # ثبت سایر خطاها
        error_message = f"A general error occurred: {type(e).__name__} - {e}"
        result["error"] = error_message
        print(error_message)
        
    return result

def send_debug_message(price_result):
    """یک پیام اشکال‌یابی به تلگرام ارسال می‌کند."""
    # اگر موفق بودیم، یک پیام موفقیت کوتاه بفرست
    if price_result["prices"]:
        message_text = "✅ **تست موفقیت‌آمیز بود!**\n\nربات توانست به API متصل شده و اطلاعات را دریافت کند. لطفاً کد نهایی را جایگزین کنید."
    # اگر شکست خوردیم، پیام خطا را بفرست
    else:
        message_text = (
            f"❌ **تست ناموفق بود!**\n\n"
            f"ربات نتوانست از سرور گیت‌هاب به API متصل شود.\n\n"
            f"**متن دقیق خطا:**\n`{price_result['error']}`\n\n"
            f"این خطا به احتمال زیاد به دلیل مسدود بودن IPهای گیت‌هاب توسط سایت مقصد است."
        )
    
    payload = {'chat_id': CHAT_ID, 'text': message_text, 'parse_mode': 'HTML'}
    requests.post(TELEGRAM_API_URL, data=payload)
    print("Debug message sent to Telegram.")

# --- منطق اصلی برنامه ---
if __name__ == "__main__":
    price_data = get_prices_for_final_debug()
    send_debug_message(price_data)

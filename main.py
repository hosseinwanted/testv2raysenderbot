import requests
import os
import random
import json
import codecs
from bs4 import BeautifulSoup

# --- تنظیمات اصلی (بدون تغییر) ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
PRICE_API_URL = "https://www.navasan.tech/wp-navasan.php?usd&eur&sekkeh"

def debug_navasan_response():
    """
    یک تابع اشکال‌یابی برای دیدن خروجی خام از API قیمت.
    """
    try:
        print("--- STARTING DEBUG RUN ---")
        print(f"Fetching data from: {PRICE_API_URL}")
        
        response = requests.get(PRICE_API_URL, timeout=15)
        response.raise_for_status()
        
        # --- بخش کلیدی: چاپ کردن خروجی خام ---
        print("\n\n--- RAW RESPONSE FROM NAVASAN.TECH ---")
        print(response.text)
        print("--- END OF RAW RESPONSE ---\n\n")
        # --- پایان بخش کلیدی ---
        
    except Exception as e:
        print(f"An error occurred during the debug run: {e}")

# --- منطق اصلی برنامه ---
if __name__ == "__main__":
    # در این نسخه، فقط تابع اشکال‌یابی را اجرا می‌کنیم
    debug_navasan_response()
    
    # برای جلوگیری از ارسال پیام خالی به تلگرام، بقیه کد را موقتا غیرفعال می‌کنیم
    print("Debug run finished. No message will be sent to Telegram.")

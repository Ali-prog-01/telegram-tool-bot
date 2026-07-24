"""
این اسکریپت رو فقط یه‌بار (بعد از بالا اومدن سایتتون رو PythonAnywhere) اجرا کنید
تا به تلگرام بگید پیام‌ها رو به کدوم آدرس بفرسته.

نحوه‌ی اجرا (تو کنسول Bash پایتون‌anywhere یا هر جای دیگه):
    python set_webhook.py https://yourusername.pythonanywhere.com

توجه: آدرس رو بدون اسلش (/) در انتهاش وارد کنید.
"""
import sys
import httpx
from config import BOT_TOKEN

if len(sys.argv) < 2:
    print("استفاده: python set_webhook.py https://yourusername.pythonanywhere.com")
    sys.exit(1)

base_url = sys.argv[1].rstrip("/")
webhook_url = f"{base_url}/{BOT_TOKEN}"

resp = httpx.get(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    params={"url": webhook_url},
)
print(resp.json())

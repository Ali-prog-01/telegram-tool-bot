"""
این فایل مخصوص هاست PythonAnywhere هست.

چرا این فایل جدا لازمه؟
پلن رایگان PythonAnywhere فقط اجازه‌ی اجرای یه «وب‌اپ» (WSGI) رو می‌ده، نه یه
اسکریپت پایتون که همیشه در پس‌زمینه با polling در حال اجراست (اون قابلیت
"Always-on tasks" هست که فقط تو پلن‌های پولی موجوده).

پس این‌جا به‌جای polling، ربات رو با webhook اجرا می‌کنیم: تلگرام هر پیام جدید
رو مستقیم به این آدرس POST می‌کنه، و ما همون‌جا پردازشش می‌کنیم.

نحوه‌ی استفاده تو پنل PythonAnywhere (بخش Web):
  - Source code / Working directory: مسیر همین پروژه
  - WSGI configuration file: محتوای همین فایل باید توش کپی بشه (یا ازش import کنید)
  - متغیر محیطی BOT_TOKEN رو تو تب "Web" > "Environment variables" ست کنید.
"""

import asyncio
import logging

from flask import Flask, request
from telegram import Update

from config import BOT_TOKEN
from main import build_application

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# اپلیکیشن تلگرام رو یه‌بار در زمان بالا اومدن سرور می‌سازیم (نه هر بار درخواست)
telegram_app = build_application()

# یه event loop اختصاصی می‌سازیم که در طول عمر پردازش زنده می‌مونه
_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)
_loop.run_until_complete(telegram_app.initialize())

# JobQueue (برای یادآوری‌ها) رو دستی استارت می‌کنیم، چون از run_webhook استفاده نمی‌کنیم
if telegram_app.job_queue:
    telegram_app.job_queue.start()
    from handlers.reminders import reschedule_pending_reminders
    reschedule_pending_reminders(telegram_app)


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    _loop.run_until_complete(telegram_app.process_update(update))
    return "OK"


@app.route("/", methods=["GET"])
def index():
    # صفحه‌ی ساده برای تست اینکه سرویس بالاست
    return "ربات تلگرام روشنه ✅"


# --- برای PythonAnywhere: این خط رو در فایل WSGI Configuration خودشون
# import کنید (جزئیات کامل در README) ---
application = app

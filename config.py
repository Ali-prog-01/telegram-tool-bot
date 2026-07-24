import os

# توکن ربات رو از متغیر محیطی می‌خونیم (هرگز مستقیم توی کد ننویس!)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# مسیر فایل دیتابیس (برای یادآوری‌ها)
DB_PATH = os.environ.get("DB_PATH", "bot_data.db")

# حداکثر حجم فایلی که پردازش می‌کنیم (به مگابایت) - برای اینکه روی پلن رایگان
# با کمبود RAM/دیسک مواجه نشیم
MAX_FILE_SIZE_MB = 15

# آیا قابلیت حذف پس‌زمینه (rembg) فعال باشه؟
# این کتابخونه حجیمه و RAM زیادی می‌خواد (حدود ۵۰۰ مگ به بالا) که ممکنه
# روی پلن‌های رایگان (مثلاً Render Free با ۵۱۲ مگ رم) مشکل ایجاد کنه.
# اگه سرورت محدودیت رم داره، این رو False کن.
ENABLE_REMOVE_BG = os.environ.get("ENABLE_REMOVE_BG", "true").lower() == "true"

# تنظیمات برای Webhook (در صورت نیاز) - اگه خالی باشه، ربات با polling کار می‌کنه
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
PORT = int(os.environ.get("PORT", "8080"))

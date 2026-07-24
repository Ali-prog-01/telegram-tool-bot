import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import BOT_TOKEN, WEBHOOK_URL, PORT
import database as db

from handlers.start import start_command, help_command
from handlers.qr_tool import qr_command
from handlers.image_tools import photo_received, image_action_callback
from handlers.pdf_tools import (
    img2pdf_start,
    img2pdf_done,
    collect_photo_for_pdf,
    pdf_to_images,
)
from handlers.zip_tools import zip_start, zip_done, collect_file_for_zip
from handlers.text_tools import shorten_command, password_command
from handlers.weather import weather_command
from handlers.reminders import (
    remind_command,
    list_reminders_command,
    delete_reminder_command,
    reschedule_pending_reminders,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def any_photo_router(update, context):
    """چون هم برای PDF و هم برای ابزار تصویر از عکس استفاده می‌کنیم،
    اول چک می‌کنیم آیا در حالت جمع‌آوری PDF هستیم یا نه."""
    if context.user_data.get("collecting_pdf"):
        await collect_photo_for_pdf(update, context)
    else:
        await photo_received(update, context)


async def any_document_router(update, context):
    """فایل‌های سندی می‌تونن عکس، PDF یا برای zip باشن."""
    doc = update.message.document
    if context.user_data.get("collecting_zip"):
        await collect_file_for_zip(update, context)
        return
    if doc and doc.mime_type == "application/pdf":
        await pdf_to_images(update, context)
        return
    if context.user_data.get("collecting_pdf") and doc and doc.mime_type and \
            doc.mime_type.startswith("image/"):
        await collect_photo_for_pdf(update, context)
        return
    if doc and doc.mime_type and doc.mime_type.startswith("image/"):
        await photo_received(update, context)


def build_application():
    """اپلیکیشن تلگرام رو می‌سازه و همه‌ی هندلرها رو ثبت می‌کنه.
    این تابع جدا از main() هست تا هم اجرای مستقیم (main.py) و هم
    آداپتورهای دیگه (مثل flask_app.py برای PythonAnywhere) بتونن ازش استفاده کنن،
    بدون اینکه polling یا webhook رو خودشون استارت کنن."""
    if not BOT_TOKEN:
        raise RuntimeError(
            "متغیر محیطی BOT_TOKEN تنظیم نشده. توکن ربات رو از @BotFather بگیر و ست کن."
        )

    db.init_db()

    application = Application.builder().token(BOT_TOKEN).build()

    # --- دستورات عمومی ---
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # --- ابزار تصویر ---
    application.add_handler(CommandHandler("qr", qr_command))
    application.add_handler(CallbackQueryHandler(image_action_callback, pattern=r"^img_"))

    # --- ابزار PDF / ZIP ---
    application.add_handler(CommandHandler("img2pdf", img2pdf_start))
    application.add_handler(CommandHandler("done", img2pdf_done))
    application.add_handler(CommandHandler("zip", zip_start))
    application.add_handler(CommandHandler("donezip", zip_done))

    # --- روتر عکس و فایل (بعد از دستورات بالا ثبت می‌شه) ---
    application.add_handler(MessageHandler(filters.PHOTO, any_photo_router))
    application.add_handler(MessageHandler(filters.Document.ALL, any_document_router))

    # --- متن و لینک ---
    application.add_handler(CommandHandler("shorten", shorten_command))
    application.add_handler(CommandHandler("password", password_command))

    # --- آب‌وهوا ---
    application.add_handler(CommandHandler("weather", weather_command))

    # --- یادآوری ---
    application.add_handler(CommandHandler("remind", remind_command))
    application.add_handler(CommandHandler("reminders", list_reminders_command))
    application.add_handler(CommandHandler("delremind", delete_reminder_command))

    return application


def main():
    application = build_application()

    # زمان‌بندی مجدد یادآوری‌های قبلی (برای وقتی سرور ری‌استارت شده)
    application.job_queue.run_once(
        lambda ctx: reschedule_pending_reminders(application), when=1
    )

    if WEBHOOK_URL:
        logger.info("در حال اجرا با Webhook...")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
        )
    else:
        logger.info("در حال اجرا با Polling...")
        application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()

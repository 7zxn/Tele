import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from rembg import remove
from PIL import Image
import io

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# إدخال رمز API الخاص ببوت تيليجرام الخاص بك هنا
TOKEN = "8110491548:AAGDKO0IgOEFtoMBlbLH31YQXXUJ3bsX-BI"

# وظيفة لبدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إرسال رسالة عندما يتم إرسال الأمر /start."""
    await update.message.reply_text(
        "مرحبًا! أنا بوت إزالة خلفية الصور. ما عليك سوى إرسال صورة وسأقوم بإزالة خلفيتها."
    )

# وظيفة للتعامل مع الصور وإزالة الخلفية
async def remove_background(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إزالة خلفية الصورة المرسلة."""
    # تحقق مما إذا كانت الرسالة تحتوي على صورة
    if not update.message.photo:
        await update.message.reply_text("يرجى إرسال صورة.")
        return

    # إرسال رسالة لإخبار المستخدم أن العملية قيد التقدم
    processing_message = await update.message.reply_text("جاري معالجة الصورة...")

    try:
        # الحصول على معرف الملف للصورة بأعلى دقة
        file_id = update.message.photo[-1].file_id

        # تنزيل الصورة
        file = await context.bot.get_file(file_id)
        input_image_bytes = await file.download_as_bytearray()

        # تحويل البيانات الثنائية إلى كائن صورة
        input_image = Image.open(io.BytesIO(input_image_bytes))

        # إزالة الخلفية باستخدام rembg
        output_image = remove(input_image)

        # حفظ الصورة في ذاكرة مؤقتة
        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format='PNG')
        output_buffer.seek(0)

        # إرسال الصورة المعالجة للمستخدم
        await update.message.reply_photo(
            photo=output_buffer,
            caption="تم إزالة الخلفية!"
        )

        # حذف رسالة المعالجة
        await processing_message.delete()

    except Exception as e:
        # في حالة حدوث خطأ، إبلاغ المستخدم
        await processing_message.edit_text(f"حدث خطأ أثناء معالجة الصورة: {str(e)}")
        logging.error(f"Error processing image: {str(e)}")

# وظيفة للرد على الرسائل غير المعروفة
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إرسال رسالة عندما يتم إرسال الأمر /help."""
    await update.message.reply_text("أرسل لي صورة وسأقوم بإزالة خلفيتها.")

# وظيفة للرد على الرسائل غير المعروفة
async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """الرد على الرسائل غير المعروفة."""
    await update.message.reply_text(
        "آسف، لا أفهم هذا الأمر. يرجى إرسال صورة أو استخدام الأمر /help للحصول على المساعدة."
    )

def main() -> None:
    """بدء تشغيل البوت."""
    # إنشاء التطبيق وتمرير رمز API الخاص بالبوت
    application = Application.builder().token(TOKEN).build()

    # على أوامر مختلفة
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # على رسائل الصور
    application.add_handler(MessageHandler(filters.PHOTO, remove_background))

    # التعامل مع جميع الرسائل الأخرى
    application.add_handler(MessageHandler(filters.ALL, unknown_message))

    # بدء البوت
    application.run_polling()

if __name__ == "__main__":
    main()
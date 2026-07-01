import os
import io
import logging
import asyncio
from datetime import datetime
from PIL import Image, ImageFilter, ImageEnhance
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ============ CONFIGURATION ============
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables (set in Railway)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("BOT_TOKEN environment variable not set!")
    exit(1)

# Optional: API keys for additional features
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
REPLICATE_API_KEY = os.environ.get('REPLICATE_API_KEY', '')

# ============ HELPER FUNCTIONS ============

async def download_image(file_id, context):
    """Download an image from Telegram and return as PIL Image."""
    try:
        file = await context.bot.get_file(file_id)
        image_bytes = await file.download_as_bytearray()
        return Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        return None

async def upload_image(image, context, caption=""):
    """Upload a PIL Image back to Telegram."""
    try:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return await context.bot.send_photo(
            chat_id=context._chat_id,
            photo=img_byte_arr,
            caption=caption
        )
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        return None

async def generate_ai_image(prompt):
    """Generate an image using AI (placeholder - implement actual API)."""
    # This is a placeholder. You can integrate with:
    # - Google Gemini API
    # - Replicate (Stable Diffusion)
    # - OpenAI DALL-E
    # - Hugging Face Inference API
    
    if GEMINI_API_KEY:
        # Example with Gemini (you'd need to install google-generativeai)
        # For now, return a placeholder response
        return None
    
    if REPLICATE_API_KEY:
        # Example with Replicate (Stable Diffusion)
        # For now, return a placeholder response
        return None
    
    # Fallback: return None if no API keys are configured
    return None

async def shorten_url(url):
    """Shorten a URL using a free API."""
    try:
        # Using is.gd as a free URL shortener
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://is.gd/create.php",
                params={
                    "format": "json",
                    "url": url
                },
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                if 'shorturl' in data:
                    return data['shorturl']
                else:
                    return f"Error: {data.get('error', 'Unknown error')}"
            else:
                return f"Error: Failed to shorten URL (HTTP {response.status_code})"
    except Exception as e:
        logger.error(f"Error shortening URL: {e}")
        return f"Error: {str(e)}"

# ============ COMMAND HANDLERS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    welcome_text = (
        f"👋 Hello {user.first_name}!\n\n"
        "Welcome to **FastImage8Bot** - Your All-in-One Image Toolkit! 🚀\n\n"
        "**What I can do for you:**\n"
        "🖼️ **Convert Images** - Change formats (PNG ↔ JPG ↔ WebP)\n"
        "🎨 **Apply Filters** - Grayscale, Blur, Brightness, Contrast\n"
        "✨ **AI Generate** - Create images from text (coming soon)\n"
        "🔗 **Shorten URLs** - Make long links short\n\n"
        "Send me an image or use the buttons below to get started!"
    )
    
    keyboard = [
        [InlineKeyboardButton("🖼️ Image Tools", callback_data="image_tools")],
        [InlineKeyboardButton("🔗 URL Shortener", callback_data="url_shortener")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "📖 **Available Commands:**\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/about - About this bot\n"
        "/ping - Check if the bot is running\n"
        "/shorten <url> - Shorten a URL\n\n"
        "**Image Features:**\n"
        "Send an image with a caption to apply filters:\n"
        "• `convert png` - Convert to PNG format\n"
        "• `convert jpg` - Convert to JPG format\n"
        "• `grayscale` - Apply grayscale filter\n"
        "• `blur` - Apply blur filter\n"
        "• `brighten` - Increase brightness\n"
        "• `darken` - Decrease brightness\n\n"
        "**URL Shortener:**\n"
        "Use /shorten <url> to shorten any link"
    )
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            help_text,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(help_text, parse_mode='Markdown')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command."""
    about_text = (
        "🤖 **FastImage8Bot**\n\n"
        "A powerful Telegram bot for image processing, AI generation, and URL shortening.\n\n"
        "**Tech Stack:**\n"
        "• Python 3.11+\n"
        "• python-telegram-bot\n"
        "• Pillow (image processing)\n"
        "• Railway (hosting)\n"
        "• GitHub (version control)\n\n"
        "**Features:**\n"
        "✅ Image format conversion\n"
        "✅ Image filters & effects\n"
        "✅ URL shortener\n"
        "🔄 AI image generation (coming soon)\n\n"
        "🔗 [GitHub Repository](https://github.com/yourusername/FastImage8Bot)"
    )
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            about_text,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    else:
        await update.message.reply_text(about_text, parse_mode='Markdown')

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ping command."""
    await update.message.reply_text("🏓 Pong! I'm alive and running!")

async def shorten_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /shorten <url> command."""
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a URL to shorten.\n"
            "Example: `/shorten https://example.com/very/long/url`",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    await update.message.reply_text(f"⏳ Shortening URL...")
    
    shortened = await shorten_url(url)
    await update.message.reply_text(
        f"✅ **URL Shortened!**\n\n"
        f"🔗 Original: `{url}`\n"
        f"✂️ Short: `{shortened}`",
        parse_mode='Markdown'
    )

# ============ IMAGE PROCESSING FUNCTIONS ============

async def process_image(image, command):
    """Process an image based on the command."""
    try:
        if command == "convert png":
            # Convert to PNG
            return image.convert('RGBA'), "✅ Converted to PNG format"
        
        elif command == "convert jpg":
            # Convert to JPG
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            else:
                image = image.convert('RGB')
            return image, "✅ Converted to JPG format"
        
        elif command == "convert webp":
            # Convert to WebP
            return image.convert('RGB'), "✅ Converted to WebP format"
        
        elif command == "grayscale":
            # Apply grayscale filter
            return image.convert('L'), "✅ Applied grayscale filter"
        
        elif command == "blur":
            # Apply blur filter
            return image.filter(ImageFilter.BLUR), "✅ Applied blur filter"
        
        elif command == "brighten":
            # Increase brightness
            enhancer = ImageEnhance.Brightness(image)
            return enhancer.enhance(1.5), "✅ Increased brightness by 50%"
        
        elif command == "darken":
            # Decrease brightness
            enhancer = ImageEnhance.Brightness(image)
            return enhancer.enhance(0.5), "✅ Decreased brightness by 50%"
        
        elif command == "contrast":
            # Increase contrast
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(2.0), "✅ Increased contrast"
        
        else:
            return image, "ℹ️ No processing applied (unknown command)"
    
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return None, f"❌ Error processing image: {str(e)}"

# ============ MESSAGE HANDLERS ============

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming photos."""
    user = update.effective_user
    caption = update.message.caption or ""
    caption_lower = caption.lower().strip()
    
    # Check if caption contains a command
    valid_commands = [
        "convert png", "convert jpg", "convert webp",
        "grayscale", "blur", "brighten", "darken", "contrast"
    ]
    
    command = None
    for cmd in valid_commands:
        if cmd in caption_lower:
            command = cmd
            break
    
    # Download the image
    photo = update.message.photo[-1]  # Get the largest version
    image = await download_image(photo.file_id, context)
    
    if image is None:
        await update.message.reply_text("❌ Failed to download your image. Please try again.")
        return
    
    # Process the image if a command was given
    if command:
        await update.message.reply_text(f"⏳ Processing your image... ({command})")
        processed_image, message = await process_image(image, command)
        
        if processed_image:
            await upload_image(processed_image, context, message)
        else:
            await update.message.reply_text(message)
    else:
        # No command: show available options
        keyboard = [
            [InlineKeyboardButton("🔄 Convert PNG", callback_data=f"convert_png_{photo.file_id}"),
             InlineKeyboardButton("🔄 Convert JPG", callback_data=f"convert_jpg_{photo.file_id}")],
            [InlineKeyboardButton("⚫ Grayscale", callback_data=f"grayscale_{photo.file_id}"),
             InlineKeyboardButton("🌀 Blur", callback_data=f"blur_{photo.file_id}")],
            [InlineKeyboardButton("☀️ Brighten", callback_data=f"brighten_{photo.file_id}"),
             InlineKeyboardButton("🌙 Darken", callback_data=f"darken_{photo.file_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📸 Got your image, {user.first_name}!\n\n"
            "Choose an action below:",
            reply_markup=reply_markup
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages."""
    text = update.message.text
    
    # Check if it's a URL
    if text.startswith(('http://', 'https://')):
        await update.message.reply_text(f"⏳ Shortening URL...")
        shortened = await shorten_url(text)
        await update.message.reply_text(
            f"✅ **URL Shortened!**\n\n"
            f"🔗 Original: `{text}`\n"
            f"✂️ Short: `{shortened}`",
            parse_mode='Markdown'
        )
        return
    
    # Check for image generation request
    if text.startswith(('generate:', 'create:')):
        prompt = text.split(':', 1)[1].strip()
        await update.message.reply_text(f"🎨 Generating image for: '{prompt}'...")
        
        # Placeholder - implement AI generation here
        await update.message.reply_text(
            "🤖 AI image generation is coming soon!\n"
            "Stay tuned for this exciting feature."
        )
        return
    
    # Default response
    await update.message.reply_text(
        "I didn't recognize that command.\n\n"
        "You can:\n"
        "• Send me an image to process\n"
        "• Send a URL to shorten it\n"
        "• Use /help to see all commands"
    )

# ============ CALLBACK QUERY HANDLERS ============

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "image_tools":
        await query.edit_message_text(
            "🖼️ **Image Tools**\n\n"
            "Send me an image with one of these commands in the caption:\n"
            "• `convert png` - Convert to PNG\n"
            "• `convert jpg` - Convert to JPG\n"
            "• `grayscale` - Make it black & white\n"
            "• `blur` - Apply blur effect\n"
            "• `brighten` - Make it brighter\n"
            "• `darken` - Make it darker\n\n"
            "Or just send an image and use the buttons!",
            parse_mode='Markdown'
        )
    
    elif data == "url_shortener":
        await query.edit_message_text(
            "🔗 **URL Shortener**\n\n"
            "To shorten a URL, use:\n"
            "`/shorten <url>`\n\n"
            "Or simply send me any URL and I'll shorten it!\n\n"
            "Example:\n"
            "`/shorten https://example.com/very/long/url`",
            parse_mode='Markdown'
        )
    
    elif data == "help":
        await help_command(update, context)
    
    elif data.startswith(("convert_png_", "convert_jpg_", "grayscale_", "blur_", "brighten_", "darken_")):
        # Parse the callback data
        parts = data.split('_')
        action = "_".join(parts[:-1])  # e.g., "convert_png"
        file_id = parts[-1]
        
        # Map action to command
        command_map = {
            "convert_png": "convert png",
            "convert_jpg": "convert jpg",
            "grayscale": "grayscale",
            "blur": "blur",
            "brighten": "brighten",
            "darken": "darken"
        }
        
        command = command_map.get(action)
        if not command:
            await query.edit_message_text("❌ Unknown command.")
            return
        
        await query.edit_message_text(f"⏳ Processing your image... ({command})")
        
        # Get the image from the file_id stored in the callback data
        image = await download_image(file_id, context)
        if image is None:
            await query.edit_message_text("❌ Failed to download your image. Please try again.")
            return
        
        processed_image, message = await process_image(image, command)
        if processed_image:
            await upload_image(processed_image, context, message)
        else:
            await query.edit_message_text(message)

# ============ MAIN FUNCTION ============

def main():
    """Start the bot."""
    # Create the Application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("shorten", shorten_command))

    # Register message handlers
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Register callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Start the bot
    logger.info("🚀 FastImage8Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

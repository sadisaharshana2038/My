"""
Image handler for Telegram and Telegraph image URLs
Handles both t.me links and telegra.ph links gracefully
"""

import logging
from pyrogram import Client
from pyrogram.types import InputMediaPhoto
from utils import extract_telegram_file_id, parse_telegram_image_url

logger = logging.getLogger(__name__)


async def get_image_from_url(client: Client, url: str) -> str:
    """
    Get image file_id from URL (Telegram or Telegraph)
    
    Args:
        client: Pyrogram client
        url: Image URL
    
    Returns:
        File ID or URL for sending
    """
    try:
        if not url:
            return None
        
        # Parse URL
        parsed_url = parse_telegram_image_url(url)
        if not parsed_url:
            return None
        
        # Check if it's a Telegram link
        telegram_data = extract_telegram_file_id(parsed_url)
        if telegram_data:
            channel, message_id = telegram_data
            
            try:
                # Get message from channel
                message = await client.get_messages(f"@{channel}", message_id)
                
                if message and message.photo:
                    return message.photo.file_id
            except Exception as e:
                logger.warning(f"Could not fetch Telegram image: {e}")
        
        # Return URL for Telegraph or other links
        return parsed_url
        
    except Exception as e:
        logger.error(f"Error getting image from URL: {e}")
        return None


async def send_photo_safe(client: Client, chat_id: int, photo: str, caption: str = None, **kwargs):
    """
    Safely send photo with fallback to text
    
    Args:
        client: Pyrogram client
        chat_id: Chat ID
        photo: Photo file_id or URL
        caption: Caption text
        **kwargs: Additional arguments for send_photo
    """
    try:
        if photo:
            # Try to send photo
            await client.send_photo(chat_id, photo, caption=caption, **kwargs)
        else:
            # Fallback to text only
            if caption:
                await client.send_message(chat_id, caption, **kwargs)
    except Exception as e:
        logger.warning(f"Error sending photo, falling back to text: {e}")
        # Fallback to text only
        if caption:
            try:
                await client.send_message(chat_id, caption, **kwargs)
            except:
                pass

"""
Force subscribe module
Checks if user has joined required channel before using bot
"""

import logging
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from config import FORCE_SUB_CHANNEL
from keyboards import get_force_sub_keyboard

logger = logging.getLogger(__name__)


async def check_force_sub(client: Client, user_id: int) -> bool:
    """
    Check if user has joined the required channel
    
    Args:
        client: Pyrogram client
        user_id: User ID to check
    
    Returns:
        True if subscribed or no force sub enabled, False otherwise
    """
    try:
        # If no force sub channel configured, allow access
        if not FORCE_SUB_CHANNEL:
            return True
        
        # Check user membership
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        
        # Allow if user is member, admin, or creator
        if member.status in ["member", "administrator", "creator"]:
            return True
        
        return False
        
    except UserNotParticipant:
        return False
    except ChatAdminRequired:
        logger.error("Bot is not admin in force sub channel!")
        return True  # Allow access if bot can't check
    except Exception as e:
        logger.error(f"Error checking force sub: {e}")
        return True  # Allow access on error


async def handle_force_sub(message: Message, lang: str = "en") -> bool:
    """
    Handle force subscribe check and send message if needed
    
    Args:
        message: Pyrogram message
        lang: Language code
    
    Returns:
        True if user is subscribed, False otherwise
    """
    try:
        from config import get_message
        
        is_subscribed = await check_force_sub(message._client, message.from_user.id)
        
        if not is_subscribed:
            # Send force subscribe message
            await message.reply_text(
                get_message(lang, "force_sub", channel_link=f"https://t.me/{FORCE_SUB_CHANNEL}"),
                reply_markup=get_force_sub_keyboard(lang)
            )
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error handling force sub: {e}")
        return True  # Allow on error

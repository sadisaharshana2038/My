"""
Inline keyboard layouts for the bot
All button configurations - FIXED f-string errors
"""

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict
from config import get_button, FORCE_SUB_CHANNEL


def get_start_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Start command keyboard"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(get_button(lang, "help"), callback_data="help"),
            InlineKeyboardButton(get_button(lang, "profile"), callback_data="profile")
        ],
        [
            InlineKeyboardButton(get_button(lang, "request"), callback_data="start_request"),
            InlineKeyboardButton(get_button(lang, "leaderboard"), callback_data="leaderboard")
        ]
    ])


def get_help_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Help menu keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="start")]
    ])


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇱🇰 සිංහල", callback_data="lang_si")
        ]
    ])


def get_search_results_keyboard(
    results: List[Dict],
    page: int,
    total_pages: int,
    query: str,
    lang: str = "en"
) -> InlineKeyboardMarkup:
    """Search results keyboard with pagination - FIXED"""
    from utils import format_file_size
    
    buttons = []
    
    # File buttons (10 max per page)
    for file in results:
        # Get file data
        file_size = file.get('file_size', 0)
        clean_title = file.get('clean_title', 'Unknown')
        year = file.get('year')
        file_id = file.get('file_id', '')
        
        # Build button text
        button_text = f"{format_file_size(file_size)} | {clean_title}"
        if year:
            button_text += f" | {year}"
        
        # Truncate if too long
        if len(button_text) > 64:
            button_text = button_text[:61] + "..."
        
        # Create callback data
        callback_data = f"dl_{file_id}"
        
        buttons.append([
            InlineKeyboardButton(button_text, callback_data=callback_data)
        ])
    
    # Pagination buttons
    pagination = []
    if page > 1:
        pagination.append(
            InlineKeyboardButton(get_button(lang, "prev"), callback_data=f"page_{query}_{page-1}")
        )
    
    pagination.append(
        InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop")
    )
    
    if page < total_pages:
        pagination.append(
            InlineKeyboardButton(get_button(lang, "next"), callback_data=f"page_{query}_{page+1}")
        )
    
    if pagination:
        buttons.append(pagination)
    
    return InlineKeyboardMarkup(buttons)


def get_force_sub_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Force subscribe keyboard"""
    if not FORCE_SUB_CHANNEL:
        return None
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(get_button(lang, "join_channel"), url=f"https://t.me/{FORCE_SUB_CHANNEL}")],
        [InlineKeyboardButton(get_button(lang, "check_subscription"), callback_data="check_sub")]
    ])


def get_request_results_keyboard(results: List[Dict]) -> InlineKeyboardMarkup:
    """TMDB search results keyboard - FIXED"""
    buttons = []
    
    for result in results[:10]:  # Max 10
        media_type = result.get("media_type", "movie")
        title = result.get("title") or result.get("name", "Unknown")
        year = ""
        
        if media_type == "movie":
            release_date = result.get("release_date", "")
            year = release_date[:4] if release_date else ""
        else:
            first_air_date = result.get("first_air_date", "")
            year = first_air_date[:4] if first_air_date else ""
        
        button_text = f"{title} ({year})" if year else title
        
        # Truncate if needed
        if len(button_text) > 64:
            button_text = button_text[:61] + "..."
        
        # Get tmdb_id
        tmdb_id = result.get('id', 0)
        
        buttons.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"req_{media_type}_{tmdb_id}"
            )
        ])
    
    return InlineKeyboardMarkup(buttons)


def get_request_detail_keyboard(request_id: str, lang: str = "en") -> InlineKeyboardMarkup:
    """Request detail keyboard with request button"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(get_button(lang, "request_subtitle"), callback_data=f"submit_req_{request_id}")]
    ])


def get_admin_panel_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Admin panel keyboard"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
            InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton("🔄 Index Channel", callback_data="admin_index"),
            InlineKeyboardButton("💾 Backup", callback_data="admin_backup")
        ],
        [
            InlineKeyboardButton("🔍 Scan Duplicates", callback_data="admin_scan")
        ]
    ])


def get_broadcast_confirm_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Broadcast confirmation keyboard"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(get_button(lang, "confirm"), callback_data="broadcast_confirm"),
            InlineKeyboardButton(get_button(lang, "cancel"), callback_data="broadcast_cancel")
        ]
    ])


def get_admin_request_keyboard(request_id: str, lang: str = "en") -> InlineKeyboardMarkup:
    """Admin request handling keyboard"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(get_button(lang, "done"), callback_data=f"req_done_{request_id}"),
            InlineKeyboardButton(get_button(lang, "not_available"), callback_data=f"req_no_{request_id}")
        ]
    ])


def get_duplicate_scan_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Duplicate scan action keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(get_button(lang, "delete_duplicates"), callback_data="delete_dupes")]
    ])

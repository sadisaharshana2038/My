"""
Configuration file for Telegram Subtitle Bot
Contains all settings, credentials, and multilingual messages
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# TELEGRAM CREDENTIALS
# ============================================
API_ID = int(os.getenv("API_ID", "36039536"))
API_HASH = os.getenv("API_HASH", "f9c74f8a38a3b2ea0f2e88fe373b554f")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8502581099:AAFiHqmUCCvH8bR15bmzBzOYCA3LrmcCn2o")
BOT_USERNAME = os.getenv("BOT_USERNAME", "MySubTest1_bot")

# ============================================
# MONGODB CONFIGURATION
# ============================================
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://Sadisa:JRGgclOXbm5KLiHn@cluster0.vexxjgb.mongodb.net/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "subtitle_bot")

# ============================================
# CHANNEL IDS
# ============================================
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID", "-1003839839205")) or None
UPDATE_CHANNEL_ID = int(os.getenv("UPDATE_CHANNEL_ID", "0")) or None
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", "0")) or None
FORCE_SUB_CHANNEL = int(os.getenv("FORCE_SUB_CHANNEL", "0")) or None

# ============================================
# ADMIN IDS
# ============================================
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "8107411538")
ADMIN_IDS: List[int] = [int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip().isdigit()]

# ============================================
# TMDB API (The Movie Database)
# ============================================
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "d2d002918cb1dfef9148bbf4f1abdcdc")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# ============================================
# IMAGE URLS (Customizable)
# ============================================
WELCOME_IMAGE = os.getenv("WELCOME_IMAGE", "https://t.me/shprofilterupdate/300")
HELP_IMAGE = os.getenv("HELP_IMAGE", "https://t.me/shprofilterupdate/300")
STATS_IMAGE = os.getenv("STATS_IMAGE", "https://t.me/shprofilterupdate/300")
PROFILE_IMAGE = os.getenv("PROFILE_IMAGE", "https://t.me/shprofilterupdate/300")

# ============================================
# BOT SETTINGS
# ============================================
RESULTS_PER_PAGE = 10
MAX_PAGES = 5
MAX_RESULTS = RESULTS_PER_PAGE * MAX_PAGES  # 50 total
FUZZY_MATCH_THRESHOLD = 70
BROADCAST_BATCH_SIZE = 50
BROADCAST_DELAY = 1  # seconds between batches
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================
# POINTS SYSTEM
# ============================================
POINTS_PER_DOWNLOAD = 1
POINTS_PER_REQUEST = 2

# ============================================
# RANK SYSTEM
# ============================================
RANKS = {
    "beginner": {"min": 0, "max": 9, "emoji": "🥉", "name_en": "Beginner", "name_si": "ආරම්භකයා"},
    "regular": {"min": 10, "max": 49, "emoji": "🥈", "name_en": "Regular User", "name_si": "සාමාන්‍ය පරිශීලක"},
    "active": {"min": 50, "max": 99, "emoji": "🥇", "name_en": "Active User", "name_si": "ක්‍රියාශීලී පරිශීලක"},
    "premium": {"min": 100, "max": 499, "emoji": "💎", "name_en": "Premium User", "name_si": "වාරික පරිශීලක"},
    "vip": {"min": 500, "max": 999, "emoji": "👑", "name_en": "VIP User", "name_si": "වී.අයි.පී පරිශීලක"},
    "legend": {"min": 1000, "max": float('inf'), "emoji": "🌟", "name_en": "Legend", "name_si": "පුරාවෘත්තය"}
}

# ============================================
# FILE EXTENSIONS (Subtitle files and archives)
# ============================================
SUBTITLE_EXTENSIONS = [".srt", ".ass", ".ssa", ".sub", ".vtt", ".sbv", ".zip"]

# Rest of config.py content (MESSAGES dict) stays the same...
MESSAGES = {
    "en": {
        "welcome": (
            "👋 <b>Welcome to Subtitle Bot!</b>\n\n"
            "🎬 I can help you find subtitle files for movies and TV shows.\n\n"
            "🔍 Just type the name of a movie or show to search!\n\n"
            "Use /help to see all available commands."
        ),
        "help": (
            "📚 <b>Help Menu</b>\n\n"
            "<b>🔍 Search Commands:</b>\n"
            "• Just type a movie/show name to search\n"
            "• Example: <code>Avatar</code> or <code>Breaking Bad</code>\n\n"
            "<b>👤 User Commands:</b>\n"
            "• /start - Start the bot\n"
            "• /help - Show this help menu\n"
            "• /language - Change language (English/Sinhala)\n"
            "• /profile - View your profile and stats\n"
            "• /request - Request a subtitle\n"
            "• /leaderboard - View top users\n\n"
            "Need help? Contact administrators!"
        ),
        "searching": "🔍 Searching for: <b>{query}</b>...",
        "no_results": "❌ No results found for: <b>{query}</b>\n\nTry different keywords or use /request",
        "search_results": "🎬 <b>Search Results for:</b> {query}\n\n📄 Found {total} results (Showing page {page}/{total_pages})",
        "download_success": "✅ <b>File Downloaded!</b>\n\n📁 File: {filename}\n💎 You earned +{points} points!",
        "file_not_found": "❌ File not found. It may have been deleted.",
        "profile": (
            "👤 <b>Your Profile</b>\n\n"
            "🆔 User ID: <code>{user_id}</code>\n"
            "👤 Name: {name}\n"
            "📥 Total Downloads: {downloads}\n"
            "💎 Points: {points}\n"
            "🏆 Rank: {rank_emoji} {rank_name}\n"
            "📅 Member Since: {join_date}\n"
            "⏰ Last Active: {last_active}"
        ),
        "leaderboard": (
            "🏆 <b>Top Users Leaderboard</b>\n\n"
            "{leaderboard_text}\n\n"
            "💡 Keep downloading to climb higher!"
        ),
        "leaderboard_entry": "{rank}. {rank_emoji} {name} - {downloads} downloads ({points} pts)",
        "request_prompt": "🎬 Please type the name of the movie or TV show you want to request:",
        "request_searching_tmdb": "🔍 Searching TMDB for: <b>{query}</b>...",
        "request_no_results": "❌ No results found on TMDB for: <b>{query}</b>",
        "request_select": "🎬 <b>Search Results:</b>\n\nSelect the correct title:",
        "request_details": (
            "🎬 <b>{title}</b> ({year})\n\n"
            "⭐ Rating: {rating}/10\n"
            "⏱️ Runtime: {runtime} minutes\n"
            "🎭 Genres: {genres}\n\n"
            "📝 <b>Overview:</b>\n{overview}\n\n"
            "Click below to request this subtitle!"
        ),
        "request_submitted": (
            "✅ <b>Request Submitted!</b>\n\n"
            "🎬 Title: {title}\n"
            "📅 Year: {year}\n\n"
            "We'll notify you once available!\n"
            "💎 You earned +{points} points!"
        ),
        "request_already_exists": "⚠️ You've already requested this title!",
        "request_fulfilled": "✅ <b>Good News!</b>\n\n🎬 Your request for <b>{title}</b> is now available!",
        "request_rejected": "❌ Sorry, <b>{title}</b> is not available at this time.",
        "force_sub": (
            "⚠️ <b>Join Our Channel First!</b>\n\n"
            "To use this bot, you must join our channel:\n"
            "👉 {channel_link}\n\n"
            "After joining, click the button below to verify."
        ),
        "not_subscribed": "❌ You haven't joined the channel yet!",
        "subscription_verified": "✅ Subscription verified! You can now use the bot.",
        "language_select": "🌐 <b>Select Your Language:</b>",
        "language_changed": "✅ Language changed to: <b>English</b>",
        "admin_panel": "👨‍💼 <b>Admin Panel</b>\n\nSelect an action:",
        "stats": (
            "📊 <b>Bot Statistics</b>\n\n"
            "👥 Total Users: {total_users}\n"
            "📁 Total Files: {total_files}\n"
            "📥 Total Downloads: {total_downloads}\n"
            "🔍 Total Searches: {total_searches}\n"
            "📝 Pending Requests: {pending_requests}\n"
            "✅ Fulfilled Requests: {fulfilled_requests}\n\n"
            "<b>🔥 Top 5 Most Downloaded:</b>\n{top_files}\n\n"
            "<b>👑 Top 5 Users:</b>\n{top_users}"
        ),
        "broadcast_prompt": "📢 Send the message you want to broadcast.\n\nSupported: Text, Photo, Video, Document",
        "broadcast_confirm": "📢 <b>Confirm Broadcast</b>\n\n👥 Total Users: {total_users}\n\nSend to all users?",
        "broadcast_cancelled": "❌ Broadcast cancelled.",
        "broadcast_started": "📢 <b>Broadcast Started!</b>\n\n👥 Total Users: {total_users}",
        "broadcast_progress": "📢 <b>Broadcasting...</b>\n\n✅ Success: {success}\n❌ Failed: {failed}\n🚫 Blocked: {blocked}\n⏳ Remaining: {remaining}",
        "broadcast_complete": (
            "✅ <b>Broadcast Complete!</b>\n\n"
            "👥 Total Users: {total_users}\n"
            "✅ Successfully Sent: {success}\n"
            "❌ Failed: {failed}\n"
            "🚫 Blocked Bot: {blocked}\n"
            "⏱️ Time Taken: {time_taken}"
        ),
        "indexing_started": "🔄 Channel indexing started...",
        "indexing_complete": "✅ Indexing complete!\n\n📁 New files added: {new_files}\n⏱️ Time taken: {time_taken}",
        "backup_created": "✅ Database backup created successfully!",
        "scan_started": "🔍 Scanning for duplicate files...",
        "scan_complete": "✅ Scan complete!\n\n🔍 Total files: {total}\n📊 Duplicates found: {duplicates}",
        "duplicates_deleted": "✅ {count} duplicate files deleted!",
        "error": "❌ An error occurred. Please try again later.",
        "error_db": "❌ Database error. Please contact administrators.",
        "admin_only": "⚠️ This command is only available to administrators.",
        "not_authorized": "⚠️ You are not authorized to use this command.",
        "btn_help": "📚 Help",
        "btn_profile": "👤 Profile",
        "btn_request": "📝 Request Subtitle",
        "btn_leaderboard": "🏆 Leaderboard",
        "btn_next": "Next ▶️",
        "btn_prev": "◀️ Previous",
        "btn_download": "📥 Download",
        "btn_request_subtitle": "📝 Request Subtitle",
        "btn_join_channel": "📢 Join Channel",
        "btn_check_subscription": "✅ I Joined",
        "btn_english": "🇬🇧 English",
        "btn_sinhala": "🇱🇰 සිංහල",
        "btn_admin_stats": "📊 Statistics",
        "btn_admin_broadcast": "📢 Broadcast",
        "btn_admin_index": "🔄 Index Channel",
        "btn_admin_backup": "💾 Backup",
        "btn_admin_scan": "🔍 Scan Duplicates",
        "btn_confirm": "✅ Confirm",
        "btn_cancel": "❌ Cancel",
        "btn_delete_duplicates": "🗑️ Delete Duplicates",
        "btn_done": "✅ Done",
        "btn_not_available": "❌ Not Available",
    },
    "si": {
        "welcome": (
            "👋 <b>උපසිරැසි බොට් වෙත සාදරයෙන් පිළිගනිමු!</b>\n\n"
            "🎬 මම ඔබට චිත්‍රපට සහ රූපවාහිනී වැඩසටහන් සඳහා උපසිරැසි ගොනු සොයා ගැනීමට උදව් කරමි.\n\n"
            "🔍 සෙවීමට චිත්‍රපටයක හෝ වැඩසටහනක නම ටයිප් කරන්න!"
        ),
        "help": (
            "📚 <b>උදව් මෙනුව</b>\n\n"
            "<b>🔍 සෙවුම් විධාන:</b>\n"
            "• චිත්‍රපට/වැඩසටහන් නමක් ටයිප් කරන්න\n\n"
            "<b>👤 පරිශීලක විධාන:</b>\n"
            "• /start - බොට් ආරම්භ කරන්න\n"
            "• /help - මෙම උදව් මෙනුව\n"
            "• /profile - ඔබේ පැතිකඩ බලන්න"
        ),
        "searching": "🔍 සෙවීම: <b>{query}</b>...",
        "no_results": "❌ ප්‍රතිඵල හමු නොවීය: <b>{query}</b>",
        "search_results": "🎬 <b>සෙවුම් ප්‍රතිඵල:</b> {query}\n\n📄 ප්‍රතිඵල {total} (පිටුව {page}/{total_pages})",
        "download_success": "✅ <b>ගොනුව බාගත විය!</b>\n\n📁 ගොනුව: {filename}\n💎 ලකුණු +{points}!",
        "btn_help": "📚 උදව්",
        "btn_profile": "👤 පැතිකඩ",
        "btn_next": "ඊළඟ ▶️",
        "btn_prev": "◀️ පෙර",
    }
}

def get_message(lang: str, key: str, **kwargs) -> str:
    """Get message in specified language with formatting"""
    try:
        if lang not in MESSAGES:
            lang = "en"
        message = MESSAGES[lang].get(key, MESSAGES["en"].get(key, ""))
        if kwargs:
            message = message.format(**kwargs)
        return message
    except Exception:
        try:
            return MESSAGES["en"][key].format(**kwargs)
        except:
            return f"Error loading message: {key}"

def get_button(lang: str, key: str) -> str:
    """Get button text in specified language"""
    return get_message(lang, f"btn_{key}")

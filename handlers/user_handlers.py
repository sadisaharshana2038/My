"""
User command handlers
Handles all user-facing commands and messages
"""

import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from config import get_message, ADMIN_IDS, RESULTS_PER_PAGE, MAX_PAGES
from keyboards import (
    get_start_keyboard, get_help_keyboard, get_language_keyboard,
    get_search_results_keyboard
)
from force_subscribe import handle_force_sub
from image_handler import send_photo_safe, get_image_from_url
from utils import sanitize_query, get_user_display_name, format_timestamp
from fuzzywuzzy import fuzz

logger = logging.getLogger(__name__)


# User state storage (in-memory, use Redis for production)
user_states = {}


def register_user_handlers(app: Client):
    """Register all user command handlers"""
    
    @app.on_message(filters.command("start") & filters.private)
    async def start_command(client: Client, message: Message):
        """Handle /start command"""
        try:
            db = client.db
            if not db:
                await message.reply_text("Bot is starting up. Please try again in a moment.")
                return
            
            # Add user to database
            await db.add_user(
                message.from_user.id,
                message.from_user.username,
                message.from_user.first_name
            )
            
            # Get user language
            user = await db.get_user(message.from_user.id)
            lang = user.get("language", "en") if user else "en"
            
            # Check force subscribe
            if not await handle_force_sub(message, lang):
                return
            
            # Send welcome message with image
            from config import WELCOME_IMAGE
            photo = await get_image_from_url(client, WELCOME_IMAGE)
            
            await send_photo_safe(
                client,
                message.chat.id,
                photo,
                get_message(lang, "welcome"),
                reply_markup=get_start_keyboard(lang)
            )
            
        except Exception as e:
            logger.error(f"Error in start command: {e}", exc_info=True)
            await message.reply_text(get_message("en", "error"))
    
    @app.on_message(filters.command("help") & filters.private)
    async def help_command(client: Client, message: Message):
        """Handle /help command"""
        try:
            db = client.db
            if not db:
                await message.reply_text("Bot is starting up...")
                return
            
            user = await db.get_user(message.from_user.id)
            lang = user.get("language", "en") if user else "en"
            
            # Check force subscribe
            if not await handle_force_sub(message, lang):
                return
            
            from config import HELP_IMAGE
            photo = await get_image_from_url(client, HELP_IMAGE)
            
            await send_photo_safe(
                client,
                message.chat.id,
                photo,
                get_message(lang, "help"),
                reply_markup=get_help_keyboard(lang)
            )
            
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await message.reply_text(get_message("en", "error"))
    
    @app.on_message(filters.command("language") & filters.private)
    async def language_command(client: Client, message: Message):
        """Handle /language command"""
        try:
            db = client.db
            if not db:
                return
            
            user = await db.get_user(message.from_user.id)
            lang = user.get("language", "en") if user else "en"
            
            await message.reply_text(
                get_message(lang, "language_select"),
                reply_markup=get_language_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Error in language command: {e}")
    
    @app.on_message(filters.command("profile") & filters.private)
    async def profile_command(client: Client, message: Message):
        """Handle /profile command"""
        try:
            db = client.db
            if not db:
                return
            
            user = await db.get_user(message.from_user.id)
            if not user:
                await message.reply_text("Please use /start first")
                return
            
            lang = user.get("language", "en")
            
            # Get rank
            rank_data = await db.get_user_rank(user.get("downloads", 0))
            
            profile_text = get_message(
                lang,
                "profile",
                user_id=user["user_id"],
                name=get_user_display_name(message.from_user),
                downloads=user.get("downloads", 0),
                points=user.get("points", 0),
                rank_emoji=rank_data["emoji"],
                rank_name=rank_data[f"name_{lang}"],
                join_date=user.get("joined_at", "").strftime("%Y-%m-%d") if user.get("joined_at") else "Unknown",
                last_active=format_timestamp(user.get("last_active", "")) if user.get("last_active") else "Now"
            )
            
            from config import PROFILE_IMAGE
            photo = await get_image_from_url(client, PROFILE_IMAGE)
            
            await send_photo_safe(
                client,
                message.chat.id,
                photo,
                profile_text
            )
            
        except Exception as e:
            logger.error(f"Error in profile command: {e}")
    
    @app.on_message(filters.command("leaderboard") & filters.private)
    async def leaderboard_command(client: Client, message: Message):
        """Handle /leaderboard command"""
        try:
            db = client.db
            if not db:
                return
            
            user = await db.get_user(message.from_user.id)
            lang = user.get("language", "en") if user else "en"
            
            # Get top users
            top_users = await db.get_top_users(10)
            
            if not top_users:
                await message.reply_text("No users yet!")
                return
            
            # Build leaderboard text
            leaderboard_entries = []
            for idx, user_data in enumerate(top_users, 1):
                rank_data = await db.get_user_rank(user_data.get("downloads", 0))
                name = user_data.get("first_name", "Unknown")
                
                entry = get_message(
                    lang,
                    "leaderboard_entry",
                    rank=idx,
                    rank_emoji=rank_data["emoji"],
                    name=name,
                    downloads=user_data.get("downloads", 0),
                    points=user_data.get("points", 0)
                )
                leaderboard_entries.append(entry)
            
            leaderboard_text = get_message(
                lang,
                "leaderboard",
                leaderboard_text="\n".join(leaderboard_entries)
            )
            
            await message.reply_text(leaderboard_text)
            
        except Exception as e:
            logger.error(f"Error in leaderboard command: {e}")
    
    @app.on_message(filters.command("request") & filters.private)
    async def request_command(client: Client, message: Message):
        """Handle /request command"""
        try:
            db = client.db
            if not db:
                return
            
            user = await db.get_user(message.from_user.id)
            lang = user.get("language", "en") if user else "en"
            
            # Check force subscribe
            if not await handle_force_sub(message, lang):
                return
            
            # Set user state to waiting for request input
            user_states[message.from_user.id] = {"state": "awaiting_request"}
            
            await message.reply_text(get_message(lang, "request_prompt"))
            
        except Exception as e:
            logger.error(f"Error in request command: {e}")
    
    @app.on_message(filters.text & filters.private & ~filters.command(["start", "help", "stats", "broadcast", "index", "backup", "scan"]))
    async def handle_text_message(client: Client, message: Message):
        """Handle text messages (search or request)"""
        try:
            db = client.db
            if not db:
                return
            
            user = await db.get_user(message.from_user.id)
            lang = user.get("language", "en") if user else "en"
            
            # Check force subscribe
            if not await handle_force_sub(message, lang):
                return
            
            # Check if user is in request state
            user_state = user_states.get(message.from_user.id, {})
            
            if user_state.get("state") == "awaiting_request":
                # Handle TMDB request
                await handle_tmdb_request(client, message, lang)
                return
            
            # Handle as search query
            await handle_search(client, message, lang)
            
        except Exception as e:
            logger.error(f"Error handling text message: {e}")


async def handle_search(client: Client, message: Message, lang: str):
    """Handle search query"""
    try:
        db = client.db
        query = sanitize_query(message.text)
        
        if len(query) < 2:
            await message.reply_text("Please provide a longer search query")
            return
        
        # Send searching message
        search_msg = await message.reply_text(
            get_message(lang, "searching", query=query)
        )
        
        # Log search
        await db.log_search(query, message.from_user.id)
        await db.increment_user_searches(message.from_user.id)
        
        # Search database (text search first)
        results, total = await db.search_files(query, 0, RESULTS_PER_PAGE)
        
        # If no results, try fuzzy search
        if not results:
            all_files = await db.fuzzy_search_files(query)
            
            # Filter by fuzzy score
            from config import FUZZY_MATCH_THRESHOLD
            results = [
                f for f in all_files
                if fuzz.ratio(query, f.get("clean_title", "").lower()) >= FUZZY_MATCH_THRESHOLD
            ]
            
            total = len(results)
            results = results[:RESULTS_PER_PAGE]  # First page
        
        if not results:
            await search_msg.edit_text(get_message(lang, "no_results", query=query))
            return
        
        # Calculate total pages
        total_pages = min((total + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE, MAX_PAGES)
        
        # Send results
        results_text = get_message(
            lang,
            "search_results",
            query=query,
            total=total,
            page=1,
            total_pages=total_pages
        )
        
        await search_msg.edit_text(
            results_text,
            reply_markup=get_search_results_keyboard(results, 1, total_pages, query, lang)
        )
        
    except Exception as e:
        logger.error(f"Error in search: {e}")


async def handle_tmdb_request(client: Client, message: Message, lang: str):
    """Handle TMDB request search"""
    try:
        from tmdb_client import TMDBClient
        from keyboards import get_request_results_keyboard
        
        query = message.text
        
        # Clear user state
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        
        # Search TMDB
        search_msg = await message.reply_text(
            get_message(lang, "request_searching_tmdb", query=query)
        )
        
        async with TMDBClient() as tmdb:
            results = await tmdb.search_multi(query)
        
        if not results:
            await search_msg.edit_text(get_message(lang, "request_no_results", query=query))
            return
        
        # Show results
        await search_msg.edit_text(
            get_message(lang, "request_select"),
            reply_markup=get_request_results_keyboard(results)
        )
        
    except Exception as e:
        logger.error(f"Error in TMDB request: {e}")

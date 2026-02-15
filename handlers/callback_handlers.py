"""
Callback query handlers
Handles all inline button callbacks
"""

import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from config import get_message, RESULTS_PER_PAGE, POINTS_PER_DOWNLOAD, ADMIN_IDS
from keyboards import (
    get_start_keyboard, get_help_keyboard, get_language_keyboard,
    get_search_results_keyboard, get_request_detail_keyboard,
    get_admin_request_keyboard
)
from force_subscribe import check_force_sub
from broadcast import BroadcastManager
from image_handler import send_photo_safe, get_image_from_url

logger = logging.getLogger(__name__)


def register_callback_handlers(app: Client):
    """Register all callback query handlers"""
    
    @app.on_callback_query(filters.regex("^start$"))
    async def start_callback(client: Client, callback: CallbackQuery):
        """Handle start button"""
        try:
            db = client.db
            user = await db.get_user(callback.from_user.id)
            lang = user.get("language", "en") if user else "en"
            
            await callback.message.edit_text(
                get_message(lang, "welcome"),
                reply_markup=get_start_keyboard(lang)
            )
            await callback.answer()
        except Exception as e:
            logger.error(f"Error in start callback: {e}")
    
    @app.on_callback_query(filters.regex("^help$"))
    async def help_callback(client: Client, callback: CallbackQuery):
        """Handle help button"""
        try:
            db = client.db
            user = await db.get_user(callback.from_user.id)
            lang = user.get("language", "en") if user else "en"
            
            await callback.message.edit_text(
                get_message(lang, "help"),
                reply_markup=get_help_keyboard(lang)
            )
            await callback.answer()
        except Exception as e:
            logger.error(f"Error in help callback: {e}")
    
    @app.on_callback_query(filters.regex("^profile$"))
    async def profile_callback(client: Client, callback: CallbackQuery):
        """Handle profile button"""
        try:
            # Trigger profile command
            from handlers.user_handlers import profile_command
            await callback.answer("Loading profile...")
            # Would need to simulate message
        except Exception as e:
            logger.error(f"Error in profile callback: {e}")
    
    @app.on_callback_query(filters.regex("^lang_"))
    async def language_callback(client: Client, callback: CallbackQuery):
        """Handle language selection"""
        try:
            db = client.db
            lang_code = callback.data.split("_")[1]
            
            await db.update_user_language(callback.from_user.id, lang_code)
            
            await callback.answer(
                get_message(lang_code, "language_changed"),
                show_alert=True
            )
            
            await callback.message.edit_text(
                get_message(lang_code, "welcome"),
                reply_markup=get_start_keyboard(lang_code)
            )
            
        except Exception as e:
            logger.error(f"Error in language callback: {e}")
    
    @app.on_callback_query(filters.regex("^dl_"))
    async def download_callback(client: Client, callback: CallbackQuery):
        """Handle file download"""
        try:
            db = client.db
            file_id = callback.data.split("_", 1)[1]
            
            # Check force subscribe
            if not await check_force_sub(client, callback.from_user.id):
                user = await db.get_user(callback.from_user.id)
                lang = user.get("language", "en") if user else "en"
                await callback.answer(get_message(lang, "not_subscribed"), show_alert=True)
                return
            
            # Get file from database
            file_data = await db.get_file(file_id)
            
            if not file_data:
                await callback.answer(get_message("en", "file_not_found"), show_alert=True)
                return
            
            # Send file
            await client.send_document(
                callback.from_user.id,
                file_id,
                caption=get_message(
                    "en",
                    "download_success",
                    filename=file_data.get("file_name"),
                    points=POINTS_PER_DOWNLOAD
                )
            )
            
            # Update statistics
            await db.increment_file_downloads(file_id)
            await db.increment_user_downloads(callback.from_user.id)
            
            await callback.answer("✅ File sent!", show_alert=False)
            
        except Exception as e:
            logger.error(f"Error in download callback: {e}")
            await callback.answer("Error sending file", show_alert=True)
    
    @app.on_callback_query(filters.regex("^page_"))
    async def pagination_callback(client: Client, callback: CallbackQuery):
        """Handle search pagination"""
        try:
            db = client.db
            parts = callback.data.split("_")
            query = parts[1]
            page = int(parts[2])
            
            user = await db.get_user(callback.from_user.id)
            lang = user.get("language", "en") if user else "en"
            
            # Calculate skip
            skip = (page - 1) * RESULTS_PER_PAGE
            
            # Get results
            results, total = await db.search_files(query, skip, RESULTS_PER_PAGE)
            
            from config import MAX_PAGES
            total_pages = min((total + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE, MAX_PAGES)
            
            # Update message
            results_text = get_message(
                lang,
                "search_results",
                query=query,
                total=total,
                page=page,
                total_pages=total_pages
            )
            
            await callback.message.edit_text(
                results_text,
                reply_markup=get_search_results_keyboard(results, page, total_pages, query, lang)
            )
            
            await callback.answer()
            
        except Exception as e:
            logger.error(f"Error in pagination callback: {e}")
    
    @app.on_callback_query(filters.regex("^req_"))
    async def request_callback(client: Client, callback: CallbackQuery):
        """Handle TMDB request selection"""
        try:
            from tmdb_client import TMDBClient
            
            db = client.db
            user = await db.get_user(callback.from_user.id)
            lang = user.get("language", "en") if user else "en"
            
            parts = callback.data.split("_")
            media_type = parts[1]
            tmdb_id = int(parts[2])
            
            # Get details from TMDB
            async with TMDBClient() as tmdb:
                if media_type == "movie":
                    details = await tmdb.get_movie_details(tmdb_id)
                else:
                    details = await tmdb.get_tv_details(tmdb_id)
            
            if not details:
                await callback.answer("Error fetching details", show_alert=True)
                return
            
            # Format details message
            details_text = get_message(
                lang,
                "request_details",
                title=details["title"],
                year=details.get("year", "N/A"),
                rating=details.get("rating", 0),
                runtime=details.get("runtime", 0),
                genres=details.get("genres", "N/A"),
                overview=details.get("overview", "No description")
            )
            
            # Send with poster
            if details.get("poster_url"):
                try:
                    await callback.message.delete()
                    await client.send_photo(
                        callback.from_user.id,
                        details["poster_url"],
                        caption=details_text,
                        reply_markup=get_request_detail_keyboard(str(tmdb_id), lang)
                    )
                except:
                    await callback.message.edit_text(
                        details_text,
                        reply_markup=get_request_detail_keyboard(str(tmdb_id), lang)
                    )
            else:
                await callback.message.edit_text(
                    details_text,
                    reply_markup=get_request_detail_keyboard(str(tmdb_id), lang)
                )
            
            await callback.answer()
            
        except Exception as e:
            logger.error(f"Error in request callback: {e}")
    
    @app.on_callback_query(filters.regex("^check_sub$"))
    async def check_subscription_callback(client: Client, callback: CallbackQuery):
        """Handle subscription check"""
        try:
            db = client.db
            user = await db.get_user(callback.from_user.id)
            lang = user.get("language", "en") if user else "en"
            
            is_subscribed = await check_force_sub(client, callback.from_user.id)
            
            if is_subscribed:
                await callback.answer(get_message(lang, "subscription_verified"), show_alert=True)
            else:
                await callback.answer(get_message(lang, "not_subscribed"), show_alert=True)
                
        except Exception as e:
            logger.error(f"Error in check sub callback: {e}")
    
    @app.on_callback_query(filters.regex("^broadcast_"))
    async def broadcast_callback(client: Client, callback: CallbackQuery):
        """Handle broadcast confirmation"""
        try:
            if callback.from_user.id not in ADMIN_IDS:
                return
            
            from handlers.admin_handlers import admin_states
            
            action = callback.data.split("_")[1]
            
            if action == "confirm":
                admin_state = admin_states.get(callback.from_user.id, {})
                broadcast_msg = admin_state.get("message")
                
                if not broadcast_msg:
                    await callback.answer("Error: No message to broadcast", show_alert=True)
                    return
                
                # Start broadcast
                await callback.message.edit_text(get_message("en", "broadcast_started", total_users=0))
                
                db = client.db
                manager = BroadcastManager(client, db)
                
                stats = await manager.broadcast_message(
                    broadcast_msg,
                    callback.from_user.id,
                    callback.message
                )
                
                # Send final stats
                final_text = get_message(
                    "en",
                    "broadcast_complete",
                    total_users=stats["total"],
                    success=stats["success"],
                    failed=stats["failed"],
                    blocked=stats["blocked"],
                    time_taken=stats["time_taken"]
                )
                
                await callback.message.edit_text(final_text)
                
                # Clear state
                if callback.from_user.id in admin_states:
                    del admin_states[callback.from_user.id]
                    
            elif action == "cancel":
                await callback.message.edit_text(get_message("en", "broadcast_cancelled"))
                
                if callback.from_user.id in admin_states:
                    del admin_states[callback.from_user.id]
            
            await callback.answer()
            
        except Exception as e:
            logger.error(f"Error in broadcast callback: {e}")
    
    @app.on_callback_query(filters.regex("^noop$"))
    async def noop_callback(client: Client, callback: CallbackQuery):
        """No-op callback (for page number button)"""
        await callback.answer()

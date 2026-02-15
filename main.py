#!/usr/bin/env python3
"""
Telegram Subtitle Bot - Main Entry Point
Professional production-ready bot with complete error handling
"""

import asyncio
import logging
from datetime import datetime
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait, RPCError
from motor.motor_asyncio import AsyncIOMotorClient
import sys
from pathlib import Path

# Import configuration
from config import (
    API_ID, API_HASH, BOT_TOKEN, MONGO_URI, DATABASE_NAME,
    SOURCE_CHANNEL_ID, ADMIN_IDS, BOT_USERNAME, LOG_LEVEL
)

# Import database
from database import Database

# Import handlers
from handlers.user_handlers import register_user_handlers
from handlers.admin_handlers import register_admin_handlers
from handlers.callback_handlers import register_callback_handlers

# Import utilities
from indexer import ChannelIndexer
from utils import setup_logging

# Setup logging
logger = setup_logging(LOG_LEVEL)


class SubtitleBot:
    """Main bot class with all initialization and lifecycle management"""
    
    def __init__(self):
        """Initialize bot instance"""
        self.app = None
        self.db = None
        self.indexer = None
        self.mongo_client = None
        
    async def initialize(self):
        """Initialize bot, database, and all components"""
        try:
            logger.info("🚀 Starting Telegram Subtitle Bot...")
            
            # Validate required environment variables
            if not all([API_ID, API_HASH, BOT_TOKEN]):
                logger.error("❌ Missing required credentials (API_ID, API_HASH, BOT_TOKEN)")
                logger.error("Please check your .env file")
                return False
                
            # Initialize Pyrogram client
            self.app = Client(
                "subtitle_bot",
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=BOT_TOKEN,
                workers=8,
                parse_mode="html"
            )
            
            logger.info("✅ Pyrogram client initialized")
            
            # Initialize MongoDB connection
            if MONGO_URI:
                try:
                    self.mongo_client = AsyncIOMotorClient(MONGO_URI)
                    # Test connection
                    await self.mongo_client.admin.command('ping')
                    
                    # Initialize database wrapper
                    self.db = Database(self.mongo_client, DATABASE_NAME)
                    await self.db.initialize()
                    
                    logger.info(f"✅ MongoDB connected: {DATABASE_NAME}")
                except Exception as e:
                    logger.error(f"❌ MongoDB connection failed: {e}")
                    logger.warning("⚠️ Bot will run without database (limited functionality)")
                    self.db = None
            else:
                logger.warning("⚠️ No MONGO_URI provided - running without database")
                self.db = None
            
            # Store database reference globally for handlers
            self.app.db = self.db
            
            # Initialize channel indexer
            if self.db and SOURCE_CHANNEL_ID:
                self.indexer = ChannelIndexer(self.app, self.db, SOURCE_CHANNEL_ID)
                logger.info("✅ Channel indexer initialized")
            else:
                logger.warning("⚠️ Channel indexer disabled (no database or source channel)")
                self.indexer = None
            
            # Register all handlers
            register_user_handlers(self.app)
            register_admin_handlers(self.app)
            register_callback_handlers(self.app)
            
            logger.info("✅ All handlers registered")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}", exc_info=True)
            return False
    
    async def start(self):
        """Start the bot"""
        try:
            # Initialize bot
            if not await self.initialize():
                logger.error("❌ Bot initialization failed")
                return
            
            # Start Pyrogram client
            await self.app.start()
            
            # Get bot information
            me = await self.app.get_me()
            logger.info(f"✅ Bot started: @{me.username} (ID: {me.id})")
            
            # Start channel indexer if available
            if self.indexer:
                asyncio.create_task(self.indexer.start())
                logger.info("✅ Channel indexer started")
            
            # Send startup notification to admins
            if self.db:
                startup_message = (
                    "🤖 <b>Bot Started Successfully!</b>\n\n"
                    f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"🤖 Bot: @{me.username}\n"
                    f"🆔 Bot ID: {me.id}\n"
                    f"🗄️ Database: Connected\n"
                    f"📡 Indexer: {'Active' if self.indexer else 'Disabled'}\n"
                    f"👥 Total Users: {await self.db.get_total_users()}\n"
                    f"📁 Total Files: {await self.db.get_total_files()}"
                )
                
                for admin_id in ADMIN_IDS:
                    try:
                        await self.app.send_message(admin_id, startup_message)
                    except Exception as e:
                        logger.warning(f"Could not notify admin {admin_id}: {e}")
            
            logger.info("🎉 Bot is now running and ready to serve!")
            logger.info("Press Ctrl+C to stop the bot")
            
            # Keep bot running
            await idle()
            
        except KeyboardInterrupt:
            logger.info("⚠️ Received stop signal")
        except Exception as e:
            logger.error(f"❌ Runtime error: {e}", exc_info=True)
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the bot gracefully"""
        try:
            logger.info("🛑 Stopping bot...")
            
            # Stop indexer
            if self.indexer:
                await self.indexer.stop()
                logger.info("✅ Channel indexer stopped")
            
            # Stop Pyrogram client
            if self.app:
                await self.app.stop()
                logger.info("✅ Bot stopped")
            
            # Close MongoDB connection
            if self.mongo_client:
                self.mongo_client.close()
                logger.info("✅ Database connection closed")
            
            logger.info("👋 Shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}", exc_info=True)


async def main():
    """Main entry point"""
    bot = SubtitleBot()
    await bot.start()


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required!")
        sys.exit(1)
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Run bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)

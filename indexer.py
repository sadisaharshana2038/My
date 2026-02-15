"""
Channel indexer for auto-indexing subtitle files
Monitors source channel and indexes new files automatically
"""

import logging
import asyncio
from datetime import datetime
from pyrogram import Client
from pyrogram.types import Message
from database import Database
from utils import clean_filename, format_file_size, is_subtitle_file
from config import UPDATE_CHANNEL_ID

logger = logging.getLogger(__name__)


class ChannelIndexer:
    """Auto-indexer for channel subtitle files"""
    
    def __init__(self, app: Client, db: Database, channel_id: int):
        """Initialize indexer"""
        self.app = app
        self.db = db
        self.channel_id = channel_id
        self.running = False
        
    async def start(self):
        """Start monitoring channel"""
        try:
            self.running = True
            logger.info(f"Channel indexer started for channel {self.channel_id}")
            
            # Index existing files on startup
            await self.index_existing_files()
            
        except Exception as e:
            logger.error(f"Error starting indexer: {e}")
    
    async def stop(self):
        """Stop indexer"""
        self.running = False
        logger.info("Channel indexer stopped")
    
    async def index_existing_files(self, limit: int = 100):
        """Index existing files from channel history"""
        try:
            logger.info(f"Indexing existing files from channel {self.channel_id}...")
            
            indexed = 0
            async for message in self.app.get_chat_history(self.channel_id, limit=limit):
                if message.document:
                    if await self.process_file(message):
                        indexed += 1
            
            logger.info(f"Indexed {indexed} existing files")
            return indexed
            
        except Exception as e:
            logger.error(f"Error indexing existing files: {e}")
            return 0
    
    async def process_file(self, message: Message) -> bool:
        """Process and index a subtitle file"""
        try:
            document = message.document
            
            # Check if it\'s a subtitle file
            if not is_subtitle_file(document.file_name):
                return False
            
            # Clean filename and extract metadata
            clean_title, year, quality = clean_filename(document.file_name)
            
            # Prepare file data
            file_data = {
                "file_id": document.file_id,
                "file_name": document.file_name,
                "file_size": document.file_size,
                "title": document.file_name.rsplit(\'.\', 1)[0],
                "clean_title": clean_title,
                "year": year,
                "quality": quality,
                "message_id": message.id,
                "channel_id": self.channel_id
            }
            
            # Add to database
            added = await self.db.add_file(file_data)
            
            if added:
                logger.info(f"Indexed new file: {clean_title}")
                
                # Send notification to update channel
                if UPDATE_CHANNEL_ID:
                    await self.send_update_notification(file_data)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return False
    
    async def send_update_notification(self, file_data: dict):
        """Send notification about new file to update channel"""
        try:
            notification = (
                "🆕 <b>New Subtitle Added!</b>\\n\\n"
                f"📁 <b>{file_data[\'clean_title\']}</b>\\n"
                f"📅 Year: {file_data[\'year\'] or \'N/A\'}\\n"
                f"🎬 Quality: {file_data[\'quality\'] or \'N/A\'}\\n"
                f"📦 Size: {format_file_size(file_data[\'file_size\'])}\\n\\n"
                "Search for it in the bot to download!"
            )
            
            await self.app.send_message(UPDATE_CHANNEL_ID, notification)
            
        except Exception as e:
            logger.error(f"Error sending update notification: {e}")

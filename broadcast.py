"""
Broadcast module for sending messages to all users
Advanced broadcasting with progress tracking and error handling
"""

import logging
import asyncio
from datetime import datetime
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from database import Database
from config import BROADCAST_BATCH_SIZE, BROADCAST_DELAY
from utils import batch_list, create_progress_bar, format_duration

logger = logging.getLogger(__name__)


class BroadcastManager:
    """Manage broadcast operations"""
    
    def __init__(self, client: Client, db: Database):
        """Initialize broadcast manager"""
        self.client = client
        self.db = db
    
    async def broadcast_message(
        self,
        message: Message,
        admin_id: int,
        progress_msg: Message = None
    ) -> dict:
        """
        Broadcast a message to all users
        
        Args:
            message: Message to broadcast
            admin_id: Admin user ID
            progress_msg: Message to update with progress
        
        Returns:
            Statistics dict
        """
        start_time = datetime.now()
        
        # Get all user IDs
        user_ids = await self.db.get_all_user_ids()
        total_users = len(user_ids)
        
        # Create broadcast record
        broadcast_id = await self.db.create_broadcast(admin_id, total_users)
        
        # Statistics
        stats = {
            "total": total_users,
            "success": 0,
            "failed": 0,
            "blocked": 0
        }
        
        # Process in batches
        for batch_num, batch in enumerate(batch_list(user_ids, BROADCAST_BATCH_SIZE), 1):
            # Send to batch
            for user_id in batch:
                try:
                    # Copy message based on type
                    if message.text:
                        await self.client.send_message(user_id, message.text)
                    elif message.photo:
                        await self.client.send_photo(
                            user_id,
                            message.photo.file_id,
                            caption=message.caption
                        )
                    elif message.video:
                        await self.client.send_video(
                            user_id,
                            message.video.file_id,
                            caption=message.caption
                        )
                    elif message.document:
                        await self.client.send_document(
                            user_id,
                            message.document.file_id,
                            caption=message.caption
                        )
                    elif message.animation:
                        await self.client.send_animation(
                            user_id,
                            message.animation.file_id,
                            caption=message.caption
                        )
                    
                    stats["success"] += 1
                    
                except (UserIsBlocked, InputUserDeactivated):
                    stats["blocked"] += 1
                except FloodWait as e:
                    logger.warning(f"FloodWait: {e.value} seconds")
                    await asyncio.sleep(e.value)
                    # Retry once
                    try:
                        await self.client.send_message(user_id, message.text or "Message")
                        stats["success"] += 1
                    except:
                        stats["failed"] += 1
                except Exception as e:
                    logger.error(f"Broadcast error for user {user_id}: {e}")
                    stats["failed"] += 1
            
            # Update database stats
            await self.db.update_broadcast_stats(
                broadcast_id,
                success=len([u for u in batch if u]),  # Batch success count
            )
            
            # Update progress message
            if progress_msg and batch_num % 5 == 0:  # Update every 5 batches
                try:
                    from config import get_message
                    
                    progress_text = get_message(
                        "en",
                        "broadcast_progress",
                        success=stats["success"],
                        failed=stats["failed"],
                        blocked=stats["blocked"],
                        remaining=total_users - stats["success"] - stats["failed"] - stats["blocked"]
                    )
                    
                    # Add progress bar
                    completed = stats["success"] + stats["failed"] + stats["blocked"]
                    progress_bar = create_progress_bar(completed, total_users)
                    progress_text += f"\\n\\n{progress_bar}"
                    
                    await progress_msg.edit_text(progress_text)
                except:
                    pass
            
            # Delay between batches
            await asyncio.sleep(BROADCAST_DELAY)
        
        # Mark broadcast complete
        await self.db.complete_broadcast(broadcast_id)
        
        # Calculate time taken
        end_time = datetime.now()
        time_taken = format_duration(int((end_time - start_time).total_seconds()))
        stats["time_taken"] = time_taken
        
        return stats

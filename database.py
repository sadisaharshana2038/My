"""
Database module for Telegram Subtitle Bot
Complete MongoDB operations with proper error handling
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError, PyMongoError
from config import POINTS_PER_DOWNLOAD, POINTS_PER_REQUEST, RANKS

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database wrapper with all operations"""
    
    def __init__(self, client: AsyncIOMotorClient, db_name: str):
        """Initialize database"""
        self.client = client
        self.db: AsyncIOMotorDatabase = client[db_name]
        
        # Collections
        self.users = self.db.users
        self.files = self.db.files
        self.requests = self.db.requests
        self.searches = self.db.searches
        self.broadcasts = self.db.broadcasts
        
    async def initialize(self):
        """Create indexes for better performance"""
        try:
            # Users indexes
            await self.users.create_index("user_id", unique=True)
            await self.users.create_index([("downloads", -1)])
            await self.users.create_index([("points", -1)])
            
            # Files indexes
            await self.files.create_index("file_id", unique=True)
            await self.files.create_index([("clean_title", "text")])
            await self.files.create_index([("downloads", -1)])
            await self.files.create_index([("added_at", -1)])
            
            # Requests indexes
            await self.requests.create_index([("user_id", 1), ("tmdb_id", 1)])
            await self.requests.create_index([("status", 1)])
            await self.requests.create_index([("created_at", -1)])
            
            # Searches indexes
            await self.searches.create_index("query")
            await self.searches.create_index([("count", -1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    # ==========================================
    # USER OPERATIONS
    # ==========================================
    
    async def add_user(self, user_id: int, username: str = None, 
                       first_name: str = None, language: str = "en") -> bool:
        """Add new user to database"""
        try:
            user_data = {
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "language": language,
                "downloads": 0,
                "points": 0,
                "requests_made": 0,
                "total_searches": 0,
                "is_banned": False,
                "joined_at": datetime.now(),
                "last_active": datetime.now()
            }
            
            await self.users.insert_one(user_data)
            logger.info(f"New user added: {user_id} (@{username})")
            return True
            
        except DuplicateKeyError:
            # User already exists, update last active
            await self.update_user_activity(user_id)
            return False
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data"""
        try:
            user = await self.users.find_one({"user_id": user_id})
            return user
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def update_user_activity(self, user_id: int):
        """Update user's last active timestamp"""
        try:
            await self.users.update_one(
                {"user_id": user_id},
                {"$set": {"last_active": datetime.now()}}
            )
        except Exception as e:
            logger.error(f"Error updating user activity {user_id}: {e}")
    
    async def update_user_language(self, user_id: int, language: str):
        """Update user's preferred language"""
        try:
            await self.users.update_one(
                {"user_id": user_id},
                {"$set": {"language": language}}
            )
            logger.info(f"User {user_id} language updated to {language}")
        except Exception as e:
            logger.error(f"Error updating user language {user_id}: {e}")
    
    async def increment_user_downloads(self, user_id: int) -> int:
        """Increment user's download count and add points"""
        try:
            result = await self.users.find_one_and_update(
                {"user_id": user_id},
                {
                    "$inc": {
                        "downloads": 1,
                        "points": POINTS_PER_DOWNLOAD
                    },
                    "$set": {"last_active": datetime.now()}
                },
                return_document=True
            )
            
            if result:
                return result.get("downloads", 0)
            return 0
            
        except Exception as e:
            logger.error(f"Error incrementing downloads for {user_id}: {e}")
            return 0
    
    async def increment_user_searches(self, user_id: int):
        """Increment user's search count"""
        try:
            await self.users.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"total_searches": 1},
                    "$set": {"last_active": datetime.now()}
                }
            )
        except Exception as e:
            logger.error(f"Error incrementing searches for {user_id}: {e}")
    
    async def increment_user_requests(self, user_id: int):
        """Increment user's request count and add points"""
        try:
            await self.users.update_one(
                {"user_id": user_id},
                {
                    "$inc": {
                        "requests_made": 1,
                        "points": POINTS_PER_REQUEST
                    },
                    "$set": {"last_active": datetime.now()}
                }
            )
        except Exception as e:
            logger.error(f"Error incrementing requests for {user_id}: {e}")
    
    async def get_user_rank(self, downloads: int) -> Dict:
        """Get user's rank based on downloads"""
        for rank_key, rank_data in RANKS.items():
            if rank_data["min"] <= downloads <= rank_data["max"]:
                return rank_data
        return RANKS["beginner"]
    
    async def get_total_users(self) -> int:
        """Get total number of users"""
        try:
            return await self.users.count_documents({})
        except Exception as e:
            logger.error(f"Error getting total users: {e}")
            return 0
    
    async def get_all_user_ids(self) -> List[int]:
        """Get list of all user IDs"""
        try:
            cursor = self.users.find({}, {"user_id": 1})
            users = await cursor.to_list(length=None)
            return [user["user_id"] for user in users]
        except Exception as e:
            logger.error(f"Error getting all user IDs: {e}")
            return []
    
    async def get_top_users(self, limit: int = 10) -> List[Dict]:
        """Get top users by downloads"""
        try:
            cursor = self.users.find(
                {},
                {
                    "user_id": 1,
                    "username": 1,
                    "first_name": 1,
                    "downloads": 1,
                    "points": 1
                }
            ).sort("downloads", -1).limit(limit)
            
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Error getting top users: {e}")
            return []
    
    # ==========================================
    # FILE OPERATIONS
    # ==========================================
    
    async def add_file(self, file_data: Dict) -> bool:
        """Add new file to database"""
        try:
            # Add metadata
            file_data["downloads"] = 0
            file_data["added_at"] = datetime.now()
            
            await self.files.insert_one(file_data)
            logger.info(f"New file added: {file_data.get('file_name')}")
            return True
            
        except DuplicateKeyError:
            logger.debug(f"File already exists: {file_data.get('file_id')}")
            return False
        except Exception as e:
            logger.error(f"Error adding file: {e}")
            return False
    
    async def get_file(self, file_id: str) -> Optional[Dict]:
        """Get file by file_id"""
        try:
            return await self.files.find_one({"file_id": file_id})
        except Exception as e:
            logger.error(f"Error getting file {file_id}: {e}")
            return None
    
    async def search_files(self, query: str, skip: int = 0, 
                          limit: int = 10) -> Tuple[List[Dict], int]:
        """
        Search files by clean_title using text search
        Returns: (results, total_count)
        """
        try:
            # Create text search query
            search_query = {"$text": {"$search": query}}
            
            # Get total count
            total = await self.files.count_documents(search_query)
            
            # Get paginated results
            cursor = self.files.find(search_query).skip(skip).limit(limit)
            results = await cursor.to_list(length=limit)
            
            return results, total
            
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return [], 0
    
    async def fuzzy_search_files(self, query: str) -> List[Dict]:
        """
        Fuzzy search using regex (fallback when text search fails)
        Returns up to 50 results
        """
        try:
            # Create regex pattern (case-insensitive)
            pattern = {"$regex": query, "$options": "i"}
            
            cursor = self.files.find({
                "$or": [
                    {"clean_title": pattern},
                    {"title": pattern},
                    {"file_name": pattern}
                ]
            }).limit(50)
            
            return await cursor.to_list(length=50)
            
        except Exception as e:
            logger.error(f"Error in fuzzy search: {e}")
            return []
    
    async def increment_file_downloads(self, file_id: str):
        """Increment file's download count"""
        try:
            await self.files.update_one(
                {"file_id": file_id},
                {"$inc": {"downloads": 1}}
            )
        except Exception as e:
            logger.error(f"Error incrementing file downloads {file_id}: {e}")
    
    async def get_total_files(self) -> int:
        """Get total number of files"""
        try:
            return await self.files.count_documents({})
        except Exception as e:
            logger.error(f"Error getting total files: {e}")
            return 0
    
    async def get_total_downloads(self) -> int:
        """Get total downloads across all files"""
        try:
            pipeline = [{"$group": {"_id": None, "total": {"$sum": "$downloads"}}}]
            result = await self.files.aggregate(pipeline).to_list(1)
            return result[0]["total"] if result else 0
        except Exception as e:
            logger.error(f"Error getting total downloads: {e}")
            return 0
    
    async def get_top_files(self, limit: int = 5) -> List[Dict]:
        """Get top downloaded files"""
        try:
            cursor = self.files.find(
                {},
                {
                    "file_name": 1,
                    "clean_title": 1,
                    "downloads": 1
                }
            ).sort("downloads", -1).limit(limit)
            
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Error getting top files: {e}")
            return []
    
    async def find_duplicates(self) -> List[List[Dict]]:
        """Find duplicate files by clean_title"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$clean_title",
                        "count": {"$sum": 1},
                        "files": {"$push": "$$ROOT"}
                    }
                },
                {"$match": {"count": {"$gt": 1}}}
            ]
            
            cursor = self.files.aggregate(pipeline)
            duplicates = await cursor.to_list(length=None)
            
            return [dup["files"] for dup in duplicates]
            
        except Exception as e:
            logger.error(f"Error finding duplicates: {e}")
            return []
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file from database"""
        try:
            result = await self.files.delete_one({"file_id": file_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            return False
    
    # ==========================================
    # REQUEST OPERATIONS
    # ==========================================
    
    async def create_request(self, request_data: Dict) -> Optional[str]:
        """Create new subtitle request"""
        try:
            # Check if already requested
            existing = await self.requests.find_one({
                "user_id": request_data["user_id"],
                "tmdb_id": request_data["tmdb_id"],
                "status": "pending"
            })
            
            if existing:
                return None
            
            # Add metadata
            request_data["status"] = "pending"
            request_data["created_at"] = datetime.now()
            request_data["fulfilled_at"] = None
            
            result = await self.requests.insert_one(request_data)
            logger.info(f"New request created: {request_data.get('title')}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating request: {e}")
            return None
    
    async def get_request(self, request_id: str) -> Optional[Dict]:
        """Get request by ID"""
        try:
            from bson.objectid import ObjectId
            return await self.requests.find_one({"_id": ObjectId(request_id)})
        except Exception as e:
            logger.error(f"Error getting request: {e}")
            return None
    
    async def update_request_status(self, request_id: str, status: str) -> bool:
        """Update request status (fulfilled/rejected)"""
        try:
            from bson.objectid import ObjectId
            
            update_data = {
                "status": status,
                "fulfilled_at": datetime.now() if status == "fulfilled" else None
            }
            
            result = await self.requests.update_one(
                {"_id": ObjectId(request_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating request status: {e}")
            return False
    
    async def get_pending_requests_count(self) -> int:
        """Get count of pending requests"""
        try:
            return await self.requests.count_documents({"status": "pending"})
        except Exception as e:
            logger.error(f"Error getting pending requests: {e}")
            return 0
    
    async def get_fulfilled_requests_count(self) -> int:
        """Get count of fulfilled requests"""
        try:
            return await self.requests.count_documents({"status": "fulfilled"})
        except Exception as e:
            logger.error(f"Error getting fulfilled requests: {e}")
            return 0
    
    # ==========================================
    # SEARCH OPERATIONS
    # ==========================================
    
    async def log_search(self, query: str, user_id: int):
        """Log search query for analytics"""
        try:
            await self.searches.update_one(
                {"query": query.lower()},
                {
                    "$inc": {"count": 1},
                    "$addToSet": {"users": user_id},
                    "$set": {"last_searched": datetime.now()}
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error logging search: {e}")
    
    async def get_total_searches(self) -> int:
        """Get total number of searches"""
        try:
            pipeline = [{"$group": {"_id": None, "total": {"$sum": "$count"}}}]
            result = await self.searches.aggregate(pipeline).to_list(1)
            return result[0]["total"] if result else 0
        except Exception as e:
            logger.error(f"Error getting total searches: {e}")
            return 0
    
    async def get_popular_searches(self, limit: int = 10) -> List[Dict]:
        """Get most popular search queries"""
        try:
            cursor = self.searches.find(
                {},
                {"query": 1, "count": 1}
            ).sort("count", -1).limit(limit)
            
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Error getting popular searches: {e}")
            return []
    
    # ==========================================
    # BROADCAST OPERATIONS
    # ==========================================
    
    async def create_broadcast(self, admin_id: int, total_users: int) -> str:
        """Create broadcast record"""
        try:
            broadcast_data = {
                "admin_id": admin_id,
                "total_users": total_users,
                "success": 0,
                "failed": 0,
                "blocked": 0,
                "status": "in_progress",
                "created_at": datetime.now(),
                "completed_at": None
            }
            
            result = await self.broadcasts.insert_one(broadcast_data)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating broadcast: {e}")
            return ""
    
    async def update_broadcast_stats(self, broadcast_id: str, 
                                    success: int = 0, failed: int = 0, 
                                    blocked: int = 0):
        """Update broadcast statistics"""
        try:
            from bson.objectid import ObjectId
            
            await self.broadcasts.update_one(
                {"_id": ObjectId(broadcast_id)},
                {"$inc": {
                    "success": success,
                    "failed": failed,
                    "blocked": blocked
                }}
            )
        except Exception as e:
            logger.error(f"Error updating broadcast stats: {e}")
    
    async def complete_broadcast(self, broadcast_id: str):
        """Mark broadcast as complete"""
        try:
            from bson.objectid import ObjectId
            
            await self.broadcasts.update_one(
                {"_id": ObjectId(broadcast_id)},
                {"$set": {
                    "status": "completed",
                    "completed_at": datetime.now()
                }}
            )
        except Exception as e:
            logger.error(f"Error completing broadcast: {e}")
    
    # ==========================================
    # BACKUP OPERATIONS
    # ==========================================
    
    async def create_backup(self) -> Dict:
        """Create complete database backup"""
        try:
            backup = {
                "timestamp": datetime.now().isoformat(),
                "users": await self.users.find({}).to_list(length=None),
                "files": await self.files.find({}).to_list(length=None),
                "requests": await self.requests.find({}).to_list(length=None),
                "searches": await self.searches.find({}).to_list(length=None),
                "broadcasts": await self.broadcasts.find({}).to_list(length=None)
            }
            
            logger.info("Database backup created successfully")
            return backup
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return {}

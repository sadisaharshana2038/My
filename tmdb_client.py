"""
TMDB API client for movie/TV show information
Used in request system to fetch movie details
"""

import logging
import aiohttp
from typing import List, Dict, Optional
from config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE
from utils import truncate_text

logger = logging.getLogger(__name__)


class TMDBClient:
    """The Movie Database API client"""
    
    def __init__(self):
        """Initialize TMDB client"""
        self.api_key = TMDB_API_KEY
        self.base_url = TMDB_BASE_URL
        self.image_base = TMDB_IMAGE_BASE
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def search_multi(self, query: str) -> List[Dict]:
        """
        Search for movies and TV shows
        
        Args:
            query: Search query
        
        Returns:
            List of search results (max 10)
        """
        try:
            if not self.api_key:
                logger.warning("TMDB API key not configured")
                return []
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.base_url}/search/multi"
            params = {
                "api_key": self.api_key,
                "query": query,
                "page": 1
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])
                    
                    # Filter to movies and TV shows only
                    filtered = [
                        r for r in results 
                        if r.get("media_type") in ["movie", "tv"]
                    ]
                    
                    return filtered[:10]  # Return max 10 results
                else:
                    logger.error(f"TMDB API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching TMDB: {e}")
            return []
    
    async def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """
        Get detailed information about a movie
        
        Args:
            movie_id: TMDB movie ID
        
        Returns:
            Movie details dict or None
        """
        try:
            if not self.api_key or not self.session:
                return None
            
            url = f"{self.base_url}/movie/{movie_id}"
            params = {"api_key": self.api_key}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._format_movie_details(data)
                return None
                
        except Exception as e:
            logger.error(f"Error getting movie details: {e}")
            return None
    
    async def get_tv_details(self, tv_id: int) -> Optional[Dict]:
        """
        Get detailed information about a TV show
        
        Args:
            tv_id: TMDB TV show ID
        
        Returns:
            TV show details dict or None
        """
        try:
            if not self.api_key or not self.session:
                return None
            
            url = f"{self.base_url}/tv/{tv_id}"
            params = {"api_key": self.api_key}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._format_tv_details(data)
                return None
                
        except Exception as e:
            logger.error(f"Error getting TV details: {e}")
            return None
    
    def _format_movie_details(self, data: Dict) -> Dict:
        """Format movie data for display"""
        return {
            "tmdb_id": data.get("id"),
            "title": data.get("title", "Unknown"),
            "year": data.get("release_date", "")[:4] if data.get("release_date") else None,
            "rating": round(data.get("vote_average", 0), 1),
            "runtime": data.get("runtime", 0),
            "genres": ", ".join([g["name"] for g in data.get("genres", [])]),
            "overview": truncate_text(data.get("overview", "No description available"), 300),
            "poster_url": f"{self.image_base}{data.get(\'poster_path\')}" if data.get("poster_path") else None,
            "media_type": "movie"
        }
    
    def _format_tv_details(self, data: Dict) -> Dict:
        """Format TV show data for display"""
        return {
            "tmdb_id": data.get("id"),
            "title": data.get("name", "Unknown"),
            "year": data.get("first_air_date", "")[:4] if data.get("first_air_date") else None,
            "rating": round(data.get("vote_average", 0), 1),
            "runtime": data.get("episode_run_time", [0])[0] if data.get("episode_run_time") else 0,
            "genres": ", ".join([g["name"] for g in data.get("genres", [])]),
            "overview": truncate_text(data.get("overview", "No description available"), 300),
            "poster_url": f"{self.image_base}{data.get(\'poster_path\')}" if data.get("poster_path") else None,
            "media_type": "tv"
        }
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()

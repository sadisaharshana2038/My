"""
Utility functions for Telegram Subtitle Bot
File cleaning, formatting, logging setup, and helper functions
"""

import re
import logging
from datetime import datetime
from typing import Tuple, Optional
from pathlib import Path


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Logger instance
    """
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Log filename with date
    log_file = log_dir / f"bot_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def clean_filename(filename: str) -> Tuple[str, Optional[int], Optional[str]]:
    """
    Clean filename by removing unwanted text and extracting metadata
    
    Args:
        filename: Original filename
    
    Returns:
        Tuple of (clean_title, year, quality)
    
    Examples:
        "Avatar (2009) 1080p @MovieChannel.srt" -> ("Avatar", 2009, "1080p")
        "[t.me/channel] Inception.2010.720p.srt" -> ("Inception", 2010, "720p")
    """
    try:
        # Remove file extension
        name = filename.rsplit('.', 1)[0] if '.' in filename else filename
        
        # Remove common unwanted patterns
        patterns_to_remove = [
            r'@\w+',  # @username
            r't\.me/\w+',  # t.me/channel
            r'https?://\S+',  # URLs
            r'\[.*?\]',  # [text]
            r'\{.*?\}',  # {text}
            r'(?i)bluray',
            r'(?i)webrip',
            r'(?i)web-dl',
            r'(?i)brrip',
            r'(?i)hdrip',
            r'(?i)x264',
            r'(?i)x265',
            r'(?i)hevc',
            r'(?i)ac3',
            r'(?i)aac',
            r'(?i)subtitle',
            r'(?i)subtitles',
            r'(?i)subs',
            r'(?i)sinhala',
            r'(?i)english',
        ]
        
        for pattern in patterns_to_remove:
            name = re.sub(pattern, '', name)
        
        # Extract year (1900-2099)
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', name)
        year = int(year_match.group(1)) if year_match else None
        
        # Extract quality
        quality_match = re.search(r'\b(4K|2160p|1080p|720p|480p|360p)\b', name, re.IGNORECASE)
        quality = quality_match.group(1).upper() if quality_match else None
        
        # Remove year and quality from name
        if year:
            name = name.replace(str(year), '')
        if quality:
            name = re.sub(re.escape(quality), '', name, flags=re.IGNORECASE)
        
        # Remove parentheses content if empty or contains only unwanted chars
        name = re.sub(r'\([^)]*\)', '', name)
        
        # Remove multiple dots and replace with spaces
        name = name.replace('.', ' ').replace('_', ' ').replace('-', ' ')
        
        # Remove multiple spaces
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Capitalize each word
        name = name.title()
        
        return name, year, quality
        
    except Exception as e:
        logging.error(f"Error cleaning filename: {e}")
        return filename, None, None


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: File size in bytes
    
    Returns:
        Formatted string (e.g., "125KB", "2.5MB")
    """
    try:
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.0f}KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f}MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f}GB"
    except:
        return "Unknown"


def format_duration(seconds: int) -> str:
    """
    Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "2h 30m", "45s")
    """
    try:
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    except:
        return "Unknown"


def format_timestamp(dt: datetime) -> str:
    """
    Format datetime in human-readable format
    
    Args:
        dt: Datetime object
    
    Returns:
        Formatted string (e.g., "2 hours ago", "3 days ago")
    """
    try:
        now = datetime.now()
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        elif seconds < 2592000:
            weeks = int(seconds / 604800)
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        elif seconds < 31536000:
            months = int(seconds / 2592000)
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = int(seconds / 31536000)
            return f"{years} year{'s' if years != 1 else ''} ago"
            
    except:
        return dt.strftime("%Y-%m-%d")


def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """
    Create a progress bar
    
    Args:
        current: Current progress value
        total: Total value
        length: Length of progress bar
    
    Returns:
        Progress bar string (e.g., "▰▰▰▰▰▱▱▱▱▱ 50%")
    """
    try:
        if total == 0:
            return "▱" * length + " 0%"
        
        percent = int((current / total) * 100)
        filled = int((current / total) * length)
        empty = length - filled
        
        bar = "▰" * filled + "▱" * empty
        return f"{bar} {percent}%"
        
    except:
        return "▱" * length + " 0%"


def sanitize_query(query: str) -> str:
    """
    Sanitize search query
    
    Args:
        query: Raw search query
    
    Returns:
        Sanitized query
    """
    try:
        # Remove special characters
        query = re.sub(r'[^\w\s]', '', query)
        
        # Remove multiple spaces
        query = re.sub(r'\s+', ' ', query)
        
        # Trim and lowercase
        query = query.strip().lower()
        
        return query
        
    except:
        return query


def truncate_text(text: str, max_length: int = 300) -> str:
    """
    Truncate text to max length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
    
    Returns:
        Truncated text with ellipsis if needed
    """
    try:
        if len(text) <= max_length:
            return text
        
        return text[:max_length].rsplit(' ', 1)[0] + "..."
        
    except:
        return text


def extract_telegram_file_id(url: str) -> Optional[Tuple[str, int]]:
    """
    Extract channel username and message ID from Telegram link
    
    Args:
        url: Telegram link (e.g., https://t.me/channel/123)
    
    Returns:
        Tuple of (channel_username, message_id) or None
    
    Examples:
        "https://t.me/moviechannel/123" -> ("moviechannel", 123)
        "t.me/updates/456" -> ("updates", 456)
    """
    try:
        # Pattern for t.me links
        pattern = r't\.me/([^/]+)/(\d+)'
        match = re.search(pattern, url)
        
        if match:
            channel = match.group(1)
            message_id = int(match.group(2))
            return channel, message_id
        
        return None
        
    except Exception as e:
        logging.error(f"Error extracting Telegram file ID: {e}")
        return None


def is_subtitle_file(filename: str) -> bool:
    """
    Check if file is a subtitle file
    
    Args:
        filename: Filename to check
    
    Returns:
        True if subtitle file, False otherwise
    """
    from config import SUBTITLE_EXTENSIONS
    
    try:
        extension = filename.lower().split('.')[-1]
        return f".{extension}" in SUBTITLE_EXTENSIONS
    except:
        return False


def escape_html(text: str) -> str:
    """
    Escape HTML special characters
    
    Args:
        text: Text to escape
    
    Returns:
        Escaped text safe for HTML
    """
    try:
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
        
    except:
        return text


def get_user_display_name(user) -> str:
    """
    Get display name for user
    
    Args:
        user: Pyrogram User object or dict
    
    Returns:
        User display name
    """
    try:
        if hasattr(user, 'first_name'):
            name = user.first_name
            if user.last_name:
                name += f" {user.last_name}"
        elif isinstance(user, dict):
            name = user.get('first_name', 'Unknown')
            if user.get('last_name'):
                name += f" {user['last_name']}"
        else:
            name = "Unknown"
        
        return escape_html(name)
        
    except:
        return "Unknown"


def validate_url(url: str) -> bool:
    """
    Validate if string is a valid URL
    
    Args:
        url: URL string to validate
    
    Returns:
        True if valid URL, False otherwise
    """
    try:
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
    except:
        return False


def parse_telegram_image_url(url: str) -> Optional[str]:
    """
    Parse Telegram image URL to get file reference
    
    Args:
        url: Telegram image URL
    
    Returns:
        Parsed URL or None if invalid
    """
    try:
        if not url:
            return None
        
        # Check if it's a Telegram link
        if 't.me/' in url or 'telegram.me/' in url:
            return url
        
        # Check if it's a Telegraph link
        if 'telegra.ph/' in url:
            return url
        
        # Check if it's a valid URL
        if validate_url(url):
            return url
        
        return None
        
    except:
        return None


def calculate_fuzzy_score(query: str, title: str) -> int:
    """
    Calculate fuzzy matching score between query and title
    Simple implementation without external library
    
    Args:
        query: Search query
        title: Title to match against
    
    Returns:
        Score from 0 to 100
    """
    try:
        query = query.lower()
        title = title.lower()
        
        # Exact match
        if query == title:
            return 100
        
        # Substring match
        if query in title:
            return 90
        
        # Word match
        query_words = set(query.split())
        title_words = set(title.split())
        
        if query_words & title_words:
            # Calculate overlap percentage
            overlap = len(query_words & title_words)
            total = len(query_words | title_words)
            return int((overlap / total) * 80)
        
        # Character overlap
        query_chars = set(query)
        title_chars = set(title)
        
        overlap = len(query_chars & title_chars)
        total = len(query_chars | title_chars)
        
        return int((overlap / total) * 60)
        
    except:
        return 0


def batch_list(items: list, batch_size: int):
    """
    Split list into batches
    
    Args:
        items: List to split
        batch_size: Size of each batch
    
    Yields:
        Batches of items
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]

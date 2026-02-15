# 🎬 Professional Telegram Subtitle Bot

A fully-featured, production-ready Telegram bot for indexing, searching, and distributing subtitle files with advanced features.

## ✨ Features

### Core Features
- 🔍 **Smart Search**: Fuzzy matching with pagination (10 results per page, max 5 pages)
- 📁 **Auto-Indexing**: Automatically indexes subtitle files from source channel
- 🌐 **Dual Language**: Full support for English and Sinhala
- 🎯 **Request System**: TMDB integration for subtitle requests with full movie details
- 📊 **Statistics**: Comprehensive tracking of downloads, searches, and user activity
- 🏆 **Leaderboard**: Rank system with points for downloads and requests
- 📢 **Broadcasting**: Advanced broadcast system with progress tracking
- 🔒 **Force Subscribe**: Optional channel subscription requirement

### User Features
- 👤 **User Profiles**: Track downloads, points, and rank
- 💎 **Points System**: Earn points for downloads (1pt) and requests (2pts)
- 🏅 **Rank System**: 6 ranks from Beginner (🥉) to Legend (🌟)
- 🎬 **Movie Details**: Full TMDB integration showing posters, ratings, genres, and overviews
- ⏱️ **Activity Tracking**: Last active timestamps and join dates

### Admin Features
- 📊 **Detailed Statistics**: Total users, files, downloads, searches
- 📢 **Bulk Broadcast**: Send messages to all users with live progress
- 🔄 **Channel Indexing**: Manual trigger for re-indexing
- 💾 **Database Backup**: One-click JSON backup export
- 🔍 **Duplicate Scanner**: Find and remove duplicate files
- 👥 **Request Management**: Approve or reject user requests
- 📈 **Analytics**: Top files, top users, popular searches

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MongoDB database
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org))
- TMDB API Key (from [themoviedb.org](https://www.themoviedb.org/settings/api))

### Installation

1. **Clone and Setup**
```bash
git clone <your-repo-url>
cd telegram_subtitle_bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials
nano .env
```

3. **Required Environment Variables**
```env
API_ID=12345678
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
BOT_USERNAME=YourBotUsername
MONGO_URI=mongodb://localhost:27017
SOURCE_CHANNEL_ID=-1001234567890
ADMIN_IDS=123456789,987654321
TMDB_API_KEY=your_tmdb_key
```

4. **Run the Bot**
```bash
python main.py
```

## 📋 Configuration

### Required Settings
- **API_ID & API_HASH**: Get from https://my.telegram.org
- **BOT_TOKEN**: Create bot with @BotFather
- **MONGO_URI**: MongoDB connection string
- **SOURCE_CHANNEL_ID**: Channel to index files from (use negative ID)
- **ADMIN_IDS**: Comma-separated admin user IDs

### Optional Settings
- **UPDATE_CHANNEL_ID**: Channel for new file notifications
- **ADMIN_CHANNEL_ID**: Channel for admin notifications
- **FORCE_SUB_CHANNEL**: Channel users must join
- **TMDB_API_KEY**: For movie details in request system
- **Custom Images**: Support both Telegraph and Telegram links

## 🎯 Usage

### For Users

**Search Subtitles**
```
Just type: Avatar
```
Bot will show paginated results with download buttons.

**Request Subtitle**
```
/request
Type: Inception
```
Bot searches TMDB, shows full movie details with poster, you click request button.

**View Profile**
```
/profile
```
Shows your stats, points, rank, and activity.

**View Leaderboard**
```
/leaderboard
```
See top 10 users by downloads.

**Change Language**
```
/language
```
Switch between English and Sinhala.

### For Admins

**View Statistics**
```
/stats
```
Comprehensive bot statistics with top files and users.

**Broadcast Message**
```
/broadcast
Then send any message (text, photo, video, document)
```
Sends to all users with live progress tracking.

**Index Channel**
```
/index
```
Manually trigger indexing of source channel.

**Backup Database**
```
/backup
```
Creates and sends JSON backup file.

**Scan Duplicates**
```
/scan
```
Finds duplicate files by clean title.

## 🏗️ Architecture

### Project Structure
```
telegram_subtitle_bot/
├── main.py                 # Bot entry point
├── config.py              # Configuration & messages
├── database.py            # MongoDB operations
├── utils.py               # Helper functions
├── indexer.py             # Channel file indexing
├── image_handler.py       # Telegram/Telegraph image handling
├── keyboards.py           # Inline keyboard layouts
├── force_subscribe.py     # Subscription checking
├── tmdb_client.py         # TMDB API integration
├── broadcast.py           # Broadcast system
├── handlers/
│   ├── user_handlers.py   # User commands
│   ├── admin_handlers.py  # Admin commands
│   └── callback_handlers.py # Button callbacks
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
├── Procfile              # Heroku deployment
├── runtime.txt           # Python version
└── README.md             # Documentation
```

### Database Schema

**users**
```python
{
    "user_id": int,
    "username": str,
    "first_name": str,
    "language": "en" | "si",
    "downloads": int,
    "points": int,
    "requests_made": int,
    "total_searches": int,
    "is_banned": bool,
    "joined_at": datetime,
    "last_active": datetime
}
```

**files**
```python
{
    "file_id": str,
    "file_name": str,
    "file_size": int,
    "title": str,
    "clean_title": str,
    "year": int,
    "quality": str,
    "message_id": int,
    "channel_id": int,
    "downloads": int,
    "added_at": datetime
}
```

**requests**
```python
{
    "user_id": int,
    "username": str,
    "title": str,
    "year": int,
    "media_type": "movie" | "tv",
    "tmdb_id": int,
    "poster_url": str,
    "rating": float,
    "genres": list,
    "overview": str,
    "status": "pending" | "fulfilled" | "rejected",
    "created_at": datetime,
    "fulfilled_at": datetime
}
```

## 🎨 Features in Detail

### Search System
- Text search with MongoDB text indexes
- Fallback to fuzzy matching (70% threshold)
- Pagination: 10 results per page, max 5 pages (50 total)
- Button format: `[Size | Name | Year]`
- Real-time search query logging

### Request System
- TMDB API integration for movie data
- Shows full movie details: poster, rating, runtime, genres, overview
- Admin approval workflow with notifications
- User notifications on fulfillment/rejection
- Points reward system

### Auto-Indexing
- Real-time monitoring of source channel
- Automatic file cleaning (removes @username, t.me links, brackets)
- Extracts year and quality automatically
- Duplicate detection
- Update channel notifications

### Broadcasting
- Supports all message types: text, photo, video, document, animation
- Batch processing (50 users per batch)
- Live progress bar
- Statistics: success, failed, blocked
- Error recovery and retry logic

### Rank System
```
🥉 Beginner: 0-9 downloads
🥈 Regular User: 10-49 downloads
🥇 Active User: 50-99 downloads
💎 Premium User: 100-499 downloads
👑 VIP User: 500-999 downloads
🌟 Legend: 1000+ downloads
```

## 🚀 Deployment

### Heroku Deployment

1. **Create Heroku App**
```bash
heroku create your-subtitle-bot
```

2. **Add MongoDB**
```bash
heroku addons:create mongodb-atlas:sandbox
```

3. **Set Environment Variables**
```bash
heroku config:set API_ID=your_api_id
heroku config:set API_HASH=your_api_hash
heroku config:set BOT_TOKEN=your_bot_token
# ... set all other variables
```

4. **Deploy**
```bash
git push heroku main
```

5. **Scale Worker**
```bash
heroku ps:scale worker=1
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

```bash
docker build -t subtitle-bot .
docker run -d --env-file .env subtitle-bot
```

### VPS Deployment

```bash
# Install dependencies
sudo apt update
sudo apt install python3.11 python3-pip mongodb

# Setup bot
cd /opt
git clone <repo>
cd telegram_subtitle_bot
pip3 install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/subtitle-bot.service
```

```ini
[Unit]
Description=Telegram Subtitle Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/opt/telegram_subtitle_bot
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable subtitle-bot
sudo systemctl start subtitle-bot
```

## 📊 Monitoring

### Logs
```bash
# View today's log
tail -f logs/bot_$(date +%Y%m%d).log

# Search errors
grep ERROR logs/bot_*.log
```

### Health Checks
The bot sends startup notifications to admins and logs all activities.

## 🔧 Troubleshooting

### Bot Not Starting
- Check Python version: `python --version` (requires 3.11+)
- Verify environment variables in .env
- Check MongoDB connection
- Review logs in `logs/` directory

### Search Not Working
- Ensure MongoDB text indexes are created
- Check if files are indexed: Check database or use /stats
- Verify SOURCE_CHANNEL_ID is correct

### TMDB Requests Failing
- Verify TMDB_API_KEY is valid
- Check API quota limits
- Review logs for specific error messages

### Images Not Loading
- Verify image URLs are accessible
- Support both Telegraph and Telegram links
- Bot gracefully falls back to text if image fails

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Make your changes with proper documentation
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [Pyrogram](https://docs.pyrogram.org/) - MTProto Telegram framework
- [MongoDB](https://www.mongodb.com/) - Database
- [TMDB](https://www.themoviedb.org/) - Movie database API

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact administrators via bot
- Check logs for error details

## 🎯 Roadmap

- [ ] Additional language support
- [ ] Advanced search filters
- [ ] User preferences system
- [ ] Automated quality checks
- [ ] Integration with more movie databases
- [ ] API for external access

---

Made with ❤️ for the subtitle community

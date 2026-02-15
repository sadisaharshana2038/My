# 🚀 Quick Start Guide

Get your Telegram Subtitle Bot running in 5 minutes!

## Prerequisites Checklist

Before starting, make sure you have:
- [ ] Python 3.11 or higher installed
- [ ] MongoDB installed locally OR MongoDB Atlas account
- [ ] Telegram account
- [ ] 15 minutes of time

## Step 1: Get Telegram Credentials (5 minutes)

### 1.1 Create Your Bot
1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Choose a name: `My Subtitle Bot`
4. Choose a username: `mysubtitlebot` (must end with 'bot')
5. **Save the BOT_TOKEN** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 1.2 Get API Credentials
1. Visit [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Click "API Development Tools"
4. Fill in application details:
   - App title: `Subtitle Bot`
   - Short name: `subbot`
   - Platform: `Other`
5. **Save API_ID** (7-8 digits) and **API_HASH** (32 characters)

### 1.3 Get TMDB API Key
1. Visit [themoviedb.org](https://www.themoviedb.org/)
2. Create account (free)
3. Go to Settings → API
4. Request API key (choose "Developer")
5. **Save the API key**

## Step 2: Setup MongoDB (5 minutes)

### Option A: MongoDB Atlas (Cloud - Recommended)
1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas/register)
2. Create free account
3. Create free cluster (M0)
4. Click "Connect" → "Connect your application"
5. **Copy the connection string** (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

### Option B: Local MongoDB
```bash
# Ubuntu/Debian
sudo apt install mongodb
sudo systemctl start mongodb

# macOS
brew install mongodb-community
brew services start mongodb-community

# Connection string: mongodb://localhost:27017
```

## Step 3: Install Bot (2 minutes)

```bash
# Clone repository
git clone <your-repo-url>
cd telegram_subtitle_bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Configure Bot (3 minutes)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env
# or use any text editor
```

**Fill in these required values:**
```env
API_ID=12345678
API_HASH=your_32_character_api_hash
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
BOT_USERNAME=yourbot
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
SOURCE_CHANNEL_ID=-1001234567890
ADMIN_IDS=123456789
TMDB_API_KEY=your_tmdb_key
```

### How to Get Channel IDs:

**Method 1: Using @userinfobot**
1. Add your bot to your channel as admin
2. Forward any message from channel to [@userinfobot](https://t.me/userinfobot)
3. Copy the ID (will be negative, like `-1001234567890`)

**Method 2: Using Web Telegram**
1. Open [web.telegram.org](https://web.telegram.org)
2. Open your channel
3. Look at URL: `web.telegram.org/#/im?p=c1234567890_...`
4. Add `-100` prefix: `-1001234567890`

## Step 5: Run the Bot! (30 seconds)

```bash
python main.py
```

You should see:
```
✅ Pyrogram client initialized
✅ MongoDB connected: subtitle_bot
✅ All handlers registered
✅ Bot started: @yourbot (ID: 123456789)
🎉 Bot is now running and ready to serve!
```

## Step 6: Test Your Bot

1. Open Telegram
2. Search for your bot username
3. Send `/start`
4. You should see welcome message!

### Test Search:
1. Type: `Avatar`
2. Bot should search and show results (if files indexed)

### Test Request:
1. Send: `/request`
2. Type: `Inception`
3. Select from TMDB results
4. Click "Request Subtitle"

## Common Issues & Solutions

### Bot not responding?
```bash
# Check if bot is running
ps aux | grep python

# Check logs
tail -f logs/bot_*.log

# Verify credentials
python -c "from config import *; print(f'API_ID: {API_ID}, Token: {BOT_TOKEN[:10]}...')"
```

### MongoDB connection failed?
```bash
# Test MongoDB connection
python -c "from pymongo import MongoClient; MongoClient('your_mongo_uri').admin.command('ping'); print('Connected!')"
```

### No files found in search?
The bot needs files in the source channel first!
1. Create a Telegram channel
2. Add your bot as admin
3. Upload some `.srt` files
4. Wait 30 seconds for auto-indexing
5. Or use `/index` command (admin only)

### Images not loading?
Images are optional! The bot works without them. To add images:
1. Upload image to Telegram channel
2. Right-click → Copy post link
3. Add to .env: `WELCOME_IMAGE=https://t.me/yourchannel/123`

## What's Next?

### Add Subtitle Files:
1. Create a channel for subtitles
2. Make your bot admin in the channel
3. Upload `.srt`, `.ass`, or `.vtt` files
4. Bot automatically indexes them!

### Customize Messages:
Edit `config.py` to change:
- Welcome message
- Help text  
- Button labels
- Add more languages

### Deploy to Production:
See `README.md` for:
- Heroku deployment
- Docker deployment
- VPS deployment with systemd

## Need Help?

1. **Check logs**: `tail -f logs/bot_*.log`
2. **Verify config**: `python -c "from config import *; print('✓ Config loaded')"`
3. **Test database**: `python -c "from database import *; print('✓ Database OK')"`
4. **Read README**: Full documentation in `README.md`

## Success Checklist

Before going live, verify:
- [ ] Bot responds to /start
- [ ] Search works (if files indexed)
- [ ] Request system works (TMDB)
- [ ] Admin commands work
- [ ] Force subscribe works (if enabled)
- [ ] Images load (if configured)
- [ ] Database stores data
- [ ] Logs are being created

## Quick Commands Reference

```bash
# Start bot
python main.py

# Stop bot
Ctrl+C

# View logs
tail -f logs/bot_*.log

# Update code
git pull
pip install -r requirements.txt --upgrade
python main.py

# Backup database (run inside Python)
python -c "from database import *; import asyncio; asyncio.run(db.create_backup())"
```

## Maintenance

### Daily:
- Check bot is running: `ps aux | grep python`
- Check logs for errors: `grep ERROR logs/bot_*.log`

### Weekly:
- Review statistics: Send `/stats` to bot
- Check top searches: Review analytics
- Update dependencies: `pip install -r requirements.txt --upgrade`

### Monthly:
- Database backup: Use `/backup` command
- Clean duplicates: Use `/scan` command
- Review user feedback

---

**Congratulations! 🎉** Your bot is now running!

For advanced features and customization, see the full [README.md](README.md).

Having issues? Check the logs first, then review the configuration.

**Pro Tip**: Start simple - get the basic search working first, then add advanced features!

# Quick Start Guide - Phase 1

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- [ ] Docker & Docker Compose (optional, for containerized setup)

## Step-by-Step Setup

### 1. Environment Setup

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your Discord bot token
# DISCORD_TOKEN=your_actual_bot_token_here
```

### 2. Install Dependencies

**Option A: Local Development**

```bash
# Install backend dependencies
pip install -r requirements-backend.txt

# Install bot dependencies
pip install -r requirements-bot.txt
```

**Option B: Docker (Recommended)**

```bash
# No manual installation needed - Docker handles it
```

### 3. Start Services

**Option A: Local Development**

Terminal 1 - Backend:
```bash
python run_backend.py
# OR: uvicorn backend.main:app --reload
```

Terminal 2 - Bot:
```bash
python run_bot.py
# OR: python -m bot.main
# OR: python bot/main.py
```

**Option B: Docker**

```bash
docker-compose up --build
```

### 4. Enable Privileged Intents (REQUIRED)

**⚠️ IMPORTANT: You must enable privileged intents before the bot will work!**

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Go to **Bot** section in the left sidebar
4. Scroll down to **Privileged Gateway Intents**
5. Enable the following intents:
   - ✅ **MESSAGE CONTENT INTENT** (Required - bot needs to read message content)
   - ⚪ **SERVER MEMBERS INTENT** (Optional, for future features)
6. Click **Save Changes**
7. Wait 1-2 minutes for changes to take effect

**Why?** The bot needs to read message content in ticket channels to relay them to the backend. This is a privileged intent that must be explicitly enabled.

### 5. Invite Bot to Discord Server

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Go to **OAuth2** → **URL Generator**
4. Select scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
5. Select bot permissions:
   - ✅ Manage Channels
   - ✅ Send Messages
   - ✅ Read Message History
   - ✅ View Channels
6. Copy the generated URL and open it in your browser
7. Select your test server and authorize

### 6. Test Phase 1 Functionality

1. **Run Setup Command**:
   - In your Discord server, type: `/setup`
   - Bot should create "Tickets" category and "Support" role
   - You should see: "✅ Setup complete!"

2. **Create a Ticket**:
   - Type: `/create-ticket`
   - Bot should create a private channel `ticket-{your_user_id}`
   - You should see a welcome message in the ticket channel

3. **Test Message Relay**:
   - Send a message in the ticket channel (e.g., "Hello, I need help!")
   - Bot should respond with: "AI is thinking... (Phase 1 placeholder)"

4. **Test Health Endpoint** (optional):
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy","service":"ai-ticket-assistant-backend"}`

## Verification Script

Run the setup verification script:

```bash
python test_setup.py
```

This will check:
- ✅ .env file exists
- ✅ Backend health endpoint responds
- ✅ Backend relay endpoint works

## Troubleshooting

### Bot doesn't appear online
- Check `DISCORD_TOKEN` in `.env` is correct
- Check bot logs for errors
- Verify bot has proper intents enabled in Discord Developer Portal

### Commands don't appear
- Wait 1-2 minutes for command sync
- Check bot logs for sync errors
- Try restarting the bot

### Backend connection fails
- Verify backend is running: `curl http://localhost:8000/health`
- Check `BACKEND_URL` in `.env`:
  - Local: `http://localhost:8000`
  - Docker: `http://api:8000`

### Ticket channel not created
- Run `/setup` first
- Check bot has "Manage Channels" permission
- Check bot logs for permission errors

## What's Working (Phase 1)

✅ Bot joins server and responds to commands  
✅ `/setup` creates Tickets category and Support role  
✅ `/create-ticket` creates private ticket channels  
✅ Messages in ticket channels are relayed to backend  
✅ Backend receives and logs messages  
✅ Bot receives placeholder response and posts it  
✅ Health check endpoint works  

## What's NOT Implemented Yet

❌ Database (Phase 2)  
❌ Knowledge base (Phase 2)  
❌ Subscription plans & limits (Phase 2)  
❌ AI processing (Phase 3)  
❌ Token tracking (Phase 3)  
❌ Dashboard (Phase 4)  

## Next Steps

Once Phase 1 is verified working, proceed to Phase 2:
- Database schema and migrations
- Knowledge base CRUD endpoints
- Subscription plan system
- Usage limit enforcement


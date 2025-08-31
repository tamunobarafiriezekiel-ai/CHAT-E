# 🚀 Telegram Admin Bot

A simple Flask-based Telegram bot with admin-only commands for group management.

## Features
- /start → Welcome message
- /help → Show help menu
- /ping → Check if bot is alive
- /echo <text> → Echo back text
- /admin <message> → Send message to admin
- /kick @username → Soft kick user (they can rejoin)
- /mute @username → Mute user
- /unmute @username → Unmute user
- /ban @username → Permanently ban user

⚠️ All commands are restricted to **ADMIN_ID**.

---

## 🚀 Deploy to Render

1. Fork or upload this repo
2. Create a new **Web Service** in Render
3. Set environment variables:
   - `BOT_TOKEN` → Your Telegram bot token
   - `ADMIN_ID` → Your Telegram ID
   - `GROUP_ID` → Target Telegram group ID
   - `RENDER_EXTERNAL_URL` → Render will auto-set this
4. Deploy and your bot will auto-set the webhook.

---

## 🔧 Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
python bot.py
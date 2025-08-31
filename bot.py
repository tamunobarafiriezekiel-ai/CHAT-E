from flask import Flask, request
import requests
import os
import time

app = Flask(__name__)

# Load environment variables
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6952136450"))
GROUP_ID = int(os.getenv("GROUP_ID", "-1002493478840"))

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# ------------------ Helper: Send message ------------------
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

# ------------------ Helper: Resolve @username to user_id ------------------
def get_user_id_from_username(username: str):
    if username.startswith("@"):
        username = username[1:]
    url = f"{BASE_URL}/getChat"
    r = requests.get(url, params={"chat_id": username})
    data = r.json()
    try:
        return data["result"]["id"]
    except:
        return None

# ------------------ Command Handlers ------------------
def handle_start(chat_id, user_id):
    if user_id == ADMIN_ID:
        send_message(chat_id, "✅ Welcome Admin! You have full access.")
    else:
        send_message(chat_id, "⚠️ You are not authorized to use this bot.")

def handle_help(chat_id, user_id):
    if user_id == ADMIN_ID:
        help_text = (
            "🤖 *Admin-Only Bot Commands:*\n"
            "- /start - Start the bot and get a welcome message\n"
            "- /help - Show this help menu\n"
            "- /ping - Check if the bot is alive\n"
            "- /echo <text> - Echo back the text you send\n"
            "- /admin <message> - Send a message to admins\n"
            "- /kick @username - Kick a user from the group\n"
            "- /ban @username - Ban a user from the group\n"
            "- /mute @username - Mute a user in the group\n"
            "- /unmute @username - Unmute a user in the group\n\n"
            "⚠️ Note: All commands are restricted to admins."
        )
        send_message(chat_id, help_text)
    else:
        send_message(chat_id, "❌ You are not authorized.")

def handle_ping(chat_id, user_id):
    if user_id == ADMIN_ID:
        send_message(chat_id, "🏓 Pong! Bot is alive.")
    else:
        send_message(chat_id, "❌ You are not authorized.")

def handle_echo(chat_id, user_id, text):
    if user_id == ADMIN_ID:
        send_message(chat_id, text)
    else:
        send_message(chat_id, "❌ You are not authorized.")

def handle_admin(chat_id, user_id, text):
    if user_id == ADMIN_ID:
        send_message(ADMIN_ID, f"📩 Admin message: {text}")
        send_message(chat_id, "✅ Sent to admin.")
    else:
        send_message(chat_id, "❌ You are not authorized.")

def handle_kick(chat_id, user_id, target_username):
    if user_id == ADMIN_ID:
        target_id = get_user_id_from_username(target_username)
        if target_id:
            # Soft kick: ban then unban
            ban_url = f"{BASE_URL}/banChatMember"
            requests.post(ban_url, json={"chat_id": GROUP_ID, "user_id": target_id})

            unban_url = f"{BASE_URL}/unbanChatMember"
            requests.post(unban_url, json={"chat_id": GROUP_ID, "user_id": target_id})

            send_message(chat_id, f"👢 User {target_username} was kicked (soft ban).")
        else:
            send_message(chat_id, f"❌ Could not find {target_username}")
    else:
        send_message(chat_id, "❌ You are not authorized.")

def handle_ban(chat_id, user_id, target_username):
    if user_id == ADMIN_ID:
        target_id = get_user_id_from_username(target_username)
        if target_id:
            url = f"{BASE_URL}/banChatMember"
            requests.post(url, json={"chat_id": GROUP_ID, "user_id": target_id})
            send_message(chat_id, f"🚫 User {target_username} banned from group.")
        else:
            send_message(chat_id, f"❌ Could not find {target_username}")
    else:
        send_message(chat_id, "❌ You are not authorized.")

def handle_mute(chat_id, user_id, target_username):
    if user_id == ADMIN_ID:
        target_id = get_user_id_from_username(target_username)
        if target_id:
            url = f"{BASE_URL}/restrictChatMember"
            requests.post(url, json={
                "chat_id": GROUP_ID,
                "user_id": target_id,
                "permissions": {"can_send_messages": False}
            })
            send_message(chat_id, f"🔇 User {target_username} muted in group.")
        else:
            send_message(chat_id, f"❌ Could not find {target_username}")
    else:
        send_message(chat_id, "❌ You are not authorized.")

def handle_unmute(chat_id, user_id, target_username):
    if user_id == ADMIN_ID:
        target_id = get_user_id_from_username(target_username)
        if target_id:
            url = f"{BASE_URL}/restrictChatMember"
            requests.post(url, json={
                "chat_id": GROUP_ID,
                "user_id": target_id,
                "permissions": {  # Restore permissions
                    "can_send_messages": True,
                    "can_send_media_messages": True,
                    "can_send_polls": True,
                    "can_send_other_messages": True,
                    "can_add_web_page_previews": True,
                    "can_change_info": False,
                    "can_invite_users": True,
                    "can_pin_messages": False
                }
            })
            send_message(chat_id, f"🔊 User {target_username} unmuted in group.")
        else:
            send_message(chat_id, f"❌ Could not find {target_username}")
    else:
        send_message(chat_id, "❌ You are not authorized.")

# ------------------ Flask Webhook ------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"]["id"]
        text = msg.get("text", "")

        if text.startswith("/start"):
            handle_start(chat_id, user_id)

        elif text.startswith("/help"):
            handle_help(chat_id, user_id)

        elif text.startswith("/ping"):
            handle_ping(chat_id, user_id)

        elif text.startswith("/echo") and user_id == ADMIN_ID:
            try:
                echo_text = text.split(" ", 1)[1]
                handle_echo(chat_id, user_id, echo_text)
            except:
                send_message(chat_id, "Usage: /echo <text>")

        elif text.startswith("/admin") and user_id == ADMIN_ID:
            try:
                admin_msg = text.split(" ", 1)[1]
                handle_admin(chat_id, user_id, admin_msg)
            except:
                send_message(chat_id, "Usage: /admin <message>")

        elif text.startswith("/kick") and user_id == ADMIN_ID:
            try:
                target_username = text.split(" ", 1)[1]
                handle_kick(chat_id, user_id, target_username)
            except:
                send_message(chat_id, "Usage: /kick @username")

        elif text.startswith("/ban") and user_id == ADMIN_ID:
            try:
                target_username = text.split(" ", 1)[1]
                handle_ban(chat_id, user_id, target_username)
            except:
                send_message(chat_id, "Usage: /ban @username")

        elif text.startswith("/mute") and user_id == ADMIN_ID:
            try:
                target_username = text.split(" ", 1)[1]
                handle_mute(chat_id, user_id, target_username)
            except:
                send_message(chat_id, "Usage: /mute @username")

        elif text.startswith("/unmute") and user_id == ADMIN_ID:
            try:
                target_username = text.split(" ", 1)[1]
                handle_unmute(chat_id, user_id, target_username)
            except:
                send_message(chat_id, "Usage: /unmute @username")

    return {"ok": True}

# ------------------ Set Webhook Automatically ------------------
if TOKEN:
    APP_URL = os.getenv("RENDER_EXTERNAL_URL", "https://telegram-bot-h9su.onrender.com")
    if APP_URL:
        webhook_url = f"{APP_URL}/webhook"
        set_webhook = f"{BASE_URL}/setWebhook?url={webhook_url}"
        try:
            r = requests.get(set_webhook)
            print("Webhook set:", r.json())
        except Exception as e:
            print("Error setting webhook:", e)

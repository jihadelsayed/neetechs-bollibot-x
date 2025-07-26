
import os
from discord_webhook import DiscordWebhook

webhook_url = os.getenv("DISCORD_WEBHOOK")

def send_alert(message):
    if not webhook_url:
        print("⚠️ Discord webhook not set.")
        return

    try:
        webhook = DiscordWebhook(url=webhook_url, content=message)
        response = webhook.execute()
        print("📢 Discord alert sent.")
    except Exception as e:
        print("❌ Failed to send Discord alert:", e)

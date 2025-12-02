from plugin import plugin
import smtplib
import requests
import os

# --- Telegram Plugin ---
@plugin("send telegram")
def send_telegram(jarvis, s):
    """
    Send a message through Telegram.
    Usage: send telegram <message>
    """
    # Get credentials from environment variables
    TELEGRAM_BOT_TOKEN = os.environ.get("JARVIS_TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.environ.get("JARVIS_TELEGRAM_CHAT_ID")

    if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
        jarvis.say("Telegram credentials are missing! Please set JARVIS_TELEGRAM_BOT_TOKEN and JARVIS_TELEGRAM_CHAT_ID.")
        return

    if not s:
        jarvis.say("What message should I send?")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": s}

    try:
        response = requests.post(url, data=data)
        if response.ok:
            jarvis.say("Message sent via Telegram!")
        else:
            jarvis.say(f"Failed to send Telegram message. Status: {response.status_code}")
    except Exception as e:
        jarvis.say(f"Error sending Telegram message: {e}")


# --- Gmail Plugin ---
@plugin("send gmail")
def send_gmail(jarvis, s):
    """
    Send a message through Gmail.
    Usage: send gmail <message>
    """
    EMAIL = os.environ.get("JARVIS_GMAIL_ADDRESS")
    PASSWORD = os.environ.get("JARVIS_GMAIL_APP_PASSWORD")

    if not EMAIL or not PASSWORD:
        jarvis.say("Gmail credentials are missing! Please set JARVIS_GMAIL_ADDRESS and JARVIS_GMAIL_APP_PASSWORD.")
        return

    if not s:
        jarvis.say("What message should I send?")
        return

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, EMAIL, s)
        jarvis.say("Email sent successfully!")
    except Exception as e:
        jarvis.say(f"Error sending email: {e}")


def send_join_message():
    """Send a startup message via Telegram."""
    TELEGRAM_BOT_TOKEN = os.environ.get("JARVIS_TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.environ.get("JARVIS_TELEGRAM_CHAT_ID")

    if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
        # Silently fail if credentials are not set
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": "Jarvis is up and running!"}

    try:
        requests.post(url, data=data)
    except Exception:
        # Silently fail on error
        pass

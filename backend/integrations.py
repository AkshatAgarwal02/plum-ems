"""
Slack & Gmail Integration Module
Handles OAuth, data fetching, and syncing
"""

import os, json, sqlite3, requests
from datetime import datetime
from functools import wraps

DB_PATH = os.path.join(os.path.dirname(__file__), "plum_ems.db")

# ─── OAuth Config (user will set these as env vars) ───────────────────────────────
SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID", "")
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET", "")
SLACK_REDIRECT_URI = os.getenv("SLACK_REDIRECT_URI", "https://plum-ems.onrender.com/api/integrations/slack/callback")

GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID", "")
GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET", "")
GMAIL_REDIRECT_URI = os.getenv("GMAIL_REDIRECT_URI", "https://plum-ems.onrender.com/api/integrations/gmail/callback")

# ─── Database helpers ───────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_token(platform):
    """Get stored OAuth token for Slack or Gmail"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT access_token FROM oauth_tokens WHERE platform=?", (platform,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def save_token(platform, access_token, refresh_token=None, expires_at=None):
    """Save OAuth token"""
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT OR REPLACE INTO oauth_tokens (platform, access_token, refresh_token, expires_at, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (platform, access_token, refresh_token, expires_at, now))
    conn.commit()
    conn.close()

# ─── Slack Integration ───────────────────────────────────────────────────────────
def fetch_slack_data():
    """Pull messages and escalations from Slack"""
    token = get_token("slack")
    if not token:
        return {"error": "Slack not connected"}

    try:
        # Fetch channels
        headers = {"Authorization": f"Bearer {token}"}
        channels_resp = requests.get("https://slack.com/api/conversations.list", headers=headers, timeout=10)
        channels = channels_resp.json().get("channels", [])

        conn = get_db()
        cursor = conn.cursor()
        now = datetime.now().isoformat()

        all_messages = []
        for channel in channels[:5]:  # Limit to 5 channels
            ch_id = channel["id"]
            ch_name = channel["name"]

            # Get recent messages
            msg_resp = requests.get(
                "https://slack.com/api/conversations.history",
                headers=headers,
                params={"channel": ch_id, "limit": 20},
                timeout=10
            )
            messages = msg_resp.json().get("messages", [])

            for msg in messages:
                # Check if message looks like an escalation
                is_esc = 1 if any(kw in msg.get("text", "").lower() for kw in ["urgent", "critical", "escalat", "sla", "breach"]) else 0
                priority = "Critical" if is_esc and any(w in msg.get("text", "").lower() for w in ["critical", "urgent"]) else "High" if is_esc else "Medium"

                cursor.execute("""
                    INSERT OR IGNORE INTO slack_messages
                    (channel_id, channel_name, user_id, user_name, message, timestamp, is_escalation, priority, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ch_id, ch_name,
                    msg.get("user", "unknown"),
                    msg.get("username", "Unknown User"),
                    msg.get("text", ""),
                    msg.get("ts"),
                    is_esc, priority,
                    now
                ))
                all_messages.append({"channel": ch_name, "text": msg.get("text", "")[:100], "priority": priority})

        conn.commit()
        conn.close()
        return {"status": "success", "messages_synced": len(all_messages), "preview": all_messages[:10]}

    except Exception as e:
        return {"error": str(e)}

# ─── Gmail Integration ───────────────────────────────────────────────────────────
def fetch_gmail_data():
    """Pull emails and extract escalations from Gmail"""
    token = get_token("gmail")
    if not token:
        return {"error": "Gmail not connected"}

    try:
        headers = {"Authorization": f"Bearer {token}"}

        # Get list of emails
        emails_resp = requests.get(
            "https://www.googleapis.com/gmail/v1/users/me/messages",
            headers=headers,
            params={"maxResults": 20, "labelIds": "INBOX"},
            timeout=10
        )
        emails = emails_resp.json().get("messages", [])

        conn = get_db()
        cursor = conn.cursor()
        now = datetime.now().isoformat()

        all_emails = []
        for email_meta in emails:
            # Get full email
            full_email_resp = requests.get(
                f"https://www.googleapis.com/gmail/v1/users/me/messages/{email_meta['id']}",
                headers=headers,
                timeout=10
            )
            email = full_email_resp.json()
            headers_list = email.get("payload", {}).get("headers", [])

            subject = next((h["value"] for h in headers_list if h["name"] == "Subject"), "No Subject")
            from_email = next((h["value"] for h in headers_list if h["name"] == "From"), "Unknown")

            # Extract body (simplified)
            body = ""
            if "parts" in email.get("payload", {}):
                for part in email["payload"]["parts"]:
                    if part.get("mimeType") == "text/plain":
                        data = part.get("body", {}).get("data", "")
                        if data:
                            import base64
                            body = base64.urlsafe_b64decode(data).decode('utf-8')
                            break

            # Check if escalation
            text_for_check = (subject + " " + body).lower()
            is_esc = 1 if any(kw in text_for_check for kw in ["urgent", "critical", "escalat", "sla", "breach", "issue"]) else 0
            priority = "Critical" if is_esc and any(w in text_for_check for w in ["critical", "urgent"]) else "High" if is_esc else "Medium"

            cursor.execute("""
                INSERT OR IGNORE INTO gmail_emails
                (message_id, from_email, subject, body, timestamp, is_escalation, priority, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email_meta["id"], from_email, subject, body[:200], now, is_esc, priority, now
            ))
            all_emails.append({"from": from_email, "subject": subject, "priority": priority})

        conn.commit()
        conn.close()
        return {"status": "success", "emails_synced": len(all_emails), "preview": all_emails[:10]}

    except Exception as e:
        return {"error": str(e)}

# ─── Get synced data ───────────────────────────────────────────────────────────
def get_slack_messages(limit=50):
    """Get recent Slack messages"""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM slack_messages ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_gmail_emails(limit=50):
    """Get recent Gmail emails"""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM gmail_emails ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_external_escalations():
    """Get all escalations from Slack and Gmail"""
    conn = get_db()

    slack_esc = conn.execute(
        "SELECT 'slack' as source, channel_name as origin, message as content, priority, timestamp FROM slack_messages WHERE is_escalation=1 ORDER BY timestamp DESC"
    ).fetchall()

    gmail_esc = conn.execute(
        "SELECT 'gmail' as source, from_email as origin, subject as content, priority, timestamp FROM gmail_emails WHERE is_escalation=1 ORDER BY timestamp DESC"
    ).fetchall()

    conn.close()

    return {
        "slack_escalations": [dict(r) for r in slack_esc],
        "gmail_escalations": [dict(r) for r in gmail_esc],
        "total": len(slack_esc) + len(gmail_esc)
    }

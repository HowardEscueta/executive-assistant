"""
Email Sender
Sends morning briefing reports via Gmail using SMTP.
Requires Gmail App Password (NOT regular password).

Usage:
    from agents.emailer import send_briefing
    send_briefing(subject, html_body)
"""

import smtplib
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))


def send_email(subject, html_body, plain_body=None):
    """Send an HTML email via Gmail SMTP."""
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = gmail_address  # Send to self

    if not gmail_address or not app_password:
        print("ERROR: Gmail credentials not found in .env")
        print("Need: GMAIL_ADDRESS and GMAIL_APP_PASSWORD")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = gmail_address
    msg["To"] = recipient
    msg["Subject"] = subject

    if plain_body:
        msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        print(f"Sending email to {recipient}...")
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(gmail_address, app_password)
        server.sendmail(gmail_address, recipient, msg.as_string())
        server.quit()
        print("Email sent!")
        return True
    except smtplib.SMTPAuthenticationError:
        print("ERROR: Gmail authentication failed.")
        print("Make sure you're using an App Password, not your regular password.")
        return False
    except Exception as e:
        print(f"ERROR sending email: {e}")
        return False


def build_briefing_html(new_songs=None, ai_trends=None, leads=None):
    """Build an HTML email body from research results."""
    today = date.today().isoformat()

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #ffffff; padding: 20px; }}
            .container {{ max-width: 700px; margin: 0 auto; }}
            h1 {{ color: #0096FF; border-bottom: 2px solid #0096FF; padding-bottom: 10px; }}
            h2 {{ color: #00D27A; margin-top: 30px; }}
            .video {{ background: #16213e; padding: 12px 16px; margin: 8px 0; border-radius: 8px; border-left: 3px solid #0096FF; }}
            .lead {{ background: #16213e; padding: 12px 16px; margin: 8px 0; border-radius: 8px; border-left: 3px solid #FFD93D; }}
            .song {{ background: #16213e; padding: 12px 16px; margin: 8px 0; border-radius: 8px; border-left: 3px solid #FF4545; }}
            a {{ color: #0096FF; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .stats {{ color: #cccccc; font-size: 13px; }}
            .score {{ color: #FFD93D; font-weight: bold; }}
            .section-count {{ color: #888; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Morning Briefing - {today}</h1>
    """

    # New Songs Section
    if new_songs:
        html += f'<h2>New Songs ({len(new_songs)})</h2>\n'
        for i, v in enumerate(new_songs, 1):
            html += f"""
            <div class="song">
                <strong>{i}. <a href="{v['url']}">{v['title']}</a></strong><br>
                <span class="stats">{v['channel']} | {v['views']:,} views | {v['upload_date']}</span>
            </div>
            """

    # AI Automation Section
    if ai_trends:
        html += f'<h2>AI Automation Trends ({len(ai_trends)})</h2>\n'
        for i, v in enumerate(ai_trends, 1):
            html += f"""
            <div class="video">
                <strong>{i}. <a href="{v['url']}">{v['title']}</a></strong><br>
                <span class="stats">{v['channel']} | {v['views']:,} views | Engagement: {v['engagement_rate']}% | {v['upload_date']}</span>
            </div>
            """

    # Freelance Leads Section
    if leads:
        hot = [l for l in leads if l.get('score', 0) >= 3]
        html += f'<h2>Freelance Leads ({len(hot)} hot)</h2>\n'
        for i, l in enumerate(hot, 1):
            html += f"""
            <div class="lead">
                <strong>{i}. <a href="{l['url']}">[{l.get('source', 'Web')}] {l['title']}</a></strong>
                <span class="score"> Score: {l.get('score', 0)}/10</span><br>
                <span class="stats">{l.get('snippet', '')[:150]}</span>
            </div>
            """
        others = [l for l in leads if l.get('score', 0) < 3]
        if others:
            html += '<p style="color:#888;">Other leads:</p><ul>'
            for l in others:
                html += f'<li><a href="{l["url"]}">{l["title"][:80]}</a></li>'
            html += '</ul>'

    html += """
        </div>
    </body>
    </html>
    """
    return html


def send_briefing(new_songs=None, ai_trends=None, leads=None):
    """Build and send the morning briefing email."""
    today = date.today().isoformat()
    html = build_briefing_html(new_songs, ai_trends, leads)
    subject = f"Morning Briefing - {today}"
    return send_email(subject, html)


if __name__ == "__main__":
    # Test with sample data
    print("Sending test briefing email...")
    send_briefing()

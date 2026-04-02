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
from email.mime.base import MIMEBase
from email import encoders
from datetime import date

from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))


def send_email(subject, html_body, plain_body=None, attachment_path=None):
    """Send an HTML email via Gmail SMTP, optionally with a file attachment."""
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = gmail_address  # Send to self

    if not gmail_address or not app_password:
        print("ERROR: Gmail credentials not found in .env")
        print("Need: GMAIL_ADDRESS and GMAIL_APP_PASSWORD")
        return False

    msg = MIMEMultipart("mixed")
    body_part = MIMEMultipart("alternative")
    if plain_body:
        body_part.attach(MIMEText(plain_body, "plain"))
    body_part.attach(MIMEText(html_body, "html"))
    msg.attach(body_part)

    msg["From"] = gmail_address
    msg["To"] = recipient
    msg["Subject"] = subject

    # Attach file if provided
    if attachment_path and os.path.exists(attachment_path):
        filename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as f:
            attachment = MIMEBase("application", "octet-stream")
            attachment.set_payload(f.read())
        encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(attachment)
        print(f"Attached: {filename}")

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


def build_briefing_html(new_songs=None, ai_trends=None, leads=None, local_leads=None):
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

    # Local Business Leads Section
    if local_leads:
        html += f'<h2 style="color:#FF7A00;">Local Business Leads ({len(local_leads)} No Website)</h2>\n'
        for i, b in enumerate(local_leads, 1):
            rating_str = f"{b['rating']}/5 ({b['user_ratings_total']} reviews)" if b.get("rating") else "No ratings"
            maps_link = f'<a href="{b["maps_url"]}">View on Maps</a>' if b.get("maps_url") else ""
            html += f"""
            <div style="background:#16213e;padding:12px 16px;margin:8px 0;border-radius:8px;border-left:3px solid #FF7A00;">
                <strong style="color:#FF7A00;">{i}. {b['name']}</strong> &nbsp;<span style="color:#888;font-size:12px;">[{b['category'].title()}]</span><br>
                <span style="color:#ccc;font-size:13px;">{b['address']}</span><br>
                <span style="color:#ccc;font-size:13px;">Phone: {b.get('phone') or 'Not listed'} &nbsp;|&nbsp; {rating_str}</span><br>
                <span style="font-size:12px;">{maps_link}</span>
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


def send_briefing(new_songs=None, ai_trends=None, leads=None, local_leads=None, pptx_path=None):
    """Build and send the morning briefing email with PPT attachment."""
    today = date.today().isoformat()
    html = build_briefing_html(new_songs, ai_trends, leads, local_leads)
    subject = f"Morning Briefing - {today}"
    return send_email(subject, html, attachment_path=pptx_path)


if __name__ == "__main__":
    print("Sending test briefing email...")
    send_briefing()

#!/usr/bin/env python3
import os
import smtplib
import tarfile
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from pathlib import Path

SMTP_HOST = "smtp.yandex.com"
SMTP_PORT = 465
SMTP_USER = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
TO_EMAIL = "241260@edu.fa.ru"

def create_archive():
    report_files = list(Path(".").glob("gl-*.json"))
    if not report_files:
        print("No report files found")
        with open("security_reports.txt", "w") as f:
            f.write("No security reports available")
        report_files = [Path("security_reports.txt")]
    
    with tarfile.open("security_reports.tar.gz", "w:gz") as tar:
        for file in report_files:
            tar.add(file)
    print(f"Created archive with {len(report_files)} files: {[f.name for f in report_files]}")
    return True

def send_email():
    if not all([SMTP_USER, SMTP_PASSWORD, TO_EMAIL]):
        print(f"Missing credentials")
        return False
    
    msg = MIMEMultipart()
    msg["Subject"] = f"Security Report - {os.environ.get('CI_PROJECT_NAME', 'Unknown')}"
    msg["From"] = SMTP_USER
    msg["To"] = TO_EMAIL
    
    body = f"""
Pipeline: {os.environ.get('CI_PIPELINE_URL', 'N/A')}
Branch: {os.environ.get('CI_COMMIT_BRANCH', 'N/A')}
Commit: {os.environ.get('CI_COMMIT_SHORT_SHA', 'N/A')}
Author: {os.environ.get('GITLAB_USER_LOGIN', 'N/A')}
Time: {os.environ.get('CI_JOB_STARTED_AT', 'N/A')}

Security reports attached.
"""
    msg.attach(MIMEText(body, "plain"))
    
    with open("security_reports.tar.gz", "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename="security_reports.tar.gz")
        msg.attach(part)
    
    try:
        print(f"Connecting to {SMTP_HOST}:{SMTP_PORT}...")
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            print(f"Logging in as {SMTP_USER}...")
            server.login(SMTP_USER, SMTP_PASSWORD)
            print(f"Sending email to {TO_EMAIL}...")
            server.send_message(msg)
            print(f"Email sent successfully to {TO_EMAIL}")
            print(f"Email subject: {msg['Subject']}")
            print(f"Attachment size: {os.path.getsize('security_reports.tar.gz')} bytes")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_archive()
    send_email()

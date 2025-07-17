import imaplib
import email
from email.header import decode_header
import time
import requests
import os

# Telegram bot token va chat_id (o'zingiznikiga moslashtiring)
TELEGRAM_BOT_TOKEN = "7613439405:AAGYuU0yUaJfuCvxmYOaJdq1mQeym7B4KkU"
TELEGRAM_CHAT_ID = "6892058691"

# Gmail kirish ma'lumotlari (App Password ishlatish kerak!)
EMAIL_USER = "mirdedaev99@gmail.com"
EMAIL_PASS = os.environ.get("EMAIL_PASSWORD")  # Render.com da "Environment"da yoziladi

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegramga yuborishda xato:", e)

def read_emails():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        status, messages = mail.search(None, '(UNSEEN)')
        mail_ids = messages[0].split()

        for num in mail_ids[-5:]:  # Oxirgi 5 ta o'qilmagan xabar
            typ, data = mail.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            from_ = msg.get("From")

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_dispo = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_dispo:
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = msg.get_payload(decode=True).decode()

            message = f"📩 Yangi signal:\n\n🔹 From: {from_}\n🔹 Subject: {subject}\n\n{body[:500]}"
            send_to_telegram(message)

        mail.logout()
    except Exception as e:
        print("Email o'qishda xato:", e)

# Har 1 daqiqada emailni tekshirish
while True:
    read_emails()
    time.sleep(60)

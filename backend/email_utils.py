import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_verification_email(to_email: str, token: str):
    smtp_server = os.getenv("EMAIL_SERVER_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("EMAIL_SERVER_PORT", "587"))
    smtp_user = os.getenv("EMAIL_SERVER_USER")
    smtp_password = os.getenv("EMAIL_SERVER_PASSWORD")
    from_email = os.getenv("EMAIL_FROM", "noreply@talkoapp.com")

    if not smtp_user or not smtp_password:
        print(f"⚠️ SMTP Credentials not set. Verification Link for {to_email}: http://localhost:3000/verify-email?token={token}")
        return

    subject = "Verify your Talk-o Account"
    body = f"""
    <h1>Welcome to Talk-o!</h1>
    <p>Please click the link below to verify your email address and complete your registration:</p>
    <a href="http://localhost:3000/verify-email?token={token}">Verify Email</a>
    <br>
    <p>If you didn't request this, please ignore this email.</p>
    """

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f"✅ Verification email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        # Fallback log for dev
        print(f"🔗 Verification Link: http://localhost:3000/verify-email?token={token}")

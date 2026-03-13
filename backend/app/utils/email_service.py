"""
Email Service for sending password reset emails.
Uses Gmail SMTP for sending emails.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional


class EmailService:
    """Service for sending emails via SMTP"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_email = os.getenv("SMTP_EMAIL", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str = "User") -> bool:
        """
        Send password reset email with reset link.
        
        Args:
            to_email: Recipient email address
            reset_token: Unique reset token
            user_name: User's name for personalization
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.smtp_email or not self.smtp_password:
            print("⚠️ SMTP credentials not configured. Token:", reset_token)
            print(f"   Reset link: {self.frontend_url}/reset-password?token={reset_token}")
            return True  # Return True for testing without email
        
        try:
            # Create reset link
            reset_link = f"{self.frontend_url}/reset-password?token={reset_token}"
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Reset Your Password - Job Matching Platform"
            message["From"] = self.smtp_email
            message["To"] = to_email
            
            # Plain text version
            text = f"""
Hello {user_name},

We received a request to reset your password for your Job Matching Platform account.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour.

If you didn't request this password reset, please ignore this email.

Best regards,
Job Matching Platform Team
            """
            
            # HTML version
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #1e3a5f, #2d5a87); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
        .button {{ display: inline-block; background: #1e3a5f; color: white !important; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Password Reset</h1>
        </div>
        <div class="content">
            <p>Hello <strong>{user_name}</strong>,</p>
            <p>We received a request to reset your password for your Job Matching Platform account.</p>
            <p>Click the button below to reset your password:</p>
            <p style="text-align: center;">
                <a href="{reset_link}" class="button">Reset Password</a>
            </p>
            <p><small>Or copy this link: {reset_link}</small></p>
            <p><strong>⏰ This link will expire in 1 hour.</strong></p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="color: #888;">If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
        </div>
        <div class="footer">
            <p>© 2026 Job Matching Platform. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """
            
            # Attach both versions
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_email, self.smtp_password)
                server.sendmail(self.smtp_email, to_email, message.as_string())
            
            print(f"✅ Password reset email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
            print(f"   Fallback - Reset token: {reset_token}")
            return False


# Singleton instance
email_service = EmailService()

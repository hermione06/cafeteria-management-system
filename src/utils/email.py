"""
Email utility functions for sending emails
"""
from flask import current_app, url_for
from flask_mail import Mail, Message
from threading import Thread


def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        mail = Mail(app)
        mail.send(msg)


def send_email(subject, recipients, text_body, html_body=None):
    """
    Send email with optional HTML body
    
    Args:
        subject: Email subject
        recipients: List of recipient emails
        text_body: Plain text email body
        html_body: HTML email body (optional)
    """
    try:
        app = current_app._get_current_object()
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=recipients if isinstance(recipients, list) else [recipients]
        )
        msg.body = text_body
        if html_body:
            msg.html = html_body
        
        # Send asynchronously to avoid blocking
        Thread(target=send_async_email, args=(app, msg)).start()
        
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False


def send_verification_email(user, token):
    """Send email verification link to user"""
    # Build verification URL
    verification_url = url_for('auth.verify_email', token=token, _external=True)
    
    subject = "Verify Your Email - Cafeteria Management System"
    
    text_body = f"""
Hello {user.username},

Thank you for registering with Cafeteria Management System!

Please verify your email address by clicking the link below:
{verification_url}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
Cafeteria Management Team
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4F46E5; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #4F46E5; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍽️ Cafeteria Management</h1>
        </div>
        <div class="content">
            <h2>Hello {user.username}!</h2>
            <p>Thank you for registering with Cafeteria Management System!</p>
            <p>Please verify your email address by clicking the button below:</p>
            <center>
                <a href="{verification_url}" class="button">Verify Email Address</a>
            </center>
            <p>Or copy and paste this link in your browser:</p>
            <p style="word-break: break-all; color: #4F46E5;">{verification_url}</p>
            <p style="color: #ef4444; margin-top: 20px;">⚠️ This link will expire in 24 hours.</p>
            <p style="margin-top: 30px; color: #6b7280;">If you didn't create this account, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2025 Cafeteria Management System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, user.email, text_body, html_body)


def send_password_reset_email(user, token):
    """Send password reset link to user"""
    # Build reset URL
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    subject = "Password Reset Request - Cafeteria Management System"
    
    text_body = f"""
Hello {user.username},

You requested to reset your password.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this, please ignore this email and your password will remain unchanged.

Best regards,
Cafeteria Management Team
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #EF4444; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #EF4444; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Password Reset</h1>
        </div>
        <div class="content">
            <h2>Hello {user.username}!</h2>
            <p>You requested to reset your password.</p>
            <p>Click the button below to reset your password:</p>
            <center>
                <a href="{reset_url}" class="button">Reset Password</a>
            </center>
            <p>Or copy and paste this link in your browser:</p>
            <p style="word-break: break-all; color: #EF4444;">{reset_url}</p>
            <p style="color: #ef4444; margin-top: 20px;">⚠️ This link will expire in 1 hour.</p>
            <p style="margin-top: 30px; color: #6b7280;">If you didn't request this, please ignore this email and your password will remain unchanged.</p>
        </div>
        <div class="footer">
            <p>© 2025 Cafeteria Management System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, user.email, text_body, html_body)


def send_welcome_email(user):
    """Send welcome email after successful verification"""
    subject = "Welcome to Cafeteria Management System!"
    
    text_body = f"""
Hello {user.username},

Welcome to Cafeteria Management System! 🎉

Your email has been verified successfully. You can now:
- Browse our menu
- Place orders
- Track your order history
- Manage your account

Login here: {url_for('auth.login', _external=True)}

Enjoy your meals!

Best regards,
Cafeteria Management Team
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #10B981; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #10B981; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
        .feature {{ margin: 10px 0; padding-left: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Welcome!</h1>
        </div>
        <div class="content">
            <h2>Hello {user.username}!</h2>
            <p>Welcome to Cafeteria Management System!</p>
            <p>Your email has been verified successfully. You can now enjoy:</p>
            <div class="feature">✅ Browse our delicious menu</div>
            <div class="feature">✅ Place orders easily</div>
            <div class="feature">✅ Track your order history</div>
            <div class="feature">✅ Manage your account</div>
            <center>
                <a href="{url_for('auth.login', _external=True)}" class="button">Go to Login</a>
            </center>
            <p style="margin-top: 30px;">Enjoy your meals! 🍽️</p>
        </div>
        <div class="footer">
            <p>© 2025 Cafeteria Management System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, user.email, text_body, html_body)
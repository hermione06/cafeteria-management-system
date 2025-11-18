from flask_mail import Mail, Message

mail = Mail()

def init_mail(app):
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'yourcafeteriaemail@gmail.com'
    app.config['MAIL_PASSWORD'] = 'your-app-password'
    mail.init_app(app)

def send_verification_email(recipient, code):
    msg = Message("Your Cafeteria Verification Code",
                  sender="noreply@cafeteria.com",
                  recipients=[recipient])
    msg.body = f"Your verification code is: {code}\nIt expires in 1 hour."
    mail.send(msg)

################# EMAIL VERIFICATION SYSTEM ######################################################

from flask import Flask, request, render_template
from flask_mail import Mail, Message
import os
import jwt  # for token generation

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'your_mail_server'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# User Registration Endpoint
@app.route('/register', methods=['POST'])
def register():
    # Implement registration logic
    # Send verification email
    return 'Registration successful, verification email sent.'

# Email Sending Function
def send_verification_email(user_email, token):
    msg = Message('Email Verification', sender='your_email', recipients=[user_email])
    msg.body = f'Please click on the link to verify your email: {url_for("verify_email", token=token, _external=True)}'
    mail.send(msg)

# Verification Endpoint
@app.route('/verify-email/<token>')
def verify_email(token):
    # Token verification logic
    return 'Email verified successfully.'

if __name__ == '__main__':
    app.run(debug=True)

#######################################################################################################################
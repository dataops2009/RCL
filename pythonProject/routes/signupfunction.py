from flask import Flask, render_template, redirect, url_for, request, render_template_string, session
import pymssql
from flask import Flask, render_template, redirect, url_for, request, render_template_string
import pymssql
from flask import Flask, render_template, redirect, url_for, request, render_template_string, session
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from mailjet_rest import Client
import random
from datetime import datetime, timedelta
from classes.RegistrationClass import SignUpManager
from classes.NotificationClass import NotificationManager
from config import auth_codes


# Mailjet setup
api_key = '0f502cb98eda788b78d88b0d79feae51'
api_secret = '690bd92e04f6e062c52d10afa0966c3f'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')


def signup_function():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    
    if password != confirm_password:
        return render_template('RCL_Signup_Screen.html', password_match_message="Passwords do not match. Please go back and try again.")

    signup_manager = SignUpManager()
    registration_result = signup_manager.register_user(username, email, password)

    if not isinstance(registration_result, dict):
        return "An unexpected error occurred during registration."

    if registration_result['status'] == 'error':
        signup_manager.close_connection()
        return registration_result['message']

    auth_code_info = signup_manager.generate_auth_code(username)
    auth_codes[username] = {'code': auth_code_info['auth_code'], 'timestamp': auth_code_info['timestamp']}
    signup_manager.close_connection()

    email_status = send_auth_code_email(email, auth_code_info['auth_code'])
    if email_status == 200:
        return render_template_string("""
            <html>
                <body>
                    <h1>Registration successful!</h1>
                    <p>Thank you, {{ username }}, for registering. A verification code has been sent to your email.</p>
                    <form action="/verify" method="post">
                        Enter Verification Code: <input type="text" name="auth_code"><br>
                        <input type="hidden" name="username" value="{{ username }}">
                        <input type="submit" value="Verify">
                    </form>
                </body>
            </html>
        """, username=username)
    else:
        return "Error sending authentication code."



def send_auth_code_email(email, auth_code):
    data = {
      'Messages': [
        {
          "From": {
            "Email": "prabbi.kandola@hotmail.co.uk",  # Use a verified sender email
            "Name": "Prabjot"
          },
          "To": [
            {
              "Email": email,
              "Name": "Recipient Name"
            }
          ],
          "Subject": "Your Authentication Code",
          "TextPart": f"Hello, your authentication code is: {auth_code}"
        }
      ]
    }
    result = mailjet.send.create(data=data)
    return result.status_code
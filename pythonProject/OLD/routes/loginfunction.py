from flask import Flask, render_template, redirect, url_for, request, render_template_string, session
import pymssql
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from mailjet_rest import Client
import random
from datetime import datetime, timedelta
#from RegistrationClass import SignUpManager
#from NotificationClass import NotificationManager


def login_function():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009',
                               'rcldevelopmentdatabase')
        cursor = conn.cursor()
        cursor.execute("SELECT Username, Password FROM UserRegistration WHERE Username = %s", (username,))
        user_record = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_record and check_password_hash(user_record[1], password):
            # User authenticated successfully
            session['username'] = username  # Log the user in
            return redirect(url_for('RCL_Home_Screen'))

        else:
            # User authentication failed
            return "Invalid username or password"

    return render_template('RCL_Login_Screen.html')

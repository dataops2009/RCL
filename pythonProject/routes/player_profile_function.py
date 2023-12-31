# player_profile_function.py

from flask import session, redirect, url_for, render_template
import pymssql  # Assuming you're using this for database operations
import pymssql
from flask import Flask, render_template, redirect, url_for, request, render_template_string
import pymssql
from flask import Flask, render_template, redirect, url_for, request, render_template_string, session
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from mailjet_rest import Client
import random
from datetime import datetime, timedelta


def player_profile_function():
   # Check if a user is logged in
    if 'username' in session:
        # Fetch additional data if needed
        username = session['username']

        # Example: Fetching additional user data from the database
        # ... (Your database logic here)

        # Render the profile page with the username
        return render_template('RCL_Player_Profile_Screen.html', username=username)
    else:
        # If no user is logged in, redirect to the login page or another appropriate page
        return redirect(url_for('RCL_Home_Screen.html'))
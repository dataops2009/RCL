from flask import session, redirect, url_for, render_template
from classes.NotificationClass import NotificationManager
import pymssql

# main.py or other files
from config import auth_codes

from config import notification_manager


#notifications = {}

#notification_manager = NotificationManager()

def notifications_function():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        username = session['username']

        # Connect to your database
        conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
        cursor = conn.cursor()

        # Fetch user's ID_Var
        cursor.execute("SELECT ID_Var FROM UserRegistration WHERE Username = %s", (username,))
        user_id = cursor.fetchone()[0]

        # Get notifications for the user
        notifications = notification_manager.get_notifications(user_id)  # <-- Add this line

        cursor.close()
        conn.close()

        return render_template('notifications.html', notifications=notifications)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return "An error occurred while trying to fetch notifications."
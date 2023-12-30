
import pymssql
from flask import Flask, render_template, redirect, url_for, request, render_template_string
import pymssql
from flask import Flask, render_template, redirect, url_for, request, render_template_string, session
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

from mailjet_rest import Client
import random
from datetime import datetime, timedelta

#from notifications import NotificationManager

class Notification:
    def __init__(self, message, timestamp):
        self.message = message
        self.timestamp = timestamp

class NotificationManager:
    def __init__(self):
        self.notifications = {}  # Dictionary to store notifications by user_id

    def add_notification(self, user_id, message):
        if user_id not in self.notifications:
            self.notifications[user_id] = []
        self.notifications[user_id].append(Notification(message, datetime.now()))

    def get_notifications(self, user_id):
        return self.notifications.get(user_id, [])

    def clear_notifications(self, user_id):
        if user_id in self.notifications:
            del self.notifications[user_id]

# Global instance of the NotificationManager
notification_manager = NotificationManager()

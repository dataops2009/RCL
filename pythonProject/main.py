

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
from PIL import Image
from io import BytesIO
import os

from routes.signupfunction import signup_function
from classes.NotificationClass import NotificationManager
from routes.signupfunction import signup_function
from routes.notificationsfunction import notifications_function
from routes.loginfunction import login_function
from routes.player_profile_function import player_profile_function
from routes.player_ranking_function import player_ranking_function
from routes.recruitment_function import recruitment_function
from routes.team_management_function import team_management_function
from routes.create_team_function import create_team_function
from routes.team_ranking_function import team_ranking_function
from config import auth_codes
from config import auth_codes
from flask import Flask, render_template, request, session
from flask import jsonify
from PIL import Image
from io import BytesIO

import base64
from flask import Flask, render_template, redirect, url_for, request, flash, session

import uuid
# main.py or other files
#from config import notification_manager

from classes.NotificationClass import NotificationManager

import pymssql


from PIL import Image
from io import BytesIO
import pymssql


notification_manager = NotificationManager()

app = Flask(__name__)

teams = []

#################################################################################################################################################################################################

# Add your secret key for session management
app.secret_key = '0123456789abcdef0123456789abcdef'

# Mailjet setup - This allows you to send an email to the user and this is our API information
api_key = '0f502cb98eda788b78d88b0d79feae51'
api_secret = '690bd92e04f6e062c52d10afa0966c3f'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')


# This is where we are keeping track of notifications which are added over time - the user has notifications appear however this will turn into an inbox which they can view
# Therefore this wll aa get extended to a table within azure
#manager = NotificationManager()

#notifications = {}
#notification_manager = NotificationManager()


##################################################################################################################################################################################################
# Home Page e.g. http://127.0.0.1:5000

conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                           user='rcldeveloper',
                           password='media$2009',
                           database='rcldevelopmentdatabase')
cursor = conn.cursor()


def get_db_connection():
    conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                           user='rcldeveloper',
                           password='media$2009',
                           database='rcldevelopmentdatabase')

    return conn



@app.route('/ajax_search_players', methods=['POST'])
def ajax_search_players():
    data = request.json
    search_query = data['search_query']

    # Connect to database and fetch players based on search query
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.Name, p.Ranking
        FROM Players_Dim p
        JOIN UserRegistration u ON p.ID_Var = u.ID_Var
        WHERE LOWER(p.Name) LIKE LOWER(%s);
    """, ('%' + search_query + '%',))

    players_results = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(players_results)

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all players initially
    cursor.execute("""
        SELECT p.Name, p.Ranking
        FROM Players_Dim p
        JOIN UserRegistration u ON p.ID_Var = u.ID_Var;
    """)
    players_results = cursor.fetchall()

    # Rest of your code for teams, etc.

    cursor.close()
    conn.close()

    return render_template('searchpage.html', players=players_results)




def generate_short_unique_id():
    unique_id = str(uuid.uuid4())  # Generate a UUID
    short_id = unique_id[:8]  # Take the first 8 characters as the short ID
    return short_id


def generate_short_unique_idd():
    unique_id = str(uuid.uuid4())  # Generate a UUID
    short_id = unique_id[:4]  # Take the first 8 characters as the short ID
    return str(short_id)  # Convert short_id to a string before returning


@app.route('/create_tournament', methods=['GET', 'POST'])
def create_tournament():
    username = session.get('username')
    if request.method == 'POST':
        # Extract data from form
        name = request.form['name']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        rank_lower_bound = int(request.form['rank_lower_bound'])
        rank_upper_bound = int(request.form['rank_upper_bound'])
        game_type = request.form['game_type']
        description = request.form['description']

        # Generate unique IDs
        unique_id = generate_short_unique_id()
        unique_idd = generate_short_unique_id()

        # Establish a database connection
        conn = get_db_connection()

        if conn:
            try:
                cursor = conn.cursor()

                # Insert data into the database
                cursor.execute(
                    "INSERT INTO Tournaments_Dim (id, TName, start_date, end_date, rank_lower_bound, rank_upper_bound, game_type, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (unique_idd, name, start_date, end_date, rank_lower_bound, rank_upper_bound, game_type, description)
                )

                # Get all users for notifications
                cursor.execute("SELECT ID_Var FROM UserRegistration WHERE ID_Var IS NOT NULL")
                users = cursor.fetchall()
                falses = 'false'

                for user in users:
                    user_id = user[0]
                    notification_message = f"A new tournament '{name}' has been created! Please enroll if interested."
                    cursor.execute(
                        "INSERT INTO Notifications (ID, ID_VAR, mymessages, read_status, tournament_name) VALUES (%s, %s, %s, %s, %s)",
                        (unique_id, user_id, notification_message, falses, name)
                    )

                conn.commit()
                cursor.close()
                conn.close()

                return redirect(url_for('create_tournament'))

            except pymssql.Error as e:
                print(f"Database Error: {e}")
                conn.rollback()  # Rollback the transaction in case of an error

    return render_template('create_tournament.html')
def get_user_id(username):
    conn = pymssql.connect(
        server='rcldevelopmentserver.database.windows.net',
        user='rcldeveloper',
        password='media$2009',
        database='rcldevelopmentdatabase'
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT ID_Var FROM UserRegistration WHERE username = %s", (username,))
    user_id = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return user_id[0] if user_id else None

def is_user_enrolled(user_id, tournament_id):
    conn = pymssql.connect(
        server='rcldevelopmentserver.database.windows.net',
        user='rcldeveloper',
        password='media$2009',
        database='rcldevelopmentdatabase'
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM user_enrollmentss WHERE ID_Var = %s AND tournament_id = %s", (user_id, tournament_id))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return result is not None

def enroll_user(user_id, tournament_id):
    conn = pymssql.connect(
        server='rcldevelopmentserver.database.windows.net',
        user='rcldeveloper',
        password='media$2009',
        database='rcldevelopmentdatabase'
    )
    
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_enrollmentss (ID_Var, tournament_id) VALUES (%s, %s)", (user_id, tournament_id))
    conn.commit()
    cursor.close()
    conn.close()





@app.route('/tournament')
def RCL_Tournament_Screen():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    # Database connection
    conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                           user='rcldeveloper',
                           password='media$2009',
                           database='rcldevelopmentdatabase')
    cursor = conn.cursor()

    # Fetch the user's ID_Var
    cursor.execute("SELECT ID_Var FROM UserRegistration WHERE Username = %s", (username,))
    result = cursor.fetchone()
    user_id = result[0] if result else None

    # Process search query if present
    search_query = request.args.get('search')
    if search_query:
        cursor.execute("SELECT * FROM Tournaments_Dim WHERE tName LIKE %s", ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT * FROM Tournaments_Dim")
    current_tournaments = cursor.fetchall()

    # Fetch user's enrolled tournaments
    enrolled_tournaments = []
    if user_id:
        cursor.execute("SELECT tournament_id FROM user_enrollmentss WHERE ID_Var = %s", (user_id,))
        enrolled_tournaments = [row[0] for row in cursor.fetchall()]

    # Fetch the team ranking of the current user
    team_ranking = None
    if user_id:
        cursor.execute("SELECT Team_ID FROM TeamPlayers WHERE Player_ID = %s", (user_id,))
        team_id_row = cursor.fetchone()
        if team_id_row:
            team_id = team_id_row[0]
            cursor.execute("SELECT Ranking FROM Teams_Dim WHERE ID = %s", (team_id,))
            ranking_row = cursor.fetchone()
            if ranking_row:
                team_ranking = ranking_row[0]

    cursor.close()
    conn.close()

    return render_template('RCL_Tournament_Screen.html',
                           current_tournaments=current_tournaments,
                           enrolled_tournaments=enrolled_tournaments,
                           team_ranking=team_ranking,

              

                           username=username)

@app.route('/enroll_tournament', methods=['POST'])
def enroll_tournament():
    data = request.get_json()
    username = data['username']
    tournament_id = data['tournament_id']
    
    user_id = get_user_id(username)
    
    if user_id and not is_user_enrolled(user_id, tournament_id):
        enroll_user(user_id, tournament_id)
        return jsonify(success=True, message="Enrollment successful")
    else:
        return jsonify(success=False, message="User already enrolled or not found")


# Route to the enrollment page
@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
    if request.method == 'POST':
        # Get the username from the form
        username = request.form['username']
        
        # Get the tournament ID from the form (you can use a dropdown or input field)
        tournament_id = request.form['tournament_id']
        
        # Use the get_user_id function to retrieve the user's ID
        user_id = get_user_id(username)
        
        if user_id is None:
            flash("User not found. Please check the username.")
        else:
            # Check if the user is already enrolled in the tournament
            if is_user_enrolled(user_id, tournament_id):
                flash("You are already enrolled in this tournament.")
            else:
                # If not enrolled, insert the enrollment into the UserEnrollments table
                conn = pymssql.connect(
                    server='rcldevelopmentserver.database.windows.net',
                    user='rcldeveloper',
                    password='media$2009',
                    database='rcldevelopmentdatabase'
                )
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user_enrollmentss (ID_Var, tournament_id) VALUES (%s, %s)", (user_id, tournament_id))
                conn.commit()
                cursor.close()
                conn.close()
                flash("Enrollment successful!")

    # Render the enrollment page with a form
    return render_template('enrollment.html')

@app.route('/TournaLead')
def tourna_lead():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                           user='rcldeveloper',
                           password='media$2009',
                           database='rcldevelopmentdatabase')
    cursor = conn.cursor()

    # Get user ID
    user_id = get_user_id(username)

    # Get teams and rankings
    cursor.execute("SELECT t.ID, t.Name, p.Ranking FROM TeamPlayers tp "
                   "JOIN Teams_Dim t ON tp.Team_ID = t.ID "
                   "JOIN Players_Dim p ON tp.Player_ID = p.ID_Var "
                   "WHERE tp.Player_ID = %s", (user_id,))
    teams_and_rankings = cursor.fetchall()

    cursor.close()
    conn.close()

    no_players = False
    if not teams_and_rankings:
        no_players = True

    return render_template('TournaLead.html', 
                           teams_and_rankings=teams_and_rankings,
                           no_players=no_players,
                           username=username)




# Function to delete old records if count exceeds a threshold
def delete_old_records():
    try:
       

        # Count the number of records
        cursor.execute("SELECT COUNT(*) FROM chat_messages")
        count = cursor.fetchone()[0]

        # Define the threshold (e.g., 50)
        threshold = 50

        if count > threshold:
            # Calculate the number of records to delete
            records_to_delete = count - threshold

            # Delete the oldest records
            cursor.execute(f"DELETE TOP({records_to_delete}) FROM chat_messages")
            conn.commit()

        # Close the database connection
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error deleting records: {str(e)}")

# Route to trigger the record deletion
@app.route('/delete-old-records', methods=['GET'])
def trigger_delete_old_records():
    delete_old_records()
    return 'Old records deleted successfully!'



@app.route('/')
def RCL_Home_Screen():
    username = session.get('username') # Read the username from the session if it's present
    return render_template('RCL_Home_Screen.html',    username = username) # Pass the username to the 

@app.route('/RCL_Main_Template')
def RCL_Main_Template():
    username = session.get('username') # Read the username from the session if it's present
    return render_template('RCL_Main_Template.html',    username = username) # Pass the username to the template

@app.route('/RCL_Header_Template')
def RCL_Header_Template():
    username = session.get('username')
    return render_template('RCL_Header_Template.html',    username = username) # Pass the username to the template

#################################################################################################################################################################################################
# Sign up page e.g. http://127.0.0.1:5000/signup

@app.route('/signup')
def RCL_Signup_Screen():
    return render_template('RCL_Signup_Screen.html')

@app.route('/submit', methods=['POST'])
def submit():
    return signup_function()  # Call the function from signupfunction.py within Routes

##################################################################################################################################################################################################
# Notifications page e.g. http://127.0.0.1:5000/notifications

@app.route('/notifications', methods=['GET', 'POST'])
def show_notifications():
    return notifications_function() # Call the function from notificationsfunction.py within Routes

##################################################################################################################################################################################################

# The user can log into their page http://127.0.0.1:5000/login

@app.route('/login', methods=['GET', 'POST'])
def RCL_Login_Screen():
    username = session.get('username')
    return login_function() # Call the fucntion from loginfunction.py within Routes

#################################################################################################################################################################################################

# The user can log out of their page - http://127.0.0.1:5000/logout

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the user's session to log them outF
    session.pop('username', None)  # Remove the 'username' key from the session

    # Redirect to the login page or any other page you prefer
    return redirect(url_for('RCL_Home_Screen'))

##############################################################################################################################################################################################

# The user can view their profile - http://127.0.0.1:5000/player-profile

@app.route('/player-profile')
def RCL_Player_Profile_Screen():
    return player_profile_function() # Call the function from player_profile_function.py within routes

############################################################################################################################################################################################

# This is how you can see all the player rankings seen within Players_Dim - http://127.0.0.1:5000/player-ranking

@app.route('/player-ranking') 
def RCL_Player_Ranking_Screen():
    return player_ranking_function() # This can be seen within the routes/player_ranking_function

###############################################################################################################################################################################################
# This is how you can see all of the players which can get recruited to team - http://127.0.0.1:5000/recruitment-center

# This is done through recommending other players who are closely matched in ranking

@app.route('/recruitment-centre/', methods=['GET', 'POST'])
def RCL_Recruitment_Centre_Screen():
    return recruitment_function() # This can be seen in routes/recruitment_function

###############################################################################################################################################################################################
#You can create a team - http://127.0.0.1:5000/RCL_Create_Team_Scren

@app.route('/RCL_Create_Team_Screen/', methods=['GET', 'POST'])
def RCL_Create_Team_Screen():
    return create_team_function() # This can be seen in Routes/Create_Team_Function.py

###############################################################################################################################################################################################
#This allows a captain to manage their team - Teams_Dim, and the players within that table can be seen in TeamPlayers

@app.route('/RCL_Team_Management_Screen/', methods=['GET', 'POST'])
def RCL_Team_Management_Screen():
    return team_management_function() # This can be seen in routes/team_management_function

##############################################################################################################################################################################################
# This gives you the ranking of each of the teams, seen in the table Teams_Dim
@app.route('/team-ranking')
def RCL_Team_Ranking_Screen():
    return team_ranking_function() # This can be seen in routes/team_ranking_function

############################################################################################################################################################################################
# Sends an email to the user to reset their password through mailjet

@app.route('/forgot-password')
def RCL_Forgot_Password_Screen():
    return render_template('RCL_Forgot_Password_Screen.html')


def compress_image(image, max_size=800, quality=85):
    """
    Compress the image, resizing and adjusting quality.
    :param image: Uploaded image file.
    :param max_size: Maximum width or height of the image.
    :param quality: Quality of the saved image.
    :return: Compressed image in Bytes.
    """
    # Open the image
    img = Image.open(image)

    # Resize the image if it's too large
    if img.height > max_size or img.width > max_size:
        output_size = (max_size, max_size)
        img.thumbnail(output_size, Image.ANTIALIAS)

    # Save the image to BytesIO object
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=quality)
    img_io.seek(0)

    return img_io





def profile_image_db_loggedoff(username):
    #username = session.get('username') 
    try:
        # Connect to the database
        conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                               user='rcldeveloper',
                               password='media$2009',
                               database='rcldevelopmentdatabase')
        cursor = conn.cursor()
        
        # SQL query to fetch the profile image BLOB
        query = 'SELECT ProfileImageColumn FROM UserRegistration WHERE Username = %s'
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        # Close the database connection
        conn.close()

        if result and result[0] is not None:
            # Convert BLOB to base64 string
            profile_image_blob = result[0]
            profile_image_base64 = base64.b64encode(profile_image_blob).decode("utf-8")
            return f"data:image/jpeg;base64,{profile_image_base64}"
        else:
            return None  # No result or no image found for the given username

    except Exception as e:
        print(f"An error occurred while fetching the profile image URL: {str(e)}")
        return None

def profile_image_db(username):
    username = session.get('username') 
    try:
        # Connect to the database
        conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                               user='rcldeveloper',
                               password='media$2009',
                               database='rcldevelopmentdatabase')
        cursor = conn.cursor()
        
        # SQL query to fetch the profile image BLOB
        query = 'SELECT ProfileImageColumn FROM UserRegistration WHERE Username = %s'
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        # Close the database connection
        conn.close()

        if result and result[0] is not None:
            # Convert BLOB to base64 string
            profile_image_blob = result[0]
            profile_image_base64 = base64.b64encode(profile_image_blob).decode("utf-8")
            return f"data:image/jpeg;base64,{profile_image_base64}"
        else:
            return None  # No result or no image found for the given username

    except Exception as e:
        print(f"An error occurred while fetching the profile image URL: {str(e)}")
        return None



def fetch_banner_image_url_from_db_loggedoff(username):
    #username = session.get('username') 
    try:
        # Connect to the database
        conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                               user='rcldeveloper',
                               password='media$2009',
                               database='rcldevelopmentdatabase')
        cursor = conn.cursor()
        
        # SQL query to fetch the profile image BLOB
        query = 'SELECT PlayerBackground FROM UserRegistration WHERE Username = %s'
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        # Close the database connection
        conn.close()

        if result and result[0] is not None:
            # Convert BLOB to base64 string
            profile_image_blob = result[0]
            profile_image_base64 = base64.b64encode(profile_image_blob).decode("utf-8")
            return f"data:image/jpeg;base64,{profile_image_base64}"
        else:
            return None  # No result or no image found for the given username

    except Exception as e:
        print(f"An error occurred while fetching the profile image URL: {str(e)}")
        return None


def fetch_banner_image_url_from_db(username):
    username = session.get('username') 
    try:
        # Connect to the database
        conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                               user='rcldeveloper',
                               password='media$2009',
                               database='rcldevelopmentdatabase')
        cursor = conn.cursor()
        
        # SQL query to fetch the profile image BLOB
        query = 'SELECT PlayerBackground FROM UserRegistration WHERE Username = %s'
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        # Close the database connection
        conn.close()

        if result and result[0] is not None:
            # Convert BLOB to base64 string
            profile_image_blob = result[0]
            profile_image_base64 = base64.b64encode(profile_image_blob).decode("utf-8")
            return f"data:image/jpeg;base64,{profile_image_base64}"
        else:
            return None  # No result or no image found for the given username

    except Exception as e:
        print(f"An error occurred while fetching the profile image URL: {str(e)}")
        return None


def upload_banner_image_to_db(banner_image, username):
    try:
        # Open the image using Pillow and resize
        img = Image.open(banner_image)
        img.thumbnail((300, 800), Image.ANTIALIAS)  # Resize the image

        # Convert the image to WebP format with optimization
        img_io = BytesIO()
        img.save(img_io, 'WEBP', quality=30, optimize=True)
        img_io.seek(0)
        webp_image_data = img_io.read()

        # Connect to the database
        conn = pymssql.connect(...)  # Fill in your connection details
        cursor = conn.cursor()

        # Update the database with the WebP image data
        cursor.execute('UPDATE UserRegistration SET PlayerBackground = %s WHERE Username = %s',
                       (webp_image_data, username))
        conn.commit()

    except Exception as e:
        print(f"Error uploading banner image: {e}")
        return False
    finally:
        if conn:
            conn.close()
    return True





@app.route('/league')
def RCL_League_Screen():
    return render_template('RCL_League_Screen.html')

@app.route('/matches')
def RCL_Matches_Screen():
    return render_template('RCL_Matches_Screen.html')

@app.route('/my-account')
def RCL_My_Account_Screen():
    return render_template('RCL_My_Account_Screen.html')

@app.route('/team-profile')
def RCL_Team_Profile_Screen():
    return render_template('RCL_Team_Profile_Screen.html')

@app.route('/subscription')
def RCL_Subcription_Screen():
    return render_template('RCL_Subcription_Screen.html')

@app.route('/eagle-eye')
def RCL_Eagle_Eye_Screen():
    return render_template('RCL_Eagle_Eye_Screen.html')

@app.route('/subscribe')
def subscribe():
    # Define your subscription tiers
    tiers = [
        {'name': 'Basic', 'price': '$5.50/month', 'features': ['Feature 1', 'Feature 2']},
        {'name': 'Premium', 'price': '$10/month', 'features': ['Feature 1', 'Feature 2', 'Feature 3']},
        {'name': 'Pro', 'price': '$20/month', 'features': ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4']}
    ]
    return render_template('subscribe.html', tiers=tiers)

@app.route('/get-chat-messages', methods=['GET'])
def get_chat_messages():
    # Connect to your database
    conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                           user='rcldeveloper',
                           password='media$2009',
                           database='rcldevelopmentdatabase')
    cursor = conn.cursor()

    # Fetch recent messages, adjust the query as needed
    cursor.execute("SELECT TOP 50 username, message_text FROM chat_messages ORDER BY timestamp DESC")

    messages = cursor.fetchall()

    # Close the connection
    cursor.close()
    conn.close()

    # Convert messages to a suitable format
    messages = [{'username': msg[0], 'message': msg[1]} for msg in messages]
    return jsonify(messages)


@app.route('/post-chat-message', methods=['POST'])
def post_chat_message():
    if 'username' in session:
        username = session['username']
        message_text = request.form['message']
        
        # Connect to your database
        conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                           user='rcldeveloper',
                           password='media$2009',
                           database='rcldevelopmentdatabase')
        cursor = conn.cursor()

        # Insert the new message
        cursor.execute("INSERT INTO chat_messages (username, message_text) VALUES (%s, %s)", (username, message_text))
        conn.commit()

        # Close the connection
        cursor.close()
        conn.close()

        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'User not logged in'})

def upload_profile_image_to_db(profile_image, username):
    if not allowed_file(profile_image.filename):
        flash('Invalid file format. Please upload a valid image.', 'error')
        return False

    # Generate a unique filename for the image
    filename = secure_filename(profile_image.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    profile_image.save(upload_path)

    # Compress and resize the image
    compressed_image_path = compress_and_resize_image(upload_path)

    # Store the compressed image path in the database
    store_image_in_database(username, compressed_image_path)

    return True

def upload_and_store_image(profile_image, username):
    if not allowed_file(profile_image.filename):
        flash('Invalid file format. Please upload a valid image.', 'error')
        return None

    # Generate a unique filename for the image
    filename = secure_filename(profile_image.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    profile_image.save(upload_path)

    # Generate the URL for the uploaded image (you may need to adjust the URL structure)
    image_url = f'/uploads/{filename}'  # Example URL format

    # Store the image URL in the database
    if store_image_url_in_database(username, image_url):
        return image_url
    else:
        flash('Failed to store image URL in the database.', 'error')
        return None

@app.route('/gamer-profilenotloggedin/<usernamenot>', methods=['GET'])
def gamer_profilenotloggedin(usernamenot):
    #username = session.get('username')
    # Fetch player data based on the username
    player_image_url = fetch_banner_image_url_from_db_loggedoff(usernamenot)
    profile_image_url = profile_image_db_loggedoff(usernamenot)
    player_data = get_player_data(usernamenot)  # Define this function to fetch data from your database

    # If no player data is found, redirect to a 404 page or give a user not found message
    if not player_data:
        return "User not found", 404

    cursor.execute("SELECT ID_Var FROM UserRegistration WHERE Username = %s", (usernamenot,))

    conn.commit()
    
    result = cursor.fetchone()
    user_id = result[0] if result else None

    enrolled_tournaments = []
    if user_id:
        # Fetch tournaments in which the user is enrolled
        cursor.execute("SELECT tournament_id FROM user_enrollments WHERE ID_Var = %s", (user_id,))
        tournaments = cursor.fetchall()
        for tournament in tournaments:
            # Assuming tournament_id is enough for display, otherwise join with tournaments table to fetch more details
            enrolled_tournaments.append(tournament[0])


    #username = session['username']
    user_id = get_user_id(usernamenot)  # Make sure you have this function to get the user's ID
    print(user_id)


   # Check if the user is a captain, co-captain, or a team player
    cursor.execute("SELECT ur.ID_Var, tp.Team_ID FROM UserRegistration ur JOIN TeamPlayers tp ON ur.ID_Var = tp.Player_ID WHERE ur.Username = %s", (usernamenot,))
    user_team_result = cursor.fetchone()

    user_role = "Not part of a team"
    if user_team_result:
        user_id, team_id = user_team_result
        cursor.execute("SELECT CaptainID, CoCaptainID FROM Teams_Dim WHERE Team_ID = %s", (team_id,))
        captain_result = cursor.fetchone()
        if captain_result:
            if captain_result[0] == user_id:
                user_role = "Captain"
            elif len(captain_result) > 1 and captain_result[1] == user_id:
                user_role = "Co-Captain"
            else:
                user_role = "Team Player"

    user_team_name = None  # Default to None if no team is found
    if user_id:
        try:
            # Query to check if the user is part of a team
            cursor.execute("SELECT Team_ID FROM TeamPlayers WHERE Player_ID = %s", (user_id,))
            team_id_result = cursor.fetchone()

            if team_id_result:
                team_id = team_id_result[0]

                # Query to get the team's name using the Team_ID
                cursor.execute("SELECT Name FROM Teams_Dim WHERE Team_ID = %s", (team_id,))
                team_name_result = cursor.fetchone()

                if team_name_result:
                    user_team_name = team_name_result[0]
        except Exception as e:
            print(f"Error fetching team data: {e}")

    # Render the gamer's profile page without the option to upload images
    return render_template('profilenotloggedin.html',  user_team_name = user_team_name, user_role = user_role, profile_image_url = profile_image_url, player_image_url =  player_image_url, player=player_data)

def get_player_data(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT p.Name, p.Ranking, p.GamesPlayed, p.GamesWon, u.ProfileImageColumn
        FROM Players_Dim p
        JOIN UserRegistration u ON p.ID_Var = u.ID_Var
        WHERE p.Name = %s
        """
        cursor.execute(query, (username,))
        player_row = cursor.fetchone()
        
        if player_row:
            player_data = {
                'username': player_row[0],
                'ranking': player_row[1],
                'games_played': player_row[2],
                'games_won': player_row[3],
                'profile_image_url': player_row[4]  # Assumes this is a URL or a path to the image
            }
            return player_data
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        conn.close()



# Route to render the gamer's profile page with the profile image upload form
@app.route('/gamer-profile', methods=['GET', 'POST'])
def gamer_profile():
    username = session.get('username')
    if request.method == 'POST':
        # Check if an image file is uploaded
        if 'profile_image' in request.files:
            profile_image = request.files['profile_image']
            if profile_image.filename != '' and session.get('username') == 'prabbi123':
                # Process and upload the image to the database
                if upload_profile_image_to_db(profile_image, session['username']):
                    # Image uploaded successfully, you can redirect or render a success message
                    return "Profile image uploaded successfully!"


    conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                                   user='rcldeveloper',
                                   password='media$2009',
                                   database='rcldevelopmentdatabase')
    cursor = conn.cursor()

    cursor.execute("SELECT ID_Var FROM UserRegistration WHERE Username = %s", (username,))

    conn.commit()
    
    result = cursor.fetchone()
    user_id = result[0] if result else None

    enrolled_tournaments = []
    if user_id:
        # Fetch tournaments in which the user is enrolled
        cursor.execute("SELECT tournament_id FROM user_enrollments WHERE ID_Var = %s", (user_id,))
        tournaments = cursor.fetchall()
        for tournament in tournaments:
            # Assuming tournament_id is enough for display, otherwise join with tournaments table to fetch more details
            enrolled_tournaments.append(tournament[0])


    #username = session['username']
    user_id = get_user_id(username)  # Make sure you have this function to get the user's ID
    print(user_id)

    

    if request.method == 'POST':
        if 'tournament_id' in request.form:
            tournament_id = request.form['tournament_id']

            conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                                   user='rcldeveloper',
                                   password='media$2009',
                                   database='rcldevelopmentdatabase')
            cursor = conn.cursor()

            cursor.execute("UPDATE Notifications SET read_status = 'true' WHERE ID_Var = %s", (user_id,))

            conn.commit()

            try:
                if not is_user_enrolled(user_id, tournament_id):
                    cursor.execute("INSERT INTO user_enrollmentss (ID_Var, tournament_id) VALUES (%s, %s)", 
                                   (user_id, tournament_id))
                    

                    conn.commit()
                    flash(f"You have successfully enrolled in tournament {tournament_id}.", "success")
                else:
                    flash("You are already enrolled in this tournament.", "info")

            except Exception as e:
                conn.rollback()  # Rollback in case of error
                flash(f'An error occurred: {str(e)}', 'error')

            finally:
                cursor.close()
                conn.close()




    conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                           user='rcldeveloper',
                           password='media$2009',
                           database='rcldevelopmentdatabase')


    cursor = conn.cursor()


   # Check if the user is a captain, co-captain, or a team player
    cursor.execute("SELECT ur.ID_Var, tp.Team_ID FROM UserRegistration ur JOIN TeamPlayers tp ON ur.ID_Var = tp.Player_ID WHERE ur.Username = %s", (username,))
    user_team_result = cursor.fetchone()

    user_role = "Not part of a team"
    if user_team_result:
        user_id, team_id = user_team_result
        cursor.execute("SELECT CaptainID, CoCaptainID FROM Teams_Dim WHERE Team_ID = %s", (team_id,))
        captain_result = cursor.fetchone()
        if captain_result:
            if captain_result[0] == user_id:
                user_role = "Captain"
            elif len(captain_result) > 1 and captain_result[1] == user_id:
                user_role = "Co-Captain"
            else:
                user_role = "Team Player"


    user_team_name = None  # Default to None if no team is found
    if user_id:
        try:
            # Query to check if the user is part of a team
            cursor.execute("SELECT Team_ID FROM TeamPlayers WHERE Player_ID = %s", (user_id,))
            team_id_result = cursor.fetchone()

            if team_id_result:
                team_id = team_id_result[0]

                # Query to get the team's name using the Team_ID
                cursor.execute("SELECT Name FROM Teams_Dim WHERE Team_ID = %s", (team_id,))
                team_name_result = cursor.fetchone()

                if team_name_result:
                    user_team_name = team_name_result[0]
        except Exception as e:
            print(f"Error fetching team data: {e}")


    cursor.execute("SELECT Ranking, GamesPlayed, ProfileViews, GamesWon FROM Players_Dim WHERE Name = %s", (username,))
    user_stats = cursor.fetchone()

    # Ensure user_stats is not None
    if user_stats:
        ranking, matches_played, profile_views, games_won = user_stats
    else:
        # Default values if user is not found
        ranking, matches_played, profile_views, games_won = 0, 0, 0,0



    cursor.execute("SELECT ID_Var FROM UserRegistration WHERE Username = %s", (username,))

   
    result = cursor.fetchone()

    if result is not None:
        user_id = result[0]
        # Proceed with the rest of your logic using user_id

        # ... rest of your code that depends on user_id ...

    else:
        # User not found in the database
        # You can redirect them to a login page or show an error message
        flash('User not found. Please log in.', 'error')
        return redirect(url_for('RCL_Home_Screen'))  # Replace 'login' with the name of your login route
    #user_id = cursor.fetchone()[0]

        # Get notifications for the user
    notifications = notification_manager.get_notifications(user_id)  # <-- Add this line

    # Fetch achievements and leaderboards data from the database
    achievements_data, leaderboard_data = fetch_data_from_database()

    username = session.get('username') 

    profile_image_url = fetch_profile_image_url_from_db('prabbi123')  # Replace with your actual function to fetch the image
    #print(profile_image_url)  # Debugging line

    cursor.execute("SELECT ID_Var FROM UserRegistration WHERE username =  %s", (username,))
    user_id = cursor.fetchone()

    
        # Fetch notifications for the user
    cursor.execute("SELECT * FROM Notifications WHERE ID_Var = %s AND read_status = 'false'", (user_id,))


    tournament_alerts = cursor.fetchall()
    print("Tournament Alerts: ", tournament_alerts)
    cursor.close()

    #return render_template('gamer_profile.html', tournament_alerts=tournament_alerts)
    banner_image_url = fetch_banner_image_url_from_db(username)

    # Fetch the user's profile image URL (modify as per your schema)
    # profile_image_url = fetch_profile_image_url(session['username'])

    # Render the HTML template with the fetched data and profile image URL
    return render_template('gamer_profile.html', ranking=ranking,user_team_name=user_team_name, banner_image_url=banner_image_url,
                            games_won = games_won,
                           matches_played=matches_played,
                           profile_views=profile_views, 
                           tournament_alerts=tournament_alerts, 
                           notifications=notifications,  
                           achievements_data=achievements_data, 
                           leaderboard_data=leaderboard_data,  
                           profile_image_url=profile_image_url, user_role = user_role ,enrolled_tournaments=enrolled_tournaments,
                           username = username)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}

def resize_and_compress_image(profile_image):
    try:
        # Open the image using PIL
        img = Image.open(profile_image)

        # Resize the image to a smaller resolution (e.g., 100x100 pixels)
        img.thumbnail((100, 100))

        # Save the compressed and resized image
        img.save('path_to_save_compressed_image', 'JPEG', quality=70)

        return True
    except Exception as e:
        print(f"Error while resizing and compressing image: {str(e)}")
        return False

def get_data():
    
    cursor.execute('SELECT tournament_id, ID_Var FROM user_enrollmentss')
    data = cursor.fetchall()
    
    return data


@app.route('/enrollments', methods=['GET', 'POST'])
def user_enrollments():
    if request.method == 'POST':
        username = request.form['username']
        tournament_id = request.form['tournament_id']
        user_id = get_user_id(username)
        
        if user_id is None:
            flash("User not found. Please check the username.")
        elif is_user_enrolled(user_id, tournament_id):
            flash("You are already enrolled in this tournament.")
        else:
            enroll_user(user_id, tournament_id)
            flash("Enrollment successful!")


        conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                                   user='rcldeveloper',
                                   password='media$2009',
                                   database='rcldevelopmentdatabase')
        cursor = conn.cursor()

        cursor.execute("UPDATE Notifications SET read_status = 'true' WHERE ID_Var = %s", (user_id,))

        conn.commit()

    data = get_data()  # This function should fetch enrollment data
    return render_template('user_enrollments.html', data=data)



@app.route('/upload-image', methods=['POST'])
def upload_image():
    # Fetch the currently logged-in username from the session
    username = session.get('username')
    if not username:
        flash("User is not logged in.", "error")
        return redirect(url_for('RCL_Login_Screen'))

    # Check if the post request has the file part
    if 'profile_image' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    profile_image = request.files['profile_image']
    
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if profile_image.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)
    
    if profile_image and allowed_file(profile_image.filename):
        if upload_profile_image_to_db(profile_image, username):
            flash('Image successfully uploaded', 'success')
            return redirect(url_for('gamer_profile'))
        else:
            flash('Failed to upload image', 'error')

    flash('Invalid file format.', 'error')
    return redirect(url_for('gamer_profile'))


def fetch_profile_image_url_from_db(username):
    username = session.get('username') 
    try:
        # Connect to the database
        conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                               user='rcldeveloper',
                               password='media$2009',
                               database='rcldevelopmentdatabase')
        cursor = conn.cursor()
        

        # SQL query to fetch the profile image BLOB
        query = 'SELECT ProfileImageColumn FROM UserRegistration WHERE Username = %s'
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        # Close the database connection
        conn.close()

        if result and result[0] is not None:
            # Convert BLOB to base64 string
            profile_image_blob = result[0]
            profile_image_base64 = base64.b64encode(profile_image_blob).decode("utf-8")
            return f"data:image/jpeg;base64,{profile_image_base64}"
        else:
            return None  # No result or no image found for the given username

    except Exception as e:
        print(f"An error occurred while fetching the profile image URL: {str(e)}")
        return None





def upload_profile_image_to_db(profile_image, username):
    try:
        # Open the image using Pillow
        img = Image.open(profile_image)

        # Resize the image (if needed) and convert to WebP format
        img.thumbnail((300, 00), Image.ANTIALIAS)  # Resize the image if it's larger than 800x800
        img_io = BytesIO()
        img.save(img_io, 'WEBP', quality=30)  # Convert to WebP format with reduced quality
        img_io.seek(0)
        webp_image_data = img_io.read()

        # Connect to the database
        conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                               user='rcldeveloper',
                               password='media$2009',
                               database='rcldevelopmentdatabase')
        cursor = conn.cursor()

        # Update the database with the WebP image data
        cursor.execute('UPDATE UserRegistration SET ProfileImageColumn = %s WHERE Username = %s',
                       (webp_image_data, username))
        conn.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        if conn:
            conn.close()
    return True



    # Function to upload the profile image to the database


# Define a function to fetch achievements and leaderboards data from the database
def fetch_data_from_database():
    try:
        # Connect to the database
        conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                           user='rcldeveloper',
                           password='media$2009',
                           database='rcldevelopmentdatabase')
        cursor = conn.cursor()

        # Fetch achievements data from the TournamentAchivements table
        cursor.execute('SELECT TournamentName, TeamID FROM TournamentAchivements')
        achievements_data = cursor.fetchall()

        # Fetch leaderboard data from the Leaderboard table
        cursor.execute('SELECT TeamID, Position FROM Leaderboard')
        leaderboard_data = cursor.fetchall()



        
            

        # Close the database connection
        conn.close()

        return achievements_data, leaderboard_data
    except Exception as e:
        # Handle any database connection or query errors here
        print(f"An error occurred while fetching data from the database: {str(e)}")
        return [], []




























































############################################ DO NOT DELETE  #################################################################################################################################################

@app.route('/verify', methods=['POST'])
def verify():
    entered_code = request.form['auth_code']
    username = request.form['username']

    code_info = auth_codes.get(username, {})
    stored_code = code_info.get('code')
    timestamp = code_info.get('timestamp')

    if stored_code and datetime.now() - timestamp < timedelta(minutes=30):
        if stored_code == entered_code:
            # Correct code and within time limit
            session['username'] = username  # User is now logged in
            return redirect(url_for('RCL_Home_Screen'))  # Redirect to the home page
        else:
            return "Invalid authentication code."
    else:
        return "Authentication code expired or invalid."



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


def send_confirmation_email(email, link):
    data = {
        'Messages': [
            {
                "From": {"Email": "prabbi.kandola@hotmail.co.uk", "Name": "Prabbiooo"},
                "To": [{"Email": email}],
                "Subject": "Team Addition Confirmation",
                "TextPart": f"Please confirm your addition to the team by clicking this link: {link}"
            }
        ]
    }
    result = mailjet.send.create(data=data)
    return result.status_code


@app.route('/confirm_addition/<token>')
def confirm_addition(token):
    #global auth_codes 
    conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                           user='rcldeveloper',
                           password='media$2009',
                           database='rcldevelopmentdatabase')
    cursor = conn.cursor()

    # Verify token and add player to the team
    if token in auth_codes and datetime.now() - auth_codes[token]['timestamp'] < timedelta(hours=24):
        player_id = auth_codes[token]['player_id']
        team_id = auth_codes[token]['team_id']

        team_player_id = generate_team_player_iid(cursor)
        # Add player to the team
        cursor.execute("INSERT INTO TeamPlayers (TeamPlayer_ID, Team_ID, Player_ID) VALUES (%s,%s, %s)", (team_player_id, team_id, player_id))
        cursor.execute("UPDATE Teams_Dim SET NumOfPlayers = NumOfPlayers + 1 WHERE ID = %s", (team_id,))
        conn.commit()

        # Optionally, remove token from auth_codes if it shouldn't be reused
        del auth_codes[token]

        message = "Player successfully added to the team."
    else:
        message = "Invalid or expired token."

    cursor.close()
    conn.close()

    return message  # You can replace this with a redirect or a template rendering


def generate_team_player_iid(cursor):
    # Fetch the latest TeamPlayer_ID
    cursor.execute("SELECT MAX(TeamPlayer_ID) FROM TeamPlayers")
    last_id_row = cursor.fetchone()[0]

    if last_id_row:
        # Extract the numeric part and increment
        last_id_number = int(last_id_row.split('-')[1])
        new_id_number = last_id_number + 1
    else:
        new_id_number = 1001  # Start from 1001 if no IDs are present

    return f"TP-{new_id_number}"



#################### EXAMPLE CODE ON HOW TO CREATE AND USE SESSIONS #######################################################################################################################################




@app.route('/my-teams')
def my_teams():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        username = session['username']

        # Connect to your database
        conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
        cursor = conn.cursor()

        # Get the user's ID_Var
        cursor.execute("SELECT ID_Var FROM UserRegistration WHERE Username = %s", (username,))
        user_id = cursor.fetchone()
        if user_id is None:
            raise Exception("User not found")

        user_id = user_id[0]

        # Query to find teams where the user is the captain
        cursor.execute("SELECT ID, Name FROM Teams_Dim WHERE CaptainID = %s", (user_id,))
        teams_managed = cursor.fetchall()

        cursor.close()
        conn.close()

        # Check if the user has teams
        if not teams_managed:
            return "You are not managing any teams."

        # Render a template with the teams
        return render_template('my_teams.html', teams=teams_managed)


    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return "An error occurred while trying to fetch your teams."









def upload_banner_image_to_db(banner_image, username):
    try:
        # Open a new database connection
        conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                               user='rcldeveloper',
                               password='media$2009',
                               database='rcldevelopmentdatabase')
        cursor = conn.cursor()

        # Read the image file and prepare it for binary database storage
        image_data = banner_image.read()

        # Update the PlayerBackground column for the user in the UserRegistration table
        cursor.execute('UPDATE UserRegistration SET PlayerBackground = %s WHERE Username = %s',
                       (image_data, username))
        conn.commit()

        # Close the database connection
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"An error occurred while uploading the banner image: {e}")
        return False

@app.route('/upload-banner-image', methods=['POST'])
def upload_banner_image():
    username = session.get('username')
    if not username:
        flash("You must be logged in to upload a banner image.", "error")
        return redirect(url_for('login'))

    if 'banner_image' in request.files:
        banner_image = request.files['banner_image']
        if banner_image and allowed_file(banner_image.filename):
            success = upload_banner_image_to_db(banner_image, username)
            if success:
                flash("Banner image uploaded successfully.", "success")
                return redirect(url_for('gamer_profile'))
            else:
                flash("Failed to upload banner image.", "error")
        else:
            flash("Invalid file format.", "error")

    return redirect(url_for('gamer_profile'))






if __name__ == '__main__':
    app.run(debug=True)


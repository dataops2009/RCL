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

app = Flask(__name__)

teams = []

#################################################################################################################################################################################################

# Add your secret key for session management
app.secret_key = '0123456789abcdef0123456789abcdef'

# Mailjet setup
api_key = '0f502cb98eda788b78d88b0d79feae51'
api_secret = '690bd92e04f6e062c52d10afa0966c3f'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

manager = NotificationManager()
notifications = {}
notification_manager = NotificationManager()


##################################################################################################################################################################################################
# Home Page e.g. http://127.0.0.1:5000

@app.route('/')
def RCL_Home_Screen():
    return render_template('RCL_Home_Screen.html')

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

@app.route('/login', methods=['GET', 'POST'])
def RCL_Login_Screen():
    return login_function()

#################################################################################################################################################################################################

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the user's session to log them outF
    session.pop('username', None)  # Remove the 'username' key from the session

    # Redirect to the login page or any other page you prefer
    return redirect(url_for('login'))

##############################################################################################################################################################################################

@app.route('/player-profile')
def RCL_Player_Profile_Screen():
    return player_profile_function()

############################################################################################################################################################################################

# This is how you can see all the player rankings seen within Players_Dim

@app.route('/player-ranking')
def RCL_Player_Ranking_Screen():
    return player_ranking_function() # This can be seen within the routes/player_ranking_function

###############################################################################################################################################################################################
# This is how you can see all of the players which can get recruited to team

@app.route('/recruitment-centre/', methods=['GET', 'POST'])
def RCL_Recruitment_Centre_Screen():
    return recruitment_function() # This can be seen in routes/recruitment_function

###############################################################################################################################################################################################
#You can create a team

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

@app.route('/forgot-password')
def RCL_Forgot_Password_Screen():
    return render_template('RCL_Forgot_Password_Screen.html')

###################################################################### THE FUNCTIONALITY NEEDS TO GET COMPLETED ############################################################################

@app.route('/tournament')
def RCL_Tournament_Screen():
    return render_template('RCL_Tournament_Screen.html')

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





############################################ HANDLING AUTHENTICATION ###########################################################################################################################

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
            return redirect(url_for('home'))  # Redirect to the home page
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



if __name__ == '__main__':
    app.run(debug=True)

import flask
from flask import Flask, request, redirect, url_for, render_template, flash, session

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
import uuid  


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
from config import auth_codes
from config import auth_codes
# main.py or other files
from config import notification_manager

from classes.NotificationClass import NotificationManager
from classes.OCR_Score_ExtractorClass import OCRProcessor  #

from classes.TournamentBuilderClass import Tournament
from classes.TournamentManager import TournamentManager

import io

from PIL import Image
import pytesseract

#from classes.pythonscripts import generate_html_tables

import uuid

import re
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

@app.route('/')
def RCL_Home_Screen():
    return render_template('RCL_Home_Screen.html')

###########################################################################################################################################################################################
@app.route('/hello')
def index():
    conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
    cursor = conn.cursor()
    cursor.execute('SELECT id, tName FROM Tournaments_Dim')  # Modify this query as needed
    tournaments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', tournaments=tournaments)

def generate_match_id():
    return str(uuid.uuid4())

@app.route('/success')
def success():
    # Add your logic for the success page here
    return "Success Page"



@app.route('/uploading', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    points = request.form.get('points')  # points should be a string like "x1,y1;x2,y2;x3,y3;x4,y4"
    points = [tuple(map(int, p.split(','))) for p in points.split(';')]

    image_data = np.fromstring(file.read(), np.uint8)
    ocr_processor = OCRProcessor(image_data)
    ocr_processor.preprocess(points)
    results = ocr_processor.process_and_extract_text()
    return jsonify(results)


def extract_team_points_and_winner(text):
    # Use regular expression to find the pattern "CAPITALIZATION1 POINTS1 POINTS2 CAPITALIZATION2"
    pattern = r'([A-Z]+)\s+(\d+)\s+(\d+)\s+([A-Z]+)'
    matches = re.findall(pattern, text)
    
    team_names = []
    points1_values = []
    points2_values = []
    
    for match in matches:
        team_name1 = match[0]
        points1 = int(match[1])
        points2 = int(match[2])
        team_name2 = match[3]
        
        team_names.append((team_name1, team_name2))
        points1_values.append(points1)
        points2_values.append(points2)
    
    # Determine the winner based on points
    winner = None
    if points1_values and points2_values:
        if points1_values[0] > points2_values[0]:
            winner = team_names[0][0]
        elif points2_values[0] > points1_values[0]:
            winner = team_names[0][1]
        else:
            winner = "DRAW"
    
    return team_names, points1_values, points2_values, winner


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    text_extracted = False
    extracted_text = ""
    stage = None
    tournament_id = None
    final_stage_data = []
    team_points = ""
    team1_points = ""


    if request.method == 'POST':
        conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
        cursor = conn.cursor()
        tournament_id = request.form.get('tournament')
        stage = request.form.get('stage')
        team1_id = request.form.get('team1')
        team2_id = request.form.get('team2')
        team1_score = request.form.get('team1_score')
        team2_score = request.form.get('team2_score')
        winner_team_id = request.form.get('winner_team_id')
        match_id = request.form.get('match_id')

    if 'file' in request.files:

            file = request.files['file']

            if file and file.filename != '':
               
                text_extracted = True
                image_data = file.read()

                # Create an instance of OCRProcessor and perform OCR
                ocr_processor = OCRProcessor(image_data)
                ocr_results = ocr_processor.perform_ocr()
                extracted_text = ' '.join([res[1] for res in ocr_results])

                #max_length = 250  # Set this to the max length allowed by your database column
                #extracted_text = extracted_text[:max_length]

                team_names, points1_values, points2_values, winner = extract_team_points_and_winner(extracted_text)
               # Create a string to display team points
                team_points_str = f"Team1: {points1_values}, Team2: {winner}, Team2: {points2_values} "

                flash('Extracted team points:\n' + team_points_str)

                # Update the database with OCR extracted text

                try:
                    cursor.execute(
                        "UPDATE MatchProgression SET Team1Score=%s, Team2Score=%s, WinnerTeamID=%s, WHERE MatchID=%s",
                        (points1_values, points2_values, winner_team_id,  match_id)
                    )
                    conn.commit()
                except Exception as e:
                    print("Database Error:", e)
                finally:
                    conn.close()
                return redirect(url_for('upload'))


    elif request.method == 'GET':
        tournament_id = request.args.get('tournament')
        stage = request.args.get('stage')

        if stage == 'initial':
            conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
            cursor = conn.cursor()
            cursor.execute("SELECT MatchID, Team1ID, Team2ID FROM MatchProgression WHERE TournamentID=%s AND Stage='initial'", (tournament_id,))
            stage_data = [{'match_id': row[0], 'team1_id': row[1], 'team2_id': row[2]} for row in cursor.fetchall()]
            conn.close()
            return render_template('initial_stage.html', initial_stage_data=stage_data)

        if stage == 'final':
            conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
            cursor = conn.cursor()
            tournament_manager = TournamentManager(conn)
            initial_winners = tournament_manager.get_initial_winners(tournament_id)
            final_matches = tournament_manager.pair_up_winners(initial_winners)

            for match in final_matches:
                match_id = generate_match_id()
                cursor.execute(
                    "INSERT INTO MatchProgression (MatchID, TournamentID, Stage, Team1ID, Team2ID) VALUES (%s, %s, 'final', %s, %s)",
                    (match_id, tournament_id, match[0], match[1])
                )

                final_stage_data.append({
                    'match_id': match_id, 
                    'tournament_id': tournament_id, 
                    'team1_id': match[0], 
                    'team2_id': match[1]
                })

            conn.commit()
            conn.close()
            return render_template('final_stage.html', final_stage_data=final_stage_data)

        elif stage == 'lastMatch':
            conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
            cursor = conn.cursor()
            cursor.execute("SELECT TOP 2 WinnerTeamID FROM MatchProgression WHERE TournamentID=%s AND Stage='final' ORDER BY MatchID DESC", (tournament_id,))
            last_winners = cursor.fetchall()

            if len(last_winners) == 2:
                match_id = generate_match_id()
                team1_id = last_winners[0][0]
                team2_id = last_winners[1][0]

                cursor.execute(
                    "INSERT INTO MatchProgression (MatchID, TournamentID, Stage, Team1ID, Team2ID) VALUES (%s, %s, 'lastMatch', %s, %s)",
                    (match_id, tournament_id, team1_id, team2_id)
                )

                conn.commit()
                conn.close()

                final_stage_data = [{
                    'match_id': match_id,
                    'tournament_id': tournament_id,
                    'team1_id': team1_id,
                    'team2_id': team2_id
                }]
                return render_template('final_stage.html', final_stage_data=final_stage_data)
            else:
                conn.close()
                return render_template('no_matches.html')

    return render_template('upload.html', tournament_id=tournament_id, stage=stage)


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
    return login_function() # Call the fucntion from loginfunction.py within Routes

#################################################################################################################################################################################################

# The user can log out of their page - http://127.0.0.1:5000/logout

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the user's session to log them outF
    session.pop('username', None)  # Remove the 'username' key from the session

    # Redirect to the login page or any other page you prefer
    return redirect(url_for('login'))

##############################################################################################################################################################################################################


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

###################################################################### THE FUNCTIONALITY NEEDS TO GET COMPLETED ############################################################################


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















if __name__ == '__main__':
    app.run(debug=True)
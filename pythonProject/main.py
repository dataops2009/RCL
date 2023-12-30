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

from NotificationClass import NotificationManager

app = Flask(__name__)

teams = []


# Add your secret key for session management
app.secret_key = '0123456789abcdef0123456789abcdef'

# Mailjet setup
api_key = '0f502cb98eda788b78d88b0d79feae51'
api_secret = '690bd92e04f6e062c52d10afa0966c3f'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

manager = NotificationManager()

notifications = {}


notification_manager = NotificationManager()


@app.route('/notifications')
def show_notifications():
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


auth_codes = {}
@app.route('/login', methods=['GET', 'POST'])
def RCL_Login_Screen():
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
            # Here you can handle what happens next (e.g., redirect to profile)
            session['username'] = username  # Log the user in
            return redirect(url_for('home'))  # Redirect to the home page
        else:
            # User authentication failed
            return "Invalid username or password"

    return render_template('RCL_Login_Screen.html')


@app.route('/')
def RCL_Home_Screen():
    return render_template('RCL_Home_Screen.html')

@app.route('/forgot-password')
def RCL_Forgot_Password_Screen():
    return render_template('RCL_Forgot_Password_Screen.html')

@app.route('/signup')
def RCL_Signup_Screen():
    return render_template('RCL_Signup_Screen.html')

@app.route('/tournament')
def RCL_Tournament_Screen():
    return render_template('RCL_Tournament_Screen.html')

@app.route('/league')
def RCL_League_Screen():
    return render_template('RCL_League_Screen.html')

@app.route('/matches')
def RCL_Matches_Screen():
    return render_template('RCL_Matches_Screen.html')

@app.route('/player-profile')
def RCL_Player_Profile_Screen():
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

@app.route('/player-ranking')
def RCL_Player_Ranking_Screen():
    conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
    cursor = conn.cursor()

    # Fetching data from Players_Dim table
    cursor.execute("SELECT ID, Name, TeamID, GamesPlayed, GamesWon, GamesLost, GamesDrawn, WinLostRatio, ID_Var, Ranking FROM Players_Dim")
    players_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('RCL_Player_Ranking_Screen.html', players_data=players_data)
@app.route('/recruitment-centre/', methods=['GET', 'POST'])
def RCL_Recruitment_Centre_Screen():
    # Redirect to login if no user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    # Connect to your database
    conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                           user='rcldeveloper',
                           password='media$2009',
                           database='rcldevelopmentdatabase')
    cursor = conn.cursor()

    try:
        # Fetch ID_Var from UserRegistration table
        cursor.execute("SELECT ID_Var FROM UserRegistration WHERE Username = %s", (username,))
        user_id_row = cursor.fetchone()
        if user_id_row is None:
            return "User not found", 404
        user_id = user_id_row[0]

        # Check if the user is a captain
        cursor.execute("SELECT ID FROM Teams_Dim WHERE CaptainID = %s", (user_id,))
        team_id_row = cursor.fetchone()
        if team_id_row is None:
            return "You are not a captain of any team.", 404
        team_id = team_id_row[0]

        # Fetch team ranking
        cursor.execute("SELECT Ranking FROM Teams_Dim WHERE ID = %s", (team_id,))
        team_ranking_row = cursor.fetchone()
        if not team_ranking_row:
            return f"No team found with ID {team_id}", 404

        team_ranking = team_ranking_row[0]
        if team_ranking is None:
            return f"Team {team_id} has no ranking", 400

        if request.method == 'POST':
            player_id = request.form['player_id']
            cursor.execute("SELECT Email FROM UserRegistration WHERE ID_Var = %s", (player_id,))
            player_email_row = cursor.fetchone()
            if not player_email_row:
                return "Player not found", 404

            player_email = player_email_row[0]
            token = str(uuid.uuid4())
            confirmation_link = f"http://yourwebsite.com/confirm_addition/{token}"
            send_confirmation_email(player_email, confirmation_link)

            auth_codes[token] = {'player_id': player_id, 'team_id': team_id, 'timestamp': datetime.now()}
            return "Invitation sent to the player."

        rank_range = 10
        cursor.execute("""
            SELECT p.ID_Var, p.Name, p.Ranking FROM Players_Dim p
            WHERE p.ID_Var NOT IN (
                SELECT Player_ID FROM TeamPlayers WHERE Team_ID = %s
            ) AND p.Ranking BETWEEN %s AND %s
        """, (team_id, team_ranking - rank_range, team_ranking + rank_range))
        available_players = cursor.fetchall()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return "An error occurred while trying to access the recruitment centre."
    finally:
        cursor.close()
        conn.close()

    return render_template('RCL_Recruitment_Centre_Screen.html', 
                           available_players=available_players, 
                           team_id=team_id)


@app.route('/my-account')
def RCL_My_Account_Screen():
    return render_template('RCL_My_Account_Screen.html')

   


@app.route('/RCL_Team_Management_Screen/', methods=['GET', 'POST'])
def RCL_Team_Management_Screen():
    # Redirect to login if no user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        username = session['username']

        # Connect to your database
        conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
        cursor = conn.cursor()

        # Fetch the user's ID_Var
        cursor.execute("SELECT ID_Var FROM UserRegistration WHERE Username = %s", (username,))
        user_id = cursor.fetchone()[0]

        # Check if the user is a captain
        cursor.execute("SELECT ID FROM Teams_Dim WHERE CaptainID = %s", (user_id,))
        team_id = cursor.fetchone()

        if team_id is None:
            cursor.close()
            conn.close()
            return "You are not a captain of any team."

        # Fetch current team players
        cursor.execute("SELECT tp.TeamPlayer_ID, tp.Team_ID, tp.Player_ID, u.Email, pd.Name FROM TeamPlayers tp "
                       "JOIN UserRegistration u ON tp.Player_ID = u.ID_Var "
                       "JOIN Players_Dim pd ON tp.Player_ID = pd.ID_Var "
                       "WHERE tp.Team_ID = %s", (team_id,))

        current_team_players = cursor.fetchall()

        # Fetch all players for the dropdown
        cursor.execute("SELECT ID_Var, Name FROM Players_Dim")
        all_players = cursor.fetchall()

        if request.method == 'POST':
            action = request.form['action']

            if action == 'add':
                player_id = request.form['player_id']

                # Fetch player email
                cursor.execute("SELECT Email FROM UserRegistration WHERE ID_Var = %s", (player_id,))
                user_email = cursor.fetchone()[0]

                # Generate a unique token
                token = str(uuid.uuid4())
                auth_codes[token] = {'player_id': player_id, 'team_id': team_id, 'timestamp': datetime.now()}

                # Send confirmation email
                confirmation_link = f"http://127.0.0.1:5000/confirm_addition/{token}"
                send_confirmation_email(user_email, confirmation_link)

                try:
                    notification_message = f"You have been invited to join the team with ID {team_id}. Please check your email for the confirmation link."
                    notification_manager.add_notification(player_id, notification_message)
                    return redirect(url_for('show_notifications'))

                except Exception as e:
                    print(f"Error adding notification: {e}")

            # Rest of your code for 'remove' and 'change_name' actions

            conn.commit()

        cursor.close()
        conn.close()

        return render_template('RCL_Team_Management_Screen.html', team_id=team_id, current_team_players=current_team_players, all_players=all_players)

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return "An error occurred while trying to manage the team."



@app.route('/team-profile')
def RCL_Team_Profile_Screen():
    return render_template('RCL_Team_Profile_Screen.html')
@app.route('/team-ranking')
def RCL_Team_Ranking_Screen():
    conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
    cursor = conn.cursor()

    # Fetching data from the relevant table (assuming it's Teams_Dim)
    cursor.execute("SELECT ID, Name, CaptainID, CoCaptainID, NumOfPlayers, GamesPlayed, GamesWon, GamesLost, GamesDrawn, WinLostRatio, Ranking FROM Teams_Dim ORDER BY Ranking")
    teams_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('RCL_Team_Ranking_Screen.html', teams_data=teams_data)


@app.route('/subscription')
def RCL_Subcription_Screen():
    return render_template('RCL_Subcription_Screen.html')

@app.route('/eagle-eye')
def RCL_Eagle_Eye_Screen():
    return render_template('RCL_Eagle_Eye_Screen.html')

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the user's session to log them outF
    session.pop('username', None)  # Remove the 'username' key from the session

    # Redirect to the login page or any other page you prefer
    return redirect(url_for('login'))
    
@app.route('/home')
def home():
    # if 'username' not in session:
    #     return redirect(url_for('login'))

    # try:
    return render_template('RCL_Home_Screen.html')
    #     username = session['username']

    #     # Fetch data from the 'Players_Dim' table based on the username
    #     conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT ID_VAR, Name FROM Players_Dim WHERE Name = %s", (username,))
    #     player_data = cursor.fetchone()  # Use fetchone() to get a single row
    #     cursor.close()
    #     conn.close()

    #     # Render the home page template with the fetched data
    #     return render_template('RCL_Home_Screen.html', username=username, player_data=player_data)
    # except Exception as e:
    #     # Log the exception for debugging
    #     print(f"An error occurred: {str(e)}")
    #     return "An error occurred while loading the home page."

# @app.route('/CreateTeam', methods=['GET'])
# def create_team_form():
#     # ... any necessary logic ...
#     return render_template('RCL_CreateTeam_Screen.html')

# @app.route('/submit-team', methods=['POST'])
# def submit_team():
#     team_name = request.form['team_name']
#     team_description = request.form['team_description']
#     teams.append({'team_name':team_name,'team_description':team_description})
#     # Redirect to the profile or another appropriate page
#     print(teams)
#     return redirect(url_for('SignUp'))
#     return render_template('RCL_Signup_Screen.html')

@app.route('/subscribe')
def subscribe():
    # Define your subscription tiers
    tiers = [
        {'name': 'Basic', 'price': '$5.50/month', 'features': ['Feature 1', 'Feature 2']},
        {'name': 'Premium', 'price': '$10/month', 'features': ['Feature 1', 'Feature 2', 'Feature 3']},
        {'name': 'Pro', 'price': '$20/month', 'features': ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4']}
    ]
    return render_template('subscribe.html', tiers=tiers)


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

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return "Passwords do not match. Please go back and try again."

        
        conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT * FROM UserRegistration WHERE Email = %s", (email,))
        if cursor.fetchone():
            return "Email already registered. Please try another email."

        # Fetch the latest ID and increment it
        cursor.execute("SELECT MAX(ID_Var) FROM Players_Dim")

        last_id_row = cursor.fetchone()
        if last_id_row and last_id_row[0]:
            last_id = int(last_id_row[0].split('-')[1])  # Extract the numeric part and convert to int
            new_id = f"PL-{last_id + 1}"
        else:
            new_id = "PL-1000"


        # Hash the password and insert new user
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO UserRegistration (Username, Email, Password) VALUES (%s, %s, %s)", (username, email, hashed_password))

        cursor.execute("INSERT INTO Players_Dim (ID_Var, Name) VALUES (%s, %s)", (new_id, username))

        conn.commit()
        cursor.close()
        conn.close()

        # Generate and send authentication code
        auth_code = str(random.randint(100000, 999999))
        auth_codes[username] = {'code': auth_code, 'timestamp': datetime.now()}
        email_status = send_auth_code_email(email, auth_code)
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



# @app.route('/CreateTeam', methods=['GET', 'POST'])
# def create_team():
#     if request.method == 'POST':
#         name = request.form['name']
#         captain_username = request.form['captain']
#         co_captain_username = request.form['co_captain']
#         selected_player_usernames = request.form.getlist('selected-players[]')

#         conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
#                                user='rcldeveloper',
#                                password='media$2009',
#                                database='rcldevelopmentdatabase')
#         cursor = conn.cursor()

#         # Generate Team ID for Teams_Dim
#         team_id = generate_id(cursor, 'Teams_Dim', 'ID', 'TD')

#         # Get Captain and Co-Captain IDs
#         cursor.execute("SELECT ID_Var FROM Players_Dim WHERE Name = %s", (captain_username,))
#         captain_id = cursor.fetchone()[0]
#         cursor.execute("SELECT ID_Var FROM Players_Dim WHERE Name = %s", (co_captain_username,))
#         co_captain_id = cursor.fetchone()[0]

#         # Insert team data into Teams_Dim table
#         cursor.execute("""
#             INSERT INTO Teams_Dim (ID, Name, CaptainID, CoCaptainID, NumOfPlayers)
#             VALUES (%s, %s, %s, %s, %s)
#         """, (team_id, name, captain_id, co_captain_id, len(selected_player_usernames)))

#         # Insert selected players into TeamPlayers table
#         for username in selected_player_usernames:
#             cursor.execute("SELECT ID_Var FROM Players_Dim WHERE Name = %s", (username,))
#             player_id = cursor.fetchone()[0]
#             if player_id:
#                 # Generate TeamPlayer ID for TeamPlayers
#                 team_player_id = generate_id(cursor, 'TeamPlayers', 'TeamPlayer_ID', 'TP')
#                 cursor.execute("""
#                     INSERT INTO TeamPlayers (TeamPlayer_ID, Team_ID, Player_ID)
#                     VALUES (%s, %s, %s)
#                 """, (team_player_id, team_id, player_id))

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return "Team created successfully."

#     # Fetch the list of player usernames
#     conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
#                            user='rcldeveloper',
#                            password='media$2009',
#                            database='rcldevelopmentdatabase')
#     cursor = conn.cursor()
#     cursor.execute("SELECT Name FROM Players_Dim")
#     player_list = [row[0] for row in cursor.fetchall()]
#     cursor.close()
#     conn.close()

#     return render_template('RCL_CreateTeam_Screen.html', player_list=player_list)



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

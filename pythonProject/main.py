import pymssql
from flask import Flask, render_template, redirect, url_for, request, render_template_string
import pymssql
from flask import Flask, render_template, redirect, url_for, request, render_template_string, session
from werkzeug.security import generate_password_hash, check_password_hash
from mailjet_rest import Client
import random
from datetime import datetime, timedelta

import uuid


# Creating teams 
# Inviting the players
# Players being able to see their invite from team


app = Flask(__name__)

teams = []


# Add your secret key for session management
app.secret_key = '0123456789abcdef0123456789abcdef'

# Mailjet setup
api_key = '0f502cb98eda788b78d88b0d79feae51'
api_secret = '690bd92e04f6e062c52d10afa0966c3f'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

# Simulated database for storing auth codes and timestamps

auth_codes = {}



 #New route for the Forgot Password page
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        # Check if the email exists in your database
        cursor.execute("SELECT Username FROM UserRegistration WHERE Email = %s", (email,))
        user_record = cursor.fetchone()

        if user_record:
            # Generate and send a verification code via email
            auth_code = str(random.randint(100000, 999999))
            auth_codes[user_record[0]] = {'code': auth_code, 'timestamp': datetime.now()}
            email_status = send_auth_code_email(email, auth_code)

            if email_status == 200:
                return redirect(url_for('password_reset_confirm'))
            else:
                return "Error sending verification code."

    return render_template('forgot_password')

# ... Other routes and logic ...

# New route for the password reset confirmation
@app.route('/password-reset-confirm')
def password_reset_confirm():
    return render_template('password_reset_confirm.html')


@app.route('/subscribe')
def subscribe():
    # Define your subscription tiers
    tiers = [
        {'name': 'Basic', 'price': '$5.50/month', 'features': ['Feature 1', 'Feature 2']},
        {'name': 'Premium', 'price': '$10/month', 'features': ['Feature 1', 'Feature 2', 'Feature 3']},
        {'name': 'Pro', 'price': '$20/month', 'features': ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4']}
    ]
    return render_template('main.html', tiers=tiers)

@app.route('/profile')
def profile():
    # ... any necessary logic ...
    return render_template('main.html')


@app.route('/submit-team', methods=['POST'])
def submit_team():
    user_name = request.form['user_name']
    password = request.form['password']
    teams.append({'user_name':user_name,'password':password})
    # Redirect to the profile or another appropriate page
    print(teams)
    return redirect(url_for('profile'))

@app.route('/main')
def main():
    # Add any necessary logic for the 'main' page
    return render_template('main.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
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

    return render_template('login.html')


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
        cursor.execute("INSERT INTO UserRegistration (Username, Email, Password, ID_Var) VALUES (%s, %s, %s, %s)", (username, email, hashed_password, new_id))

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



@app.route('/logout', methods=['POST'])
def logout():
    # Clear the user's session to log them out
    session.pop('username', None)  # Remove the 'username' key from the session

    # Redirect to the login page or any other page you prefer
    return redirect(url_for('login'))

    
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        username = session['username']
        # Fetch data from the 'Players_Dim' table based on the username
        conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
        cursor = conn.cursor()
        cursor.execute("SELECT ID_VAR, Name FROM Players_Dim WHERE Name = %s", (username,))
        player_data = cursor.fetchone()  # Use fetchone() to get a single row
        cursor.close()
        conn.close()

        # Render the home page template with the fetched data
        return render_template('home.html', username=username, player_data=player_data)
    except Exception as e:
        # Log the exception for debugging
        print(f"An error occurred: {str(e)}")
        return "An error occurred while loading the home page."



def welcome():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    # Fetch user-specific information from the database
    conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM UserRegistration WHERE Username = %s", (username,))
    user_info = cursor.fetchone()
    cursor.close()
    conn.close()

    # Assuming user_info contains the necessary details
    return render_template_string("""
        <html>
            <body>
                <h1>Welcome, {{ username }}!</h1>
                <p>Here is your information:</p>
                <!-- Display user information here -->
            </body>
        </html>
    """, username=username)


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


def generate_id(cursor, table_name, id_column_name, prefix, start_id=1001):
    cursor.execute(f"SELECT MAX({id_column_name}) FROM {table_name}")
    last_id = cursor.fetchone()[0]

    if last_id is None or '-' not in last_id:
        return f"{prefix}-{start_id}"

    number = int(last_id.split('-')[1]) + 1
    return f"{prefix}-{number}"
@app.route('/create-team', methods=['GET', 'POST'])
def create_team():
    if 'username' not in session:
        return redirect(url_for('login'))

    captain_username = session['username']
    conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                           user='rcldeveloper',
                           password='media$2009',
                           database='rcldevelopmentdatabase')
    cursor = conn.cursor()

    # Get Captain's ID_Var from UserRegistration
    cursor.execute("SELECT ID_Var FROM UserRegistration WHERE Username = %s", (captain_username,))
    captain_record = cursor.fetchone()
    if not captain_record:
        cursor.close()
        conn.close()
        return "Captain not found."
    captain_id = captain_record[0]

    if request.method == 'POST':
        name = request.form['name']
        co_captain_username = request.form['co_captain']
        selected_player_usernames = request.form.getlist('selected-players[]')

        # Generate Team ID for Teams_Dim
        team_id = generate_id(cursor, 'Teams_Dim', 'ID', 'TD')

        # Insert team data into Teams_Dim table
        cursor.execute("""
            INSERT INTO Teams_Dim (ID, Name, CaptainID, CoCaptainID, NumOfPlayers)
            VALUES (%s, %s, %s, %s, %s)
        """, (team_id, name, captain_id, None, len(selected_player_usernames)))

        # Insert selected players into TeamPlayers table
        for player_name in selected_player_usernames:
            cursor.execute("SELECT ID_Var FROM Players_Dim WHERE Name = %s", (player_name,))
            player_dim_record = cursor.fetchone()
            if player_dim_record:
                player_id_var = player_dim_record[0]
                cursor.execute("SELECT ID_Var FROM UserRegistration WHERE ID_Var = %s", (player_id_var,))
                user_registration_record = cursor.fetchone()
                if user_registration_record:
                    team_player_id = generate_id(cursor, 'TeamPlayers', 'TeamPlayer_ID', 'TP')
                    cursor.execute("""
                        INSERT INTO TeamPlayers (TeamPlayer_ID, Team_ID, Player_ID)
                        VALUES (%s, %s, %s)
                    """, (team_player_id, team_id, player_id_var))
                else:
                    cursor.close()
                    conn.close()
                    return f"Player {player_name} not found in UserRegistration."
            else:
                cursor.close()
                conn.close()
                return f"Player {player_name} not found in Players_Dim."

        # Update Co-Captain in Teams_Dim
        if co_captain_username:
            cursor.execute("SELECT ID_Var FROM Players_Dim WHERE Name = %s", (co_captain_username,))
            co_captain_dim_record = cursor.fetchone()
            if co_captain_dim_record:
                co_captain_id_var = co_captain_dim_record[0]
                cursor.execute("""
                    UPDATE Teams_Dim
                    SET CoCaptainID = %s
                    WHERE ID = %s
                """, (co_captain_id_var, team_id))

        conn.commit()
        cursor.close()
        conn.close()

        return "Team created successfully."

    # Fetch the list of player names for the form
    cursor.execute("SELECT Name FROM Players_Dim")
    player_list = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    return render_template('create_team.html', player_list=player_list)


@app.route('/team-management/<team_id>', methods=['GET', 'POST'])
def team_management(team_id):
    # Redirect to login if no user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        username = session['username']

        # Connect to your database
        conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
        cursor = conn.cursor()

        # Verify if the logged-in user is the captain of the team
        cursor.execute("SELECT ID_Var FROM UserRegistration WHERE Username = %s", (username,))
        user_id = cursor.fetchone()[0]

        cursor.execute("SELECT CaptainID FROM Teams_Dim WHERE ID = %s", (team_id,))
        team_info = cursor.fetchone()

        if team_info is None or team_info[0] != user_id:
            cursor.close()
            conn.close()
            return "You do not have permission to manage this team."

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

            elif action == 'remove':
                team_player_id = request.form['player_id']
                cursor.execute("DELETE FROM TeamPlayers WHERE TeamPlayer_ID = %s", (team_player_id,))
                cursor.execute("UPDATE Teams_Dim SET NumOfPlayers = NumOfPlayers - 1 WHERE ID = %s", (team_id,))

            elif action == 'change_name':
                new_name = request.form['new_name']
                cursor.execute("UPDATE Teams_Dim SET Name = %s WHERE ID = %s", (new_name, team_id))

            conn.commit()

        cursor.close()
        conn.close()

        return render_template('team_management.html', team_id=team_id, current_team_players=current_team_players, all_players=all_players)

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return "An error occurred while trying to manage the team."


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

@app.route('/recruitment/<team_id>', methods=['GET', 'POST'])
def recruitment(team_id):
    conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                           user='rcldeveloper',
                           password='media$2009',
                           database='rcldevelopmentdatabase')
    cursor = conn.cursor()

    if request.method == 'POST':
        player_id = request.form['player_id']
        cursor.execute("SELECT Email FROM UserRegistration WHERE ID_Var = %s", (player_id,))
        player_email = cursor.fetchone()[0]

        token = str(uuid.uuid4())
        confirmation_link = f"http://yourwebsite.com/confirm_addition/{token}"
        send_confirmation_email(player_email, confirmation_link)

        # Store the token with player and team info for later verification
        auth_codes[token] = {'player_id': player_id, 'team_id': team_id, 'timestamp': datetime.now()}

        return "Invitation sent to the player."

    # Existing code to fetch players with similar ranking
    cursor.execute("SELECT Ranking FROM Teams_Dim WHERE ID = %s", (team_id,))
    team_ranking = cursor.fetchone()[0]
    rank_range = 10

    cursor.execute("""
        SELECT p.ID_Var, p.Name, p.Ranking FROM Players_Dim p
        WHERE p.ID_Var NOT IN (
            SELECT Player_ID FROM TeamPlayers WHERE Team_ID = %s
        ) AND p.Ranking BETWEEN %s AND %s
    """, (team_id, team_ranking - rank_range, team_ranking + rank_range))
    available_players = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('recruitment.html', available_players=available_players, team_id=team_id)



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
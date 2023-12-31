
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

def team_management_function():
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

        # Check if the user is a captain and get their team_id
        cursor.execute("SELECT ID FROM Teams_Dim WHERE CaptainID = %s", (user_id,))
        team_id_row = cursor.fetchone()

        if team_id_row is None:
            cursor.close()
            conn.close()
            return "You are not a captain of any team."

        team_id = team_id_row[0]

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

            elif action == 'remove':
                team_player_id = request.form['player_id']
                cursor.execute("DELETE FROM TeamPlayers WHERE TeamPlayer_ID = %s", (team_player_id,))
                cursor.execute("UPDATE Teams_Dim SET NumOfPlayers = NumOfPlayers - 1 WHERE ID = %s", (team_id,))

            elif action == 'change_name':
                new_name = request.form['new_name']
                cursor.execute("UPDATE Teams_Dim SET Name = %s WHERE ID = %s", (new_name, team_id))



            conn.commit()

        # Fetch current team players
        cursor.execute("SELECT tp.TeamPlayer_ID, tp.Team_ID, tp.Player_ID, u.Email, pd.Name FROM TeamPlayers tp "
                       "JOIN UserRegistration u ON tp.Player_ID = u.ID_Var "
                       "JOIN Players_Dim pd ON tp.Player_ID = pd.ID_Var "
                       "WHERE tp.Team_ID = %s", (team_id,))
        current_team_players = cursor.fetchall()

        # Fetch all players for the dropdown
        cursor.execute("SELECT ID_Var, Name FROM Players_Dim")
        all_players = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('RCL_Team_Management_Screen.html', team_id=team_id, current_team_players=current_team_players, all_players=all_players)

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return "An error occurred while trying to manage the team."


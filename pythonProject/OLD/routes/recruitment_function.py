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

def recruitment_function():
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

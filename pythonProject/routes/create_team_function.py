
from flask import Flask, render_template, redirect, url_for, request, render_template_string, session
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from mailjet_rest import Client
import random
from datetime import datetime, timedelta


def create_team_function():
    if request.method == 'POST':
        name = request.form['name']
        captain_username = request.form['captain']
        co_captain_username = request.form['co_captain']
        selected_player_usernames = request.form.getlist('selected-players[]')

        conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                               user='rcldeveloper',
                               password='media$2009',
                               database='rcldevelopmentdatabase')
        cursor = conn.cursor()

        # Generate Team ID for Teams_Dim
        team_id = generate_id(cursor, 'Teams_Dim', 'ID', 'TD')

        # Get Captain and Co-Captain IDs
        cursor.execute("SELECT ID_Var FROM Players_Dim WHERE Name = %s", (captain_username,))
        captain_id = cursor.fetchone()[0]
        cursor.execute("SELECT ID_Var FROM Players_Dim WHERE Name = %s", (co_captain_username,))
        co_captain_id = cursor.fetchone()[0]

        # Insert team data into Teams_Dim table
        cursor.execute("""
            INSERT INTO Teams_Dim (ID, Name, CaptainID, CoCaptainID, NumOfPlayers)
            VALUES (%s, %s, %s, %s, %s)
        """, (team_id, name, captain_id, co_captain_id, len(selected_player_usernames)))

        # Insert selected players into TeamPlayers table
        for username in selected_player_usernames:
            cursor.execute("SELECT ID_Var FROM Players_Dim WHERE Name = %s", (username,))
            player_id = cursor.fetchone()[0]
            if player_id:
                # Generate TeamPlayer ID for TeamPlayers
                team_player_id = generate_id(cursor, 'TeamPlayers', 'TeamPlayer_ID', 'TP')
                cursor.execute("""
                    INSERT INTO TeamPlayers (TeamPlayer_ID, Team_ID, Player_ID)
                    VALUES (%s, %s, %s)
                """, (team_player_id, team_id, player_id))

        conn.commit()
        cursor.close()
        conn.close()

        return "Team created successfully."

    # Fetch the list of player usernames
    conn = pymssql.connect(server='rcldevelopmentserver.database.windows.net',
                           user='rcldeveloper',
                           password='media$2009',
                           database='rcldevelopmentdatabase')
    cursor = conn.cursor()
    cursor.execute("SELECT Name FROM Players_Dim")
    player_list = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    return render_template('RCL_CreateTeam_Screen.html', player_list=player_list)




















































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


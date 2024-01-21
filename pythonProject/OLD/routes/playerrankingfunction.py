
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


def player_ranking_function():
    conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
    cursor = conn.cursor()

    # Fetching data from Players_Dim table
    cursor.execute("SELECT ID, Name, TeamID, GamesPlayed, GamesWon, GamesLost, GamesDrawn, WinLostRatio, ID_Var, Ranking FROM Players_Dim")
    players_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('RCL_Player_Ranking_Screen.html', players_data=players_data)

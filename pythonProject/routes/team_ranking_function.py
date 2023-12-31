
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

def team_ranking_function():
    conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
    cursor = conn.cursor()

    # Fetching data from the relevant table (assuming it's Teams_Dim)
    cursor.execute("SELECT ID, Name, CaptainID, CoCaptainID, NumOfPlayers, GamesPlayed, GamesWon, GamesLost, GamesDrawn, WinLostRatio, Ranking FROM Teams_Dim ORDER BY Ranking")
    teams_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('RCL_Team_Ranking_Screen.html', teams_data=teams_data)

import pymssql
from flask import Flask, render_template, redirect, url_for, request, render_template_string



app = Flask(__name__)

teams = []

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

@app.route('/create-team', methods=['GET'])
def create_team_form():
    # ... any necessary logic ...
    return render_template('create_team.html')

@app.route('/submit-team', methods=['POST'])
def submit_team():
    user_name = request.form['user_name']
    password = request.form['password']
    teams.append({'user_name':user_name,'password':password})
    # Redirect to the profile or another appropriate page
    print(teams)
    return redirect(url_for('profile'))


@app.route('/submit', methods=['POST'])
def submit():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # Check if the two passwords match
    if password != confirm_password:
        return "Passwords do not match. Please go back and try again."

    conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009',
                           'rcldevelopmentdatabase')
    cursor = conn.cursor()

    # Insert data into UserRegistration
    cursor.execute("INSERT INTO UserRegistration (Username, Email, Password) VALUES (%s, %s, %s)",
                   (username, email, password))

    # Insert the username into the Players_Dim table
    #cursor.execute("INSERT INTO Players_Dim (ID, Name) VALUES (%s,%s)", (12345, username))

    conn.commit()
    cursor.close()
    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
        <title>Registration Successful</title>
    </head>
    <body>

    <div class="login-box">
        <h2>Registration Successful!</h2>
        <div id="breacherlogo"><img src="{{ url_for('static', filename='images/BreachersLogo_Transparant.png') }}"></div>
        <p>Thank you, {{ username }}, for registering.</p>
    </div>

    </body>
    </html>
    """, username=username)


if __name__ == '__main__':
    app.run(debug=True)

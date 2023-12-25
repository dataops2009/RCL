import pymssql
from flask import Flask, render_template, redirect, url_for, request, render_template_string
import pymssql
from flask import Flask, render_template, redirect, url_for, request, render_template_string, session
from werkzeug.security import generate_password_hash, check_password_hash
from mailjet_rest import Client
import random
from datetime import datetime, timedelta


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
            return redirect(url_for('profile'))
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
        
        cursor.execute("INSERT INTO UserRegistration (Username, Email, Password) VALUES (%s, %s, %s)", (username, email, password))
        #cursor.execute("INSERT INTO Players_Dim (ID, Name) VALUES (%s,%s)", (12345, username))

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

    return render_template_string("""
        <html>
            <body>
                <form action="/signup" method="post">
                    Username: <input type="text" name="username"><br>
                    Email: <input type="text" name="email"><br>
                    Password: <input type="password" name="password"><br>
                    Confirm Password: <input type="password" name="confirm_password"><br>
                    <input type="submit" value="Submit">
                </form>
            </body>
        </html>
    """)

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
            return render_template_string("""
                <html>
                    <body>
                        <h1>Verification successful!</h1>
                        <p>Welcome, {{ username }}. You are now logged in.</p>
                        <!-- Redirect to profile or dashboard page -->
                        <a href="{{ url_for('profile') }}">Go to Profile</a>
                    </body>
                </html>
            """, username=username)
        else:
            return "Invalid authentication code."
    else:
        return "Authentication code expired or invalid."



if __name__ == '__main__':
    app.run(debug=True)

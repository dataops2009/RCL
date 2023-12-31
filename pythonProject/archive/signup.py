from flask import Flask, request, render_template_string, session
import pymssql
from mailjet_rest import Client
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# Secret key for session management
app.secret_key = '0123456789abcdef0123456789abcdef'  # Replace with a securely generated key

# Mailjet setup
api_key = '0f502cb98eda788b78d88b0d79feae51'
api_secret = '690bd92e04f6e062c52d10afa0966c3f'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

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

# Simulated database for storing auth codes and timestamps
auth_codes = {}

@app.route('/', methods=['GET'])
def form():
    return render_template_string("""
        <html>
            <body>
                <form action="/submit" method="post">
                    Username: <input type="text" name="username"><br>
                    Email: <input type="text" name="email"><br>
                    Password: <input type="password" name="password"><br>
                    Confirm Password: <input type="password" name="confirm_password"><br>
                    <input type="submit" value="Submit">
                </form>
            </body>
        </html>
    """)

@app.route('/submit', methods=['POST'])
def submit():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        return "Passwords do not match. Please go back and try again."

    conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO UserRegistration (Username, Email, Password) VALUES (%s, %s, %s)", (username, email, password))
    cursor.execute("INSERT INTO Players_Dim (ID, Name) VALUES (%s,%s)", (12345, username))

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
            return render_template_string("""
                <html>
                    <body>
                        <h1>Verification successful!</h1>
                        <p>Welcome, {{ username }}. You are now logged in.</p>
                    </body>
                </html>
            """, username=username)
        else:
            return "Invalid authentication code."
    else:
        return "Authentication code expired or invalid."

if __name__ == '__main__':
    app.run(debug=True)

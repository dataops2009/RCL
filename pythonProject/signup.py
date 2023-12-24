from flask import Flask, request, render_template_string
import pymssql

app = Flask(__name__)

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

    # Check if the two passwords match
    if password != confirm_password:
        return "Passwords do not match. Please go back and try again."

    conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
    cursor = conn.cursor()
    
    # Insert data into UserRegistration
    cursor.execute("INSERT INTO UserRegistration (Username, Email, Password) VALUES (%s, %s, %s)", (username, email, password))
    
    # Insert the username into the Players_Dim table
    cursor.execute("INSERT INTO Players_Dim (ID, Name) VALUES (%s,%s)", (12345, username))

    conn.commit()
    cursor.close()
    conn.close()

    return render_template_string("""
        <html>
            <body>
                <h1>Registration successful!</h1>
                <p>Thank you, {{ username }}, for registering.</p>
            </body>
        </html>
    """, username=username)

if __name__ == '__main__':
    app.run(debug=True)

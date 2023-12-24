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
                    <input type="submit" value="Submit">
                </form>
            </body>
        </html>
    """)

@app.route('/submit', methods=['POST'])
def submit():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']  # Remember to hash passwords in a real application

    conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO UserRegistration (Username, Email, Password) VALUES (%s, %s, %s)", (username, email, password))
    conn.commit()
    cursor.close()
    conn.close()

    return 'Registration successful!'

if __name__ == '__main__':
    app.run(debug=True)

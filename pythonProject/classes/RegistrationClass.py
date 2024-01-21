import pymssql
from werkzeug.security import generate_password_hash
import random
from datetime import datetime

class SignUpManager:
    def __init__(self):
        self.conn = pymssql.connect('rcldevelopmentserver.database.windows.net', 'rcldeveloper', 'media$2009', 'rcldevelopmentdatabase')

    def email_exists(self, email):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT * FROM UserRegistration WHERE Email = %s", (email,))
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error in email_exists: {e}")
            return False  # or handle the error as appropriate

    def username_exists(self, username):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT * FROM UserRegistration WHERE Username = %s", (username,))
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error in username_exists: {e}")
            return False  # or handle the error as appropriate
            
    def register_user(self, username, email, password):
        try:
            if self.email_exists(email):
                return {"status": "error", "message": "Email already registered"}
            if self.username_exists(username):
                return {"status": "error", "message": "Username already taken"}

            with self.conn.cursor() as cursor:
                # Retrieve the maximum ID_Var
                cursor.execute("SELECT MAX(ID_Var) FROM Players_Dim")
                last_id_row = cursor.fetchone()
                
                # Increment the ID
                if last_id_row and last_id_row[0]:
                    last_id_num = int(last_id_row[0].split('-')[1])
                    new_id = f"PL-{last_id_num + 1}"
                else:
                    new_id = "PL-1000"  # Default ID if no IDs are present in the table

                # Hash the password
                hashed_password = generate_password_hash(password)

                # Insert user
                cursor.execute("INSERT INTO UserRegistration (ID_Var , Username, Email, Password) VALUES (%s, %s, %s, %s)", (new_id, username, email, hashed_password))
                cursor.execute("INSERT INTO Players_Dim (ID_Var, Name) VALUES (%s, %s)", (new_id, username))

                self.conn.commit()

            return {"status": "success", "username": username, "new_id": new_id}
        except Exception as e:
            print(f"Error in register_user: {e}")
            return {"status": "error", "message": "An error occurred during registration"}

    def generate_auth_code(self, username):
        auth_code = str(random.randint(100000, 999999))
        timestamp = datetime.now()
        return {"auth_code": auth_code, "timestamp": timestamp}

    def close_connection(self):
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                print(f"Error closing connection: {e}")

# REMOVED: from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

# ADDED: Import the globally shared MySQL object
from database_connection import mysql


class User:
    def __init__(self, user_id, user_type, name, email=None):
        self.id = f"{user_type}_{user_id}" # Flask-Login expects a string ID
        self.user_type = user_type
        self.name = name
        self.email = email
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return self.id

    @staticmethod
    def get(user_id_full):
        if not user_id_full:
            return None
        
        try:
            user_type, uid_str = user_id_full.split('_')
            # Assuming DB ID is INT
            uid = int(uid_str) 
        except ValueError:
            return None # Malformed ID

        # CHANGED: Access the shared MySQL object directly
        # This works because Flask-Login calls this within an application context
        cur = mysql.connection.cursor(None) 
        
        user_data = None
        
        if user_type == 'student':
            cur.execute("SELECT Student_ID, FirstName, LastName, Email FROM student WHERE Student_ID = %s", (uid,))
            user_data = cur.fetchone()
            if user_data:
                return User(user_data['Student_ID'], 'student', 
                            f"{user_data['FirstName']} {user_data['LastName']}", 
                            user_data['Email'])
        elif user_type == 'admin':
            cur.execute("SELECT Staff_ID, Name FROM warden WHERE Staff_ID = %s", (uid,))
            user_data = cur.fetchone()
            if user_data:
                return User(user_data['Staff_ID'], 'admin', user_data['Name'])
        
        cur.close()
        return None
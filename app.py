from flask import Flask, render_template, redirect, url_for, flash, session
# Remove the unused Flask-MySQLdb import here (it's in database_connection.py)
from flask_login import LoginManager, login_required, current_user
from config import Config
import os
# 1. IMPORT the globally shared MySQL object
from database_connection import mysql


app = Flask(__name__)
app.config.from_object(Config)

# 2. INITIALIZE MySQL using the shared object's init_app method
# This registers the instance for use in your routes and models.
mysql.init_app(app) 

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Import routes
from routes import auth, student, admin, room, mess, fees, visitor

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(student.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(room.bp)
app.register_blueprint(mess.bp)
app.register_blueprint(fees.bp)
app.register_blueprint(visitor.bp)

@login_manager.user_loader
def load_user(user_id):
    # This correctly imports User from models.database, which now uses the shared 'mysql'
    from models.database import User
    return User.get(user_id)

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('user_type') == 'student':
            return redirect(url_for('student.dashboard'))
        elif session.get('user_type') == 'admin':
            return redirect(url_for('admin.dashboard'))
    return redirect(url_for('auth.login'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
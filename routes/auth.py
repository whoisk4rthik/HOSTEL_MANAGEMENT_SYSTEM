from flask import Blueprint, render_template, request, redirect, url_for, flash, session
# REMOVED: from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash
from flask import current_app

# ADDED: Import the globally shared MySQL object
from database_connection import mysql

bp = Blueprint('auth', __name__, url_prefix='/auth') 

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        
        # CHANGED: Accessing the shared MySQL object directly
        cur = mysql.connection.cursor()
        
        if user_type == 'student':
            cur.execute("SELECT Student_ID, FirstName, LastName, Email FROM student WHERE Student_ID = %s", (user_id,))
            user = cur.fetchone()
            
            if user:
                # Simple password check (Student_ID as password for demo)
                if password == str(user['Student_ID']):
                    session['user_id'] = user['Student_ID']
                    session['user_type'] = 'student'
                    session['user_name'] = f"{user['FirstName']} {user['LastName']}"
                    flash('Login successful!', 'success')
                    return redirect(url_for('student.dashboard')) 
                else:
                    flash('Invalid credentials', 'danger')
            else:
                flash('Student not found', 'danger')
                
        elif user_type == 'admin':
            cur.execute("SELECT Staff_ID, Name FROM warden WHERE Staff_ID = %s", (user_id,))
            user = cur.fetchone()
            
            if user:
                # Simple password check (Staff_ID as password for demo)
                if password == str(user['Staff_ID']):
                    session['user_id'] = user['Staff_ID']
                    session['user_type'] = 'admin'
                    session['user_name'] = user['Name']
                    flash('Login successful!', 'success')
                    return redirect(url_for('admin.dashboard'))
                else:
                    flash('Invalid credentials', 'danger')
            else:
                flash('Admin not found', 'danger')
        
        cur.close()
    
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))
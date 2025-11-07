from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask import current_app
from datetime import datetime
from database_connection import mysql # ADDED: Import the globally shared MySQL object

bp = Blueprint('student', __name__, url_prefix='/student')

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'student':
            flash('Please login as student', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
def dashboard():
    # CHANGED: Use the imported 'mysql' object directly
    cur = mysql.connection.cursor()
    student_id = session['user_id']
    
    # Get student details
    cur.execute("""
        SELECT s.*, r.Room_no, m.Name as MessName, m.Fees as MessFees
        FROM student s
        LEFT JOIN room r ON s.Room_ID = r.Room_ID
        LEFT JOIN mess m ON s.Mess_ID = m.Mess_ID
        WHERE s.Student_ID = %s
    """, (student_id,))
    student = cur.fetchone()
    
    # Get pending fees
    cur.execute("SELECT CalculatePendingFees(%s) as pending", (student_id,))
    pending = cur.fetchone()
    
    # Get recent payments
    cur.execute("""
        SELECT * FROM fees 
        WHERE Student_ID = %s 
        ORDER BY PaymentDate DESC LIMIT 5
    """, (student_id,))
    payments = cur.fetchall()
    
    cur.close()
    
    return render_template('student/dashboard.html', 
                           student=student, 
                           pending=pending['pending'] or 0,
                           payments=payments)

@bp.route('/profile')
@login_required
def profile():
    # CHANGED: Use the imported 'mysql' object directly
    cur = mysql.connection.cursor()
    student_id = session['user_id']
    
    cur.execute("""
        SELECT s.*, r.Room_no, m.Name as MessName
        FROM student s
        LEFT JOIN room r ON s.Room_ID = r.Room_ID
        LEFT JOIN mess m ON s.Mess_ID = m.Mess_ID
        WHERE s.Student_ID = %s
    """, (student_id,))
    student = cur.fetchone()
    
    # Get phone numbers
    cur.execute("SELECT Ph_no FROM studentphone WHERE Student_ID = %s", (student_id,))
    phones = cur.fetchall()
    
    cur.close()
    
    return render_template('student/profile.html', student=student, phones=phones)

@bp.route('/room')
@login_required
def room():
    # CHANGED: Use the imported 'mysql' object directly
    cur = mysql.connection.cursor()
    student_id = session['user_id']
    
    # Get current room details
    cur.execute("""
        SELECT r.*, w.Name as WardenName, w.Ph_no as WardenPhone
        FROM student s
        JOIN room r ON s.Room_ID = r.Room_ID
        JOIN warden w ON r.Staff_ID = w.Staff_ID
        WHERE s.Student_ID = %s
    """, (student_id,))
    room = cur.fetchone()
    
    room_id = room['Room_ID'] if room else 0
    
    # Get roommates
    cur.execute("""
        SELECT Student_ID, FirstName, LastName, Department
        FROM student
        WHERE Room_ID = %s AND Student_ID != %s
    """, (room_id, student_id))
    roommates = cur.fetchall()
    
    # Get allocation history
    cur.execute("""
        SELECT ra.*, r.Room_no
        FROM roomallocation ra
        JOIN room r ON ra.Room_ID = r.Room_ID
        WHERE ra.Student_ID = %s
        ORDER BY ra.AllocationDate DESC
    """, (student_id,))
    history = cur.fetchall()
    
    cur.close()
    
    return render_template('student/room.html', room=room, roommates=roommates, history=history)

@bp.route('/mess', methods=['GET', 'POST'])
@login_required
def mess():
    # CHANGED: Use the imported 'mysql' object directly
    cur = mysql.connection.cursor()
    student_id = session['user_id']
    
    if request.method == 'POST':
        new_mess_id = request.form.get('mess_id')
        
        cur.execute("UPDATE student SET Mess_ID = %s WHERE Student_ID = %s", 
                    (new_mess_id, student_id))
        mysql.connection.commit()
        flash('Mess updated successfully!', 'success')
        return redirect(url_for('student.mess'))
    
    # Get all mess options
    cur.execute("SELECT * FROM mess")
    all_mess = cur.fetchall()
    
    # Get current mess
    cur.execute("""
        SELECT m.* FROM mess m
        JOIN student s ON s.Mess_ID = m.Mess_ID
        WHERE s.Student_ID = %s
    """, (student_id,))
    current_mess = cur.fetchone()
    
    cur.close()
    
    return render_template('student/mess.html', all_mess=all_mess, current_mess=current_mess)

@bp.route('/fees', methods=['GET', 'POST'])
@login_required
def fees():
    # CHANGED: Use the imported 'mysql' object directly
    cur = mysql.connection.cursor()
    student_id = session['user_id']
    
    if request.method == 'POST':
        amount = request.form.get('amount')
        fee_type = request.form.get('type')
        
        cur.execute("""
            INSERT INTO fees (Status, FeesAmount, PaymentDate, Type, Student_ID)
            VALUES ('Paid', %s, %s, %s, %s)
        """, (amount, datetime.now().date(), fee_type, student_id))
        mysql.connection.commit()
        flash('Payment recorded successfully!', 'success')
        return redirect(url_for('student.fees'))
    
    # Get all fees
    cur.execute("""
        SELECT * FROM fees 
        WHERE Student_ID = %s 
        ORDER BY PaymentDate DESC
    """, (student_id,))
    all_fees = cur.fetchall()
    
    # Get pending fees
    cur.execute("SELECT CalculatePendingFees(%s) as pending", (student_id,))
    pending = cur.fetchone()
    
    cur.close()
    
    return render_template('student/fees.html', all_fees=all_fees, pending=pending['pending'] or 0)

@bp.route('/visitors', methods=['GET', 'POST'])
@login_required
def visitors():
    # CHANGED: Use the imported 'mysql' object directly
    cur = mysql.connection.cursor()
    student_id = session['user_id']
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        relation = request.form.get('relation')
        visit_date = request.form.get('visit_date')
        out_date = request.form.get('out_date')
        
        try:
            # Insert visitor
            cur.execute("""
                INSERT INTO visitor (Visitor_Name, Ph_no, Relation_to_student, VisitDate, OutDate)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                Relation_to_student = %s, VisitDate = %s, OutDate = %s
            """, (name, phone, relation, visit_date, out_date, relation, visit_date, out_date))
            
            # Link to student
            cur.execute("""
                INSERT IGNORE INTO visitedby (Visitor_Name, Student_ID)
                VALUES (%s, %s)
            """, (name, student_id))
            
            mysql.connection.commit()
            flash('Visitor registered successfully!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error: {str(e)}', 'danger')
        
        return redirect(url_for('student.visitors'))
    
    # Get visitor history
    cur.execute("""
        SELECT v.* FROM visitor v
        JOIN visitedby vb ON v.Visitor_Name = vb.Visitor_Name
        WHERE vb.Student_ID = %s
        ORDER BY v.VisitDate DESC
    """, (student_id,))
    visitors = cur.fetchall()
    
    cur.close()
    
    return render_template('student/visitors.html', visitors=visitors)
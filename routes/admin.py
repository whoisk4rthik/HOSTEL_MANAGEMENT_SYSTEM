from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask import current_app
from database_connection import mysql
from datetime import date
import MySQLdb

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'admin':
            flash('Admin access required', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@admin_required
def dashboard():
    cur = mysql.connection.cursor()
    
    # Get statistics
    cur.execute("SELECT COUNT(*) as total FROM student")
    total_students = cur.fetchone()['total']
    
    cur.execute("SELECT COUNT(*) as total FROM room WHERE Status = 'Occupied'")
    occupied_rooms = cur.fetchone()['total']
    
    cur.execute("SELECT COUNT(*) as total FROM room")
    total_rooms = cur.fetchone()['total']
    
    cur.execute("SELECT SUM(FeesAmount) as total FROM fees WHERE Status IN ('Pending', 'Overdue')")
    pending_fees = cur.fetchone()['total'] or 0
    
    # Get ALL students with their details including pending fees
    cur.execute("""
        SELECT s.Student_ID, s.FirstName, s.LastName, s.Department, s.Sex, s.Email,
               s.Room_ID, r.Room_no, s.Mess_ID, m.Name as MessName,
               COALESCE(
                   (SELECT SUM(f.FeesAmount) 
                    FROM fees f 
                    WHERE f.Student_ID = s.Student_ID 
                    AND f.Status IN ('Pending', 'Overdue')), 
                   0
               ) as PendingFees
        FROM student s
        LEFT JOIN room r ON s.Room_ID = r.Room_ID
        LEFT JOIN mess m ON s.Mess_ID = m.Mess_ID
        ORDER BY s.Student_ID DESC
    """)
    all_students = cur.fetchall()
    
    # Get ALL rooms for allocation dropdown
    cur.execute("""
        SELECT Room_ID, Room_no, Capacity, Status,
               (SELECT COUNT(*) FROM roomallocation ra 
                WHERE ra.Room_ID = r.Room_ID AND ra.VacateDate IS NULL) as CurrentOccupancy
        FROM room r
        ORDER BY Room_no
    """)
    available_rooms = cur.fetchall()
    
    # Get available mess options
    cur.execute("SELECT Mess_ID, Name, Type, Fees FROM mess ORDER BY Name")
    available_mess = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/dashboard.html',
                           total_students=total_students,
                           occupied_rooms=occupied_rooms,
                           total_rooms=total_rooms,
                           pending_fees=pending_fees,
                           all_students=all_students,
                           available_rooms=available_rooms,
                           available_mess=available_mess)

@bp.route('/add_student', methods=['POST'])
@admin_required
def add_student():
    cur = mysql.connection.cursor()
    
    try:
        student_id = request.form.get('student_id')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        department = request.form.get('department')
        sex = request.form.get('sex')
        email = request.form.get('email')
        phone = request.form.get('phone')
        mess_id = request.form.get('mess_id')
        
        # Insert student without room initially
        cur.execute("""
            INSERT INTO student (Student_ID, FirstName, LastName, Department, Sex, Email, Mess_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (student_id, first_name, last_name, department, sex, email, mess_id))
        
        # Add phone number if provided
        if phone:
            cur.execute("""
                INSERT INTO studentphone (Ph_no, Student_ID)
                VALUES (%s, %s)
            """, (phone, student_id))
        
        mysql.connection.commit()
        flash(f'✅ Student {first_name} {last_name} added successfully! You can now allocate a room.', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'❌ Error adding student: {str(e)}', 'danger')
    finally:
        cur.close()
    
    return redirect(url_for('admin.dashboard'))

@bp.route('/delete_student/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    cur = mysql.connection.cursor()
    
    try:
        # Delete in correct order to respect foreign key constraints
        cur.execute("DELETE FROM visitedby WHERE Student_ID = %s", (student_id,))
        cur.execute("DELETE FROM studentphone WHERE Student_ID = %s", (student_id,))
        cur.execute("DELETE FROM roomallocation WHERE Student_ID = %s", (student_id,))
        cur.execute("DELETE FROM fees WHERE Student_ID = %s", (student_id,))
        cur.execute("DELETE FROM student WHERE Student_ID = %s", (student_id,))
        
        mysql.connection.commit()
        flash(f'✅ Student ID {student_id} deleted successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'❌ Error deleting student: {str(e)}', 'danger')
    finally:
        cur.close()
    
    return redirect(url_for('admin.dashboard'))

@bp.route('/allocate_room/<int:student_id>', methods=['POST'])
@admin_required
def allocate_room(student_id):
    cur = mysql.connection.cursor()
    
    room_id = request.form.get('room_id')
    allocation_date = request.form.get('allocation_date') or date.today()
    
    try:
        # Call the stored procedure that handles room allocation
        cur.callproc('HandleRoomAllocation', (student_id, room_id, allocation_date))
        mysql.connection.commit()
        flash(f'✅ SUCCESS: Room allocation completed for Student ID {student_id}!', 'success')
    except MySQLdb.Error as e:
        mysql.connection.rollback()
        error_code = e.args[0] if e.args else None
        error_msg = e.args[1] if len(e.args) > 1 else str(e)
        
        # Check if it's the trigger error (error code 1644)
        if error_code == 1644:
            if 'capacity reached' in str(error_msg).lower():
                flash('🚫 DATABASE TRIGGER FIRED! Room is at full capacity. Cannot allocate more students to this room. Please select a different room.', 'danger')
            elif 'room does not exist' in str(error_msg).lower():
                flash('🚫 DATABASE TRIGGER FIRED! The selected room does not exist in the database.', 'danger')
            else:
                flash(f'🚫 DATABASE TRIGGER FIRED! {error_msg}', 'danger')
        else:
            flash(f'❌ Database Error: {error_msg} (Error Code: {error_code})', 'danger')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'❌ Unexpected Error: {str(e)}', 'danger')
    finally:
        cur.close()
    
    return redirect(url_for('admin.dashboard'))

@bp.route('/students')
@admin_required
def students():
    cur = mysql.connection.cursor()
    
    search = request.args.get('search', '')
    
    if search:
        cur.execute("""
            SELECT s.*, r.Room_no, m.Name as MessName
            FROM student s
            LEFT JOIN room r ON s.Room_ID = r.Room_ID
            LEFT JOIN mess m ON s.Mess_ID = m.Mess_ID
            WHERE s.FirstName LIKE %s OR s.LastName LIKE %s OR s.Department LIKE %s
        """, (f'%{search}%', f'%{search}%', f'%{search}%'))
    else:
        cur.execute("""
            SELECT s.*, r.Room_no, m.Name as MessName
            FROM student s
            LEFT JOIN room r ON s.Room_ID = r.Room_ID
            LEFT JOIN mess m ON s.Mess_ID = m.Mess_ID
        """)
    
    students = cur.fetchall()
    cur.close()
    
    return render_template('admin/students.html', students=students)

@bp.route('/rooms')
@admin_required
def rooms():
    cur = mysql.connection.cursor()
    
    cur.execute("""
        SELECT r.*, w.Name as WardenName,
                (SELECT COUNT(*) FROM roomallocation ra 
                WHERE ra.Room_ID = r.Room_ID AND ra.VacateDate IS NULL) as CurrentOccupancy
        FROM room r
        JOIN warden w ON r.Staff_ID = w.Staff_ID
    """)
    rooms = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/rooms.html', rooms=rooms)

@bp.route('/mess')
@admin_required
def mess():
    cur = mysql.connection.cursor()
    
    cur.execute("""
        SELECT m.*, w.Name as WardenName,
                (SELECT COUNT(*) FROM student s WHERE s.Mess_ID = m.Mess_ID) as CurrentStudents
        FROM mess m
        JOIN warden w ON m.Staff_ID = w.Staff_ID
    """)
    mess_list = cur.fetchall()
    
    cur.close()
    
    return render_template('admin/mess.html', mess_list=mess_list)

@bp.route('/fees')
@admin_required
def fees():
    cur = mysql.connection.cursor()
    
    status_filter = request.args.get('status', 'all')
    
    query = """
        SELECT f.*, s.FirstName, s.LastName, s.Student_ID
        FROM fees f
        JOIN student s ON f.Student_ID = s.Student_ID
    """
    params = []
    if status_filter != 'all':
        query += " WHERE f.Status = %s"
        params.append(status_filter)
    
    query += " ORDER BY f.PaymentDate DESC"
    
    cur.execute(query, tuple(params))
    
    fees = cur.fetchall()
    cur.close()
    
    return render_template('admin/fees.html', fees=fees, status_filter=status_filter)
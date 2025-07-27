from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mail import Mail, Message
import pyttsx3
import datetime
import sqlite3
import random
import os
from mgit_assistant import handle_student_query
from mgit_assistant import take_command_mgit
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText


app = Flask(__name__)
app.secret_key = "your_secret_key"

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'asmartcampus@gmail.com'
app.config['MAIL_PASSWORD'] = 'wpef rwua euqn abrp'
app.config['MAIL_DEFAULT_SENDER'] = 'asmartcampus@gmail.com'

mail = Mail(app)

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        college TEXT
    );
    CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password TEXT,
    college TEXT DEFAULT 'MGIT'
);
    
    CREATE TABLE IF NOT EXISTS timetables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        branch TEXT NOT NULL,
        section TEXT NOT NULL,
        year TEXT NOT NULL,
        file_path TEXT NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
CREATE TABLE IF NOT EXISTS query_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_email TEXT,
    query TEXT,
    response TEXT DEFAULT 'Pending',
    status TEXT DEFAULT 'Pending',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS email_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient TEXT,
    message TEXT,
    timestamp TEXT
);





    ''')
    
     # Seed default admin (if necessary)
    cursor.execute("SELECT * FROM admin_users WHERE username = ?", ("adminmgit",))
    if not cursor.fetchone():
        hashed_password = ("Admin@123")
        cursor.execute("INSERT INTO admin_users (username, email, password, college) VALUES (?, ?, ?, ?)",
                       ("adminmgit", "admin@mgit.com", hashed_password, "MGIT"))
        conn.commit()
    

    # Seed default users (if necessary)
    cursor.execute("SELECT * FROM users WHERE email=?", ("hai123@gmail.com",))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, email, password, college) VALUES (?, ?, ?, ?)",
                       ("vishnu", "hai123@gmail.com", "7894", "MGIT"))
        cursor.execute("INSERT INTO users (username, email, password, college) VALUES (?, ?, ?, ?)",
                       ("ramu", "vishnurupi1234@gmail.com", "Vishnu@123", "MGIT"))
        conn.commit()
        
        # Seed sample query logs (if none exist)
    cursor.execute("SELECT * FROM query_logs")
    if not cursor.fetchone():
        sample_logs = [
            ("What is the MGIT college fest?", "MGIT organizes Nirvana, a popular annual fest!", "2025-04-18 09:30:00"),
            ("Where can I find the CSE 2nd Year timetable?", "You can download it from the Timetables section on the dashboard.", "2025-04-18 10:15:00"),
            ("Who is the principal of MGIT?", "The principal of MGIT is Dr. A. Ravi Kumar.", "2025-04-18 11:00:00"),
            ("When are the semester exams scheduled?", "Semester exams are scheduled for May 2025.", "2025-04-18 11:30:00"),
        ]

        cursor.executemany("INSERT INTO query_logs (query, response, timestamp) VALUES (?, ?, ?)", sample_logs)
        conn.commit()

   

    conn.close()

init_db()

# Voice Assistant
def speak(audio):
    engine = pyttsx3.init()
    engine.say(audio)
    engine.runAndWait()

def wish_me():
    hour = int(datetime.datetime.now().hour)
    if hour < 12:
        return "Good Morning!"
    elif hour < 18:
        return "Good Afternoon!"
    else:
        return "Good Evening!"

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        greeting = wish_me()
        return render_template('dashboard.html', greeting=greeting)
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/cbitabout')
def cbitabout():
    return render_template('cbitabout.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/mgit')
def mgit_page():
    if 'username' in session:
        return render_template('mgit.html', username=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/cbit')
def cbit_page():
    if 'username' in session:
        return render_template('cbit.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/other')
def other_college_page():
    if 'username' in session:
        return f"<h2>Welcome, {session['username']}! Your college is not listed.</h2><a href='/logout'>Logout</a>"
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = 'is_admin' in request.form

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        if is_admin:
            # Check admin login
            cursor.execute("SELECT username, password, college FROM admin_users WHERE username = ?", (username,))
            admin = cursor.fetchone()

            if admin and admin[1]==password:
                session['admin_email'] = admin[0]
                session['college_name'] = admin[2]
                flash('Admin logged in successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials', 'danger')
        else:
            # Check user login
            cursor.execute("SELECT username, password, college FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user and user[1]==password:
                session['username'] = user[0]
                session['college'] = user[2]
                if user[2] == "MGIT":
                    return redirect(url_for('mgit_page'))
                else:
                    flash('Access denied: Only MGIT students can log in here.', 'danger')
            else:
                flash('Invalid username or password!', 'danger')
        conn.close()
    return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        college = request.form['college']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password, college) VALUES (?, ?, ?, ?)", 
                           (username, email, password, college))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username or Email already taken. Try a different one."
        finally:
            conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/contact')
def contact():
    return render_template('contact.html')







#Admin starts here
#
#
#Admin upload timetables

@app.route('/admin/upload-timetable', methods=['GET', 'POST'])
def upload_timetable():
    message = None  # ✅ Always define it at the start

    if request.method == 'POST':
        file = request.files['file']
        branch = request.form['branch']
        section = request.form['section']
        year = request.form['year']

        if file:
            filename = secure_filename(file.filename)
            file_path = filename
            file.save(os.path.join('static/pdfs', filename))

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect('users.db')
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO timetables (branch, section, year, file_path, uploaded_at)
                VALUES (?, ?, ?, ?, ?)
            """, (branch, section, year, file_path, now))
            conn.commit()
            conn.close()

            message = "✅ Timetable uploaded successfully!"

    return render_template('upload_timetable.html', message=message)

#Admin can view time tables

@app.route('/admin/view-timetables')
def view_timetables():
    if 'admin_email' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT branch, section, year, uploaded_at, file_path FROM timetables")
    timetables = cursor.fetchall()
    conn.close()

    return render_template('view_timetables.html', files=timetables)


#Admin can add theadmins

@app.route('/admin/add-admin', methods=['GET', 'POST'])
def add_admin():
    if 'admin_email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        college_name = request.form['college']

        hashed_password = password  # you can hash this later

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO admin_users (username, email, password, college) VALUES (?, ?, ?, ?)", 
                           (username, email, hashed_password, college_name))
            conn.commit()
            conn.close()
            flash('New admin added successfully!', 'success')
            return render_template('add_admin.html')  # stay on same page after adding

        except sqlite3.IntegrityError:
            flash('Admin username or email already exists.', 'error')
            conn.close()
            return render_template('add_admin.html')

    return render_template('add_admin.html')



#Admin can view the admins

@app.route('/admin/view-admins')
def view_admins():
    if 'admin_email' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, password FROM admin_users")
    admins = cursor.fetchall()
    conn.close()

    return render_template('view_admins.html', admins=admins)



#Admin can edit the admin


@app.route('/admin/edit-admin/<int:admin_id>', methods=['GET', 'POST'])
def edit_admin(admin_id):
    if 'admin_email' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        college_name = request.form['college']

        hashed_password = password  # you can hash this later

        try:
            cursor.execute("UPDATE admin_users SET username = ?, email = ?, password = ?, college = ? WHERE id = ?",
                           (username, email, hashed_password, college_name, admin_id))
            conn.commit()
            conn.close()
            flash('Admin details updated successfully!', 'success')
            return redirect(url_for('view_admins'))  # Redirect to view admins page after edit
        except sqlite3.IntegrityError:
            flash('Error updating admin details. Please try again.', 'error')
            conn.close()
            return redirect(url_for('view_admins'))

    # Fetch admin details to pre-populate the form
    cursor.execute("SELECT username, email, password, college FROM admin_users WHERE id = ?", (admin_id,))
    admin = cursor.fetchone()
    conn.close()

    if admin:
        return render_template('edit_admin.html', admin=admin)
    else:
        flash('Admin not found.', 'error')
        return redirect(url_for('view_admins'))




@app.route('/admin/delete-admin/<int:admin_id>', methods=['GET', 'POST'])
def delete_admin(admin_id):
    if 'admin_email' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM admin_users WHERE id = ?", (admin_id,))
    conn.commit()
    conn.close()

    flash('Admin deleted successfully!', 'success')
    return redirect(url_for('view_admins'))  # Redirect back to the admin list


#queriess


@app.route('/admin/view-queries', methods=['GET', 'POST'])
def view_queries():
    if 'admin_email' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    if request.method == 'POST':
        new_query = request.form['new_query']
        new_response = request.form['new_response']
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute("INSERT INTO query_logs (query, response, timestamp) VALUES (?, ?, ?)",
                  (new_query, new_response, timestamp))
        conn.commit()

    # Fetch query_text, response, timestamp from query_logs
    c.execute("SELECT id, query, response, timestamp FROM query_logs")
    logs = c.fetchall()
    conn.close()

    return render_template('view_queries.html', logs=logs)





@app.route('/admin/edit_query/<int:id>', methods=['GET', 'POST'])
def edit_query(id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    if request.method == 'POST':
        new_query = request.form['query']
        new_response = request.form['response']

        c.execute("UPDATE query_logs SET query = ?, response = ? WHERE id = ?", (new_query, new_response, id))
        conn.commit()
        conn.close()
        flash('Query and response updated successfully!', 'success')
        return redirect(url_for('view_queries'))
    else:
        c.execute("SELECT * FROM query_logs WHERE id = ?", (id,))
        query = c.fetchone()
        conn.close()
        return render_template('edit_query.html', query=query)


@app.route('/view_query_logs')
def view_query_logs():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM query_logs")
    logs = c.fetchall()
    conn.close()
    return render_template('view_queries.html', logs=logs)



@app.route('/admin/delete_query/<int:id>', methods=['POST'])
def delete_query(id):
    if 'admin_email' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM query_logs WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash('Query deleted successfully!', 'success')
    return redirect(url_for('view_queries'))







@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_email' in session:
        return render_template('admindashboard.html', admin_email=session['admin_email'])
    else:
        return redirect(url_for('login'))







@app.route('/admin/update-college', methods=['GET', 'POST'])
def update_college():
    if 'admin_email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_college_name = request.form['college_name']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE admin_users SET college_name=? WHERE email=?", 
                       (new_college_name, session['admin_email']))
        conn.commit()
        conn.close()
        flash('College name updated successfully!', 'success')
        session['college_name'] = new_college_name
        return redirect(url_for('admin_dashboard'))

    return render_template('update_college.html')





@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_email', None)
    session.pop('college_name', None)
    return redirect(url_for('login'))






#maps


@app.route('/library_map')
def library_map_page():
    location = request.args.get('location')
    return render_template('library_map.html', location=location)
    
@app.route('/auditorium_map')
def auditorium_map_page():
    location = request.args.get('location')
    return render_template('auditorium_map.html', location=location)

    
@app.route('/canteen_map')
def canteen_map_page():
    location = request.args.get('location')
    return render_template('canteen_map.html', location=location)


@app.route('/mgit')
def mgit():
    return render_template('mgit.html')



#mgit.html

@app.route("/view_timetable", methods=["GET", "POST"])
def view_timetable():
    if request.method == "POST":
        branch = request.form["branch"].lower().strip()
        section = request.form["section"].strip()
        year = request.form["year"].strip()

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT file_path FROM timetables
            WHERE branch=? AND section=? AND year=?
            ORDER BY uploaded_at DESC
            LIMIT 1
        """, (branch, section, year))
        result = cursor.fetchone()
        conn.close()

        if result:
            file_name = result[0]  # e.g. 'cse_1_1styear_timetable'
            file_path = f"pdfs/{file_name}.pdf"
            full_static_path = os.path.join("static", file_path)

            if os.path.exists(full_static_path):
                return render_template("view_timetable.html", file_path=file_path, found=True)
            else:
                return render_template("view_timetable.html", not_found=True)

        else:
            return render_template("view_timetable.html", not_found=True)

    return render_template("view_timetable.html")






@app.route("/view_announcements", methods=["GET", "POST"])
def view_announcements():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT title, content, posted_at FROM announcements
        ORDER BY posted_at DESC
    """)
    announcements = cursor.fetchall()
    
    conn.close()
    
    return render_template("view_announcements.html", announcements=announcements)





@app.route("/academic_calendar")
def academic_calendar():
    return render_template("academic_calendar.html")

@app.route("/submit_query")
def submit_query():
    return render_template("submit_query.html")

@app.route("/exam_schedules")
def exam_schedules():
    return render_template("exam_schedules.html")

@app.route("/college_events")
def college_events():
    return render_template("college_events.html")





#admin manage users

# Manage Users Page
@app.route('/admin/manage-users')
def manage_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('admin_manage_users.html', users=users)

# Add New User
@app.route('/admin/add-user', methods=['POST'])
def add_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                   (username, email, password))
    conn.commit()
    conn.close()
    return redirect('/admin/manage-users')

# Edit User Form
@app.route('/admin/edit-user/<int:user_id>')
def edit_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return render_template('edit_user.html', user=user)

# Update User
@app.route('/admin/update-user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username=?, email=?, password=? WHERE id=?",
                   (username, email, password, user_id))
    conn.commit()
    conn.close()
    return redirect('/admin/manage-users')

# Delete User
@app.route('/admin/delete-user/<int:user_id>')
def delete_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/manage-users')




#admin_notifications.html
@app.route('/admin/notifications')
def view_notifications():
    status = request.args.get('status', 'Pending')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notifications WHERE status = ?", (status,))
    notifications = cursor.fetchall()
    return render_template('admin_notifications.html', notifications=notifications, current_status=status)


@app.route('/admin/resolve-notification/<int:notification_id>', methods=['POST'])
def resolve_notification(notification_id):
    response_text = request.form['response']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # update the notification
    cursor.execute("""
        UPDATE notifications 
        SET response = ?, status = 'Resolved'
        WHERE id = ?
    """, (response_text, notification_id))
    conn.commit()

    # Send mail to the student
    cursor.execute("SELECT student_email FROM notifications WHERE id = ?", (notification_id,))
    student_email = cursor.fetchone()[0]
    send_notification_email(student_email, response_text)
    

    return redirect('/admin/notifications')



def send_notification_email(to_email, message):
    sender_email = "youremail@gmail.com"
    sender_password = "yourpassword"

    msg = MIMEText(f"The admin has replied to your query:\n\n{message}\n\nThanks for reaching out!")
    msg['Subject'] = "MGIT Assistant - Query Update"
    msg['From'] = sender_email
    msg['To'] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)
    log_email(to_email, message)

def log_email(to_email, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO email_logs (recipient, message, timestamp) VALUES (?, ?, ?)",
                   (to_email, message, timestamp))
    conn.commit()
    conn.close()



@app.route('/my-queries')
def my_queries():
    email = session.get('email')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT query, response, status, timestamp FROM notifications WHERE student_email = ?", (email,))
    data = cursor.fetchall()
    conn.close()
    return render_template('my_queries.html', queries=data)




@app.context_processor
def inject_notification_count():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM notifications WHERE status = 'Pending'")
    count = cursor.fetchone()[0]
    conn.close()
    return dict(pending_notifications=count)





#email

# Forgot Password
def check_email_exists(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def send_otp(email):
    try:
        otp = str(random.randint(100000, 999999))
        session['otp'] = otp
        session['email'] = email

        msg = Message("Your OTP Code", recipients=[email])
        msg.body = f"Your OTP for password reset is: {otp}"
        mail.send(msg)

        print(f"OTP Sent to {email}: {otp}")
        return True
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return False

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        if not check_email_exists(email):
            flash("The email does not exist. Please try again.", "error")
            return redirect(url_for('forgot_password'))

        if send_otp(email):
            session['email'] = email
            return redirect(url_for('verify_otp'))
        else:
            flash("Failed to send OTP. Try again later.", "error")
            return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        if entered_otp == session.get('otp'):
            return redirect(url_for('reset_password'))
        else:
            return "Invalid OTP. Try again."
    return render_template('verify_otp.html')

@app.route('/resend-otp', methods=['POST'])
def resend_otp():
    email = session.get('email')
    if not email:
        return "Session expired. Please request a new OTP.", 400

    if send_otp(email):
        return "New OTP sent successfully!"
    else:
        return "Failed to send OTP. Try again later.", 500

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        email = session.get('email')

        if not email:
            return "Session expired. Please request a new OTP."

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

            if user:
                cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
                conn.commit()
                conn.close()

                session.pop('otp', None)
                session.pop('email', None)

                return redirect(url_for('login'))
            else:
                return "Email not found. Please register first."
        except Exception as e:
            return f"Error updating password: {e}"

    return render_template('reset_password.html')





@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.json.get('query')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    college = session.get('college')
    student_email = session.get('email')

    if user_query:
        if college == "MGIT":
            response = handle_student_query(student_email, user_query)

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO query_logs (query, response, timestamp, student_email) VALUES (?, ?, ?, ?)",
                           (user_query, response, timestamp, student_email))
            conn.commit()
            conn.close()

            return jsonify({'response': response})
        else:
            return jsonify({'response': "I currently don't have information for your college."})
    
    return jsonify({'response': "No query received!"})


@app.route('/voice_command/<query>')
def voice_command(query):
    if 'college' in session:
        if session['college'] == "MGIT":
            response = take_command_mgit(query.lower())
        else:
            response = "I currently don't have information for your college."
    else:
        response = "Please log in first to access voice commands."

    speak(response)
    return jsonify({'response': response})

@app.route('/test-email')
def test_email():
    try:
        msg = Message("Test Email", recipients=["your-email@gmail.com"], body="Hello, this is a test email!")
        mail.send(msg)
        return "Test email sent successfully!"
    except Exception as e:
        return f"Error: {e}"
 
 
 


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
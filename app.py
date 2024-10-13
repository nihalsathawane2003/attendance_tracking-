from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure secret key for signing cookies

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User data storage (in-memory dictionaries)
users = {}
passwords = {}

# Loading user from dictionary
@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route('/')
def home():
    return redirect(url_for('login'))  # Redirect to login page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)
        if user and check_password_hash(passwords.get(username), password):  # Check password hash
            login_user(user)
            return redirect(url_for('dashboard'))  # Redirect to dashboard after login
        else:
            error_message = "Invalid credentials"
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')  # Render login page for GET request

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['new_username']
        password = request.form['new_password']

        # Registration validation
        if len(password) < 6:
            error_message = "Password must be at least 6 characters long."
            return render_template('login.html', error_message=error_message)

        if username in users:
            error_message = "Username already exists"
            return render_template('login.html', error_message=error_message)
        else:
            new_user = UserMixin()
            new_user.id = username
            users[username] = new_user  # Store user
            passwords[username] = generate_password_hash(password)  # Hash and store password
            success_message = "User registered successfully! Please log in."
            return render_template('login.html', success_message=success_message)

@app.route('/dashboard')
@login_required
def dashboard():
    current_date = pd.Timestamp.now().strftime('%Y-%m-%d')

    # Pass data to the dashboard template
    return render_template('home.html', current_date=current_date)

@app.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    if request.method == 'POST':
        if 'reset' in request.form:  # Reset attendance if requested
            if os.path.exists('attendance.xlsx'):
                os.remove('attendance.xlsx')  # Delete the existing file
        else:
            student_name = request.form['student_name']
            
            # Read or create the attendance Excel file
            if os.path.exists('attendance.xlsx'):
                df = pd.read_excel('attendance.xlsx')
            else:
                df = pd.DataFrame(columns=["Student Name", "Status"])

            # Add new attendance record
            new_entry = pd.DataFrame({"Student Name": [student_name], "Status": ["Present"]})
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_excel('attendance.xlsx', index=False)

        return redirect(url_for('attendance'))

    # Read attendance data to display
    if os.path.exists('attendance.xlsx'):
        df = pd.read_excel('attendance.xlsx')
    else:
        df = pd.DataFrame(columns=["Student Name", "Status"])

    return render_template('attendance.html', attendance_data=df.to_html(classes='data'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

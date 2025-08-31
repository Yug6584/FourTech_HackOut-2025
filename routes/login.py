from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from __init__ import mysql
import re

login_bp = Blueprint(
    'login_bp',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

@login_bp.route('/', methods=['GET', 'POST'])
def login():
    # If the user is already logged in, redirect them to the home page
    if session.get('logged_in'):
        return redirect(url_for('index_bp.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Input validation to ensure email and password are provided
        if not all([email, password]):
            flash('Email and password are required.', 'danger')
            return render_template('login.html')

        # Validate the email format with a regular expression
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            flash('Invalid email format.', 'danger')
            return render_template('login.html')

        cur = mysql.connection.cursor()
        # Find the user by email, ensuring they used manual registration
        cur.execute("SELECT * FROM users WHERE email=%s AND auth_provider='manual'", (email,))
        user = cur.fetchone()
        cur.close()

        # If no user is found with a manual auth provider, suggest Google login
        if not user:
            flash('This email is registered with Google login or does not exist. Please use Google to log in.', 'danger')
            return render_template('login.html')

        # Verify the password hash from the database
        if user and check_password_hash(user[3], password):  # password_hash is the 4th column
            # Set session variables for successful login
            session['logged_in'] = True
            session['user_id'] = user[0]
            session['user_name'] = user[1]  # username
            session['user_email'] = user[2]  # email
            session['user_picture'] = '/static/default-user.png'  # Assign a default picture for manual logins
            session.permanent = True  # Make the session persistent
            
            flash('Login successful!', 'success')
            return redirect(url_for('index_bp.index'))
        else:
            # Handle invalid password case
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')
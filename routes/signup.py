from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from __init__ import mysql
import re

signup_bp = Blueprint(
    'signup_bp',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

@signup_bp.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Input validation
        if not all([username, email, password]):
            flash('All fields are required.', 'danger')
            return render_template('signup.html')

        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            flash('Invalid email format.', 'danger')
            return render_template('signup.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('signup.html')

        # Check if email or username already exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s OR username=%s", (email, username))
        existing_user = cur.fetchone()
        if existing_user:
            flash('Email or username already exists.', 'danger')
            cur.close()
            return render_template('login.html')

        # Hash the password
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            cur.execute(
                "INSERT INTO users (username, email, password_hash, auth_provider) VALUES (%s, %s, %s, %s)",
                (username, email, password_hash, 'manual')
            )
            mysql.connection.commit()

            # Fetch the newly created user
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()
            cur.close()

            # Log in the user automatically
            session['logged_in'] = True
            session['user_id'] = user[0]
            session['user_name'] = user[1]  # username
            session['user_email'] = user[2]  # email
            session['user_picture'] = '/static/default-user.png'  # Default for manual login
            flash('Signup successful! Welcome!', 'success')
            return redirect(url_for('index_bp.index'))  # Redirect to index
        except mysql.connection.Error as e:
            flash(f'Signup failed: {str(e)}', 'danger')
            cur.close()
            return render_template('signup.html')

    return render_template('signup.html')
import os
import requests
from flask import Blueprint, request, redirect, url_for, session, flash, current_app
from dotenv import load_dotenv
from __init__ import mysql

load_dotenv()

auth_bp = Blueprint('auth_bp', __name__)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = 'http://127.0.0.1:5000/auth/google/callback'

@auth_bp.route('/google/callback')
def google_callback():
    if session.get('logged_in'):
        return redirect(url_for('index_bp.index'))  # Prevent re-authentication

    code = request.args.get('code')
    if not code:
        flash('Google authentication failed: No authorization code provided.', 'error')
        return redirect(url_for('login_bp.login'))

    try:
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code',
        }
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()
        access_token = token_json.get('access_token')

        if not access_token:
            flash('Google authentication failed: Could not retrieve access token.', 'error')
            return redirect(url_for('login_bp.login'))

        userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        userinfo_headers = {'Authorization': f'Bearer {access_token}'}
        userinfo_response = requests.get(userinfo_url, headers=userinfo_headers)
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()

        email = user_info.get('email')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if user and user[4] == 'manual':
            flash('This email is registered with manual login. Please use email and password to log in.', 'error')
            cur.close()
            return redirect(url_for('login_bp.login'))

        if not user:
            cur.execute(
                "INSERT INTO users (username, email, auth_provider) VALUES (%s, %s, %s)",
                (user_info.get('name'), email, 'google')
            )
            mysql.connection.commit()
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()

        session['logged_in'] = True
        session['user_id'] = user[0]
        session['user_name'] = user_info.get('name', 'Valued User')
        session['user_email'] = user[2]
        session['user_picture'] = user_info.get('picture', '/static/default-user.png')
        session.permanent = True  # Make session persistent
        cur.close()
        flash(f"Welcome, {session['user_name']}!", 'success')
        return redirect(url_for('index_bp.index'))

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Google login failed: {e}")
        flash(f"Google login failed: {str(e)}", 'error')
        return redirect(url_for('login_bp.login'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index_bp.index'))
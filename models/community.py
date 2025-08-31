# models/community.py
import mysql.connector
from mysql.connector import Error
import os

def get_db_connection():
    """Create and return a database connection using mysql-connector"""
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', '!S6@d1#Qe$02%vL^0r&06*a'),
            database=os.environ.get('MYSQL_DB', 'terragen'),
            autocommit=False
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def get_active_members():
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM users WHERE is_active = 1")
            result = cursor.fetchone()
            return result['count'] if result else 0
    except Error as e:
        print(f"Error getting active members: {e}")
        return 0
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_total_posts():
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM posts")
            result = cursor.fetchone()
            return result['count'] if result else 0
    except Error as e:
        print(f"Error getting total posts: {e}")
        return 0
    finally:
        if conn and conn.is_connected():
            conn.close()

# In models/community.py - update the search_communities function
def search_communities(query=None):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor(dictionary=True) as cursor:
            if query:
                cursor.execute("""
                    SELECT c.*, COUNT(uc.user_id) as member_count 
                    FROM communities c 
                    LEFT JOIN user_community uc ON c.id = uc.community_id 
                    WHERE c.name LIKE %s OR c.description LIKE %s 
                    GROUP BY c.id
                """, (f"%{query}%", f"%{query}%"))
            else:
                cursor.execute("""
                    SELECT c.*, COUNT(uc.user_id) as member_count 
                    FROM communities c 
                    LEFT JOIN user_community uc ON c.id = uc.community_id 
                    GROUP BY c.id
                """)
            return cursor.fetchall()
    except Error as e:
        print(f"Error searching communities: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()

def join_community(user_id, community_id):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT IGNORE INTO user_community (user_id, community_id) VALUES (%s, %s)",
                (user_id, community_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    except Error as e:
        print(f"Error joining community: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_joined_community(user_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT c.* FROM communities c
                JOIN user_community uc ON c.id = uc.community_id
                WHERE uc.user_id = %s
                LIMIT 1
            """, (user_id,))
            return cursor.fetchone()
    except Error as e:
        print(f"Error getting joined community: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

def create_post(user_id, community_id, content, filename=None, filepath=None):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            # Insert the post
            cursor.execute(
                "INSERT INTO posts (user_id, community_id, content) VALUES (%s, %s, %s)",
                (user_id, community_id, content)
            )
            post_id = cursor.lastrowid
            
            # Insert file if provided
            if filename and filepath:
                cursor.execute(
                    "INSERT INTO files (post_id, filename, filepath) VALUES (%s, %s, %s)",
                    (post_id, filename, filepath)
                )
            
            conn.commit()
            return True
    except Error as e:
        print(f"Error creating post: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_recent_posts(community_id=None, limit=20):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor(dictionary=True) as cursor:
            if community_id:
                cursor.execute("""
                    SELECT p.*, u.username, f.filename, f.filepath,
                           DATE_FORMAT(p.created_at, '%%Y-%%m-%%d %%H:%%i:%%s') as formatted_date
                    FROM posts p
                    JOIN users u ON p.user_id = u.id
                    LEFT JOIN files f ON p.id = f.post_id
                    WHERE p.community_id = %s
                    ORDER BY p.created_at DESC
                    LIMIT %s
                """, (community_id, limit))
            else:
                # If no community_id provided, return empty list instead of all posts
                return []
            
            posts = cursor.fetchall()
            
            # Format the dates for display
            for post in posts:
                if 'formatted_date' in post:
                    post['created_at'] = post['formatted_date']
            
            return posts
    except Error as e:
        print(f"Error getting recent posts: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()
# Additional utility functions you might need
def get_community_by_id(community_id):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM communities WHERE id = %s", (community_id,))
            return cursor.fetchone()
    except Error as e:
        print(f"Error getting community by ID: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_user_posts(user_id, limit=10):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT p.*, c.name as community_name, f.filename, f.filepath,
                       DATE_FORMAT(p.created_at, '%%Y-%%m-%%d %%H:%%i:%%s') as formatted_date
                FROM posts p
                JOIN communities c ON p.community_id = c.id
                LEFT JOIN files f ON p.id = f.post_id
                WHERE p.user_id = %s
                ORDER BY p.created_at DESC
                LIMIT %s
            """, (user_id, limit))
            
            posts = cursor.fetchall()
            
            # Format the dates for display
            for post in posts:
                if 'formatted_date' in post:
                    post['created_at'] = post['formatted_date']
            
            return posts
    except Error as e:
        print(f"Error getting user posts: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os

from models.community import (
    get_active_members, get_total_posts, search_communities,
    join_community, get_joined_community, create_post, get_recent_posts
)

# models/community.py - Add this function
def get_total_communities():
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM communities")
            result = cursor.fetchone()
            return result['count'] if result else 0
    except Error as e:
        print(f"Error getting total communities: {e}")
        return 0
    finally:
        if conn and conn.is_connected():
            conn.close()
            
community_bp = Blueprint('community_bp', __name__)

UPLOAD_FOLDER = 'static/uploads'

# If you want to show both active members and total communities
@community_bp.route('/')
def community():
    active_members = get_active_members()  # Keep this if showing both
    total_communities = get_total_communities()  # NEW
    total_posts = get_total_posts()
    query = request.args.get('q')
    communities = search_communities(query)
    
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access the community features.', 'warning')
        return render_template('community.html',
            active_members=active_members,  # Keep if showing both
            total_communities=total_communities,  # NEW
            total_posts=total_posts,
            communities=communities,
            joined_community=None,
            posts=[],
            user_logged_in=False
        )
    
    user_id = session['user_id']
    joined_community = get_joined_community(user_id)
    posts = get_recent_posts(joined_community['id']) if joined_community else []
    
    return render_template(
        'community.html',
        active_members=active_members,  # Keep if showing both
        total_communities=total_communities,  # NEW
        total_posts=total_posts,
        communities=communities,
        joined_community=joined_community,
        posts=posts,
        user_logged_in=True
    )           
# routes/community.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os

from models.community import (
    get_active_members, get_total_posts, search_communities,
    join_community, get_joined_community, create_post, get_recent_posts
)

community_bp = Blueprint('community_bp', __name__)

UPLOAD_FOLDER = 'static/uploads'

@community_bp.route('/', methods=['GET', 'POST'])
def community():
    active_members = get_active_members()
    total_posts = get_total_posts()
    query = request.args.get('q')
    communities = search_communities(query)
    user_id = session.get('user_id', 1)  # Replace with real user session
    joined_community = get_joined_community(user_id)
    posts = get_recent_posts(joined_community['id']) if joined_community else []
    return render_template(
        'community.html',
        active_members=active_members,
        total_posts=total_posts,
        communities=communities,
        joined_community=joined_community,
        posts=posts
    )

@community_bp.route('/join', methods=['POST'])  # Remove /community prefix
def join_community_route():
    user_id = session.get('user_id', 1)  # Replace with real user session
    community_id = request.form.get('community_id')
    if not community_id:
        flash('Community not specified.', 'danger')
        return redirect(url_for('community_bp.community'))  # Use blueprint name
    try:
        join_community(user_id, community_id)
        flash('You have joined the community!', 'success')
    except Exception as e:
        flash('Error joining community: ' + str(e), 'danger')
    return redirect(url_for('community_bp.community'))  # Use blueprint name

@community_bp.route('/post', methods=['POST'])  # Remove /community prefix
def create_post_route():  # Rename to avoid conflict
    user_id = session.get('user_id', 1)  # Replace with real user session
    community_id = request.form.get('community_id')
    content = request.form.get('content')
    file = request.files.get('file')
    filename = None
    filepath = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        filepath = filepath.replace('static/', '')  # For url_for('static', ...)
    create_post(user_id, community_id, content, filename, filepath)
    flash('Post created!', 'success')
    return redirect(url_for('community_bp.community'))  # Use blueprint name
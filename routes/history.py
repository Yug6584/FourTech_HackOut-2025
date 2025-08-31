# routes/history.py
from flask import Blueprint, render_template, request, jsonify
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.database_utils import DatabaseManager

history_bp = Blueprint('history_bp', __name__)
db_manager = DatabaseManager()

@history_bp.route('/history')
def chat_history():
    """Render chat history page"""
    return render_template('history.html')

@history_bp.route('/api/sessions')
def get_sessions():
    """API endpoint to get chat sessions"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        sessions = db_manager.get_chat_sessions(limit, offset)
        return jsonify({'sessions': sessions, 'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@history_bp.route('/api/session/<int:session_id>')
def get_session_messages(session_id):
    """API endpoint to get messages for a specific session"""
    try:
        messages = db_manager.get_chat_messages(session_id)
        return jsonify({'messages': messages, 'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})
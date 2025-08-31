from flask import Blueprint, request, redirect, url_for, flash, session
from __init__ import mysql

delete_user_bp = Blueprint(
    'delete_user_bp',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

@delete_user_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('logged_in'):
        flash('You must be logged in to delete an account.', 'danger')
        return redirect(url_for('login_bp.login'))

    if session.get('user_id') != user_id:
        flash('You can only delete your own account.', 'danger')
        return redirect(url_for('index_bp.index'))

    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        mysql.connection.commit()
        cur.close()

        if session.get('user_id') == user_id:
            session.clear()
            flash('Your account has been deleted.', 'success')
        else:
            flash('User deleted successfully.', 'success')

        return redirect(url_for('index_bp.index'))
    except mysql.connection.Error as e:
        flash(f'Failed to delete user: {str(e)}', 'danger')
        return redirect(url_for('index_bp.index'))
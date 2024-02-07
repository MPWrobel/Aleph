from flask import Blueprint, g, render_template, redirect, request, session
from werkzeug.security import check_password_hash

from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
    if user_id := session.get('user_id'):
        g.user = get_db().execute(
            'SELECT * FROM Users WHERE user_id = ?', user_id
        ).fetchone()


@bp.route('/log-in', methods=('GET', 'POST'))
def log_in():
    if request.method == 'GET':
        return render_template('auth/log-in.html')

    username = request.form['username']
    password = request.form['password']

    # TODO: Add a flash message
    if not username or not password:
        return render_template('auth/log-in.html')

    db = get_db()
    user = db.users.fetchbyusername(username)

    if user is None:
        return f'User {username} does not exist'

    if not check_password_hash(user['password'], password):
        return 'Invalid password'

    session.clear()
    session['user_id'] = user['user_id']

    return f'Logged in as {username}', {'HX-Redirect': request.args.get('redirect')}

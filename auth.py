import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, abort)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if g.user:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Wrong Username'
        elif not password:
            error = 'Wrong Password'

        if not error:
            try:
                db.execute('INSERT INTO user (username, password) VALUES (?, ?)',
                           (username, generate_password_hash(password)),
                           )
                db.commit()
            except db.IntegrityError:
                error = f'User {username} is already registered'
            else:
                return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if g.user:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

        if not user:
            error = 'Incorrect Username'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect Password'

        if not error:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged():
    user_id = session.get('user_id')

    if not user_id:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()


@bp.route('logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


@bp.route('/user/<string:username>')
def profile(username):
    if get_db().execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone():
        return render_template('auth/profile.html', username=username)
    abort(404)


@bp.route('/user/<string:username>/settings', methods=('GET', 'POST'))
def settings(username):
    user_id = get_db().execute('SELECT id FROM user WHERE username = ?', (username,)).fetchone()['id']
    if user_id == session.get('user_id'):
        return render_template('auth/settings.html')
    return redirect(url_for('index'))


@bp.route('/user/<string:username>/settings/password', methods=('POST',))
def change_password(username):
    user_id = session.get('user_id')
    user = get_db().execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
    if user_id == user['id']:
        if request.method == 'POST':
            password = request.form['password']
            newpassword = request.form['newpassword']
            error = None

            if not check_password_hash(user['password'], password):
                error = 'Incorrect Password'
            elif password == newpassword:
                error = 'Passwords are the same'

            if not error:
                db = get_db()
                db.execute('UPDATE user SET password = ?'
                           ' WHERE id = ?', (generate_password_hash(newpassword), user_id,))
                db.commit()
                return render_template('auth/profile.html')

            flash(error)

        return render_template('auth/settings.html')

    return redirect(url_for('index'))

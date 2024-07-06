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
        error = None

        if not username:
            error = 'Wrong Username'
        elif not password:
            error = 'Wrong Password'

        if not error:
            db = get_db()
            cur = db.cursor()
            try:
                cur.execute('INSERT INTO "user" (username, password) VALUES (%s, %s)',
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
        cur = db.cursor()
        error = None

        cur.execute('SELECT * FROM "user" WHERE username = %s', (username,))
        user = cur.fetchone()
        if not user:
            error = 'Incorrect Username'
        elif not check_password_hash(user[2], password):
            error = 'Incorrect Password'

        if not error:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged():
    user_id = session.get('user_id')
    if not user_id:
        g.user = None
    else:
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT * FROM "user" WHERE id = %s', (user_id,))
        g.user = cur.fetchone()


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
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM "user" WHERE username = %s', (username,))
    if cur.fetchone():
        return render_template('auth/profile.html', username=username)
    abort(404)


@bp.route('/user/<string:username>/settings', methods=('GET', 'POST'))
def settings(username):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT id FROM "user" WHERE username = %s', (username,))
    user_id = cur.fetchone()[0]
    if user_id == session.get('user_id'):
        return render_template('auth/settings.html')
    return redirect(url_for('index'))


@bp.route('/user/<string:username>/settings/password', methods=('POST',))
def change_password(username):
    db = get_db()
    cur = db.cursor()
    user_id = session.get('user_id')
    cur.execute('SELECT * FROM "user" WHERE username = %s', (username,))
    user = cur.fetchone()
    if user_id == user[0]:
        if request.method == 'POST':
            password = request.form['password']
            newpassword = request.form['newpassword']
            error = None

            if not check_password_hash(user[2], password):
                error = 'Incorrect Password'
            elif password == newpassword:
                error = 'Passwords are the same'

            if not error:
                cur.execute('UPDATE user SET password = %s'
                            ' WHERE id = %s', (generate_password_hash(newpassword), user_id,))
                db.commit()
                return render_template('auth/profile.html')

            flash(error)

        return render_template('auth/settings.html')

    return redirect(url_for('index'))

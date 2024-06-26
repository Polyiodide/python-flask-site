import os

from flask import Flask, render_template


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='dev', DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),)

    from . import db, auth
    db.init_app(app)
    app.register_blueprint(auth.bp)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/user/<string:username>')
    def profile(username):
        from flaskr.db import get_db
        if get_db().execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone():
            return render_template('profile.html')
        return '404'

    return app

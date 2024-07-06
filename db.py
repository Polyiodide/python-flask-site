import psycopg2
import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(host='127.0.0.1',
                                database='test',
                                user='test',
                                password='123123')
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.cursor().execute(f.read().decode('utf-8'))
    db.commit()


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

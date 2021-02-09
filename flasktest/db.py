import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


class Database():
    def __init__(self, path=None):
        if not path:
            path = current_app.config['DATABASE']

        self.db = self.connect(path)
        self.execute = self.db.execute
        self.executescript = self.db.executescript
        self.commit = self.db.commit
        self.close = self.db.close

    def connect(self, path):
        db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        db.row_factory = sqlite3.Row
        return db

    def add_search(self, search):
        query = 'INSERT INTO searches (search) VALUES (?)'
        params = (search, )
        self.execute(query, params)
        self.commit()

    def get_searches(self):
        query = 'SELECT * FROM searches ORDER BY time DESC'
        cur = self.execute(query)
        return cur.fetchall()

    def reset(self):
        with current_app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))


def get_db():
    if 'db' not in g:
        g.db = Database()

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


@click.command('init-db')
@with_appcontext
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    click.echo('Initialised the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)

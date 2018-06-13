import pymysql
import click
from . import db_config
from flask import current_app, g


def db_connect():
     if 'db' not in g:
          g.db = pymysql.connect(host=sql_vals['host'],
                          port=sql_vals['port'],
                          db=sql_vals['db'],
                          user=sql_vals['user'],
                          password=sql_vals['password'])
     return g.db

def db_close():
     db = g.pop('db', None)

     if db is not None:
          db.close()

def init_db():
     db = db_connect()

     with current_app.open_resource('schema.sql') as schema:
          db.executescript(schema.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
     init_db()
     click.echo('Initialized the database.')

def init_app(app):
     app.teardown_appcontext(close_db)
     app.cli.add_command(init_db_command)

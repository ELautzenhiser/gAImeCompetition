import pymysql
import click
from .db_config import *
from flask import current_app, g
from flask.cli import with_appcontext

def parse_sql(filename):
     with current_app.open_resource(filename) as file:
          data = file.read().decode('utf8').split('\n')
          statements = []
          DELIMITER = ';'
          statement = ''

          for line_num, line in enumerate(data):
               if not line.strip():
                    continue

               elif DELIMITER not in line:
                    statement += line

               elif statement:
                    statement += line
                    statements.append(statement.strip())
                    statement = ''
               else:
                    statements.append(line.strip())
          return statements
               

def db_connect():
     if 'db' not in g:
          g.db = pymysql.connect(host=sql_vals['host'],
                          port=sql_vals['port'],
                          db=sql_vals['db'],
                          user=sql_vals['user'],
                          password=sql_vals['password'])
     return g.db

def db_close(e=None):
     db = g.pop('db', None)

     if db is not None:
          db.close()

def init_db():
     db = db_connect()
     statements = parse_sql('schema.sql')
     with db.cursor() as cursor:
          for statement in statements:
               cursor.execute(statement)
     db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
     init_db()
     click.echo('Initialized the database.')

def init_app(app):
     app.teardown_appcontext(db_close)
     app.cli.add_command(init_db_command)

import pymysql
import click
from .database.db_config import *
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
               

def open_db():
     if 'db' not in g:
          g.db = pymysql.connect(host=sql_vals['host'],
                          port=sql_vals['port'],
                          db=sql_vals['db'],
                          user=sql_vals['user'],
                          password=sql_vals['password'])
     return g.db

def get_db():
    c = open_db()
    return c.cursor(pymysql.cursors.DictCursor)

def close_db(e=None):
     db = g.pop('db', None)

     if db is not None:
          db.close()

def init_db():
     #database hasn't been created, so we use a new connection to make it
     db = pymysql.connect(host=sql_vals['host'],
                          port=sql_vals['port'],
                          user=sql_vals['user'],
                          password=sql_vals['password'])
     statements = parse_sql('database/schema.sql')

     with db.cursor() as cursor:
          for statement in statements:
               cursor.execute(statement)
     db.commit()

def query_db(query, num_rows=-1):
     db = open_db()
     with db.cursor(pymysql.cursors.DictCursor) as cursor:
          cursor.execute(query)
     if num_rows == 1:
          return cursor.fetchone()
     elif num_rows == -1:
          return cursor.fetchall()
     else:
          return cursor.fetchmany(num_rows)

def insert_db(table, **kwargs):
     keys = []
     values = []
     for key, value in kwargs:
          keys.append(key)
          if isinstance(value, basestring):
              values.append("'" + value + "'")
          else:
              values.append(str(value))
     key_string = '(' + ', '.join(keys) + ')'
     value_string = '(' + ', '.join(values) + ')'
     
     transaction = 'INSERT INTO {1} {2} VALUES {3};'.format(
                          table, key_string, value_string)

     db = open_db()
     with db.cursor() as cursor:
          success = cursor.execute(transaction)
     db.commit()
     return success

@click.command('init-db')
@with_appcontext
def init_db_command():
     init_db()
     click.echo('Initialized the database.')

def init_app(app):
     app.teardown_appcontext(close_db)
     app.cli.add_command(init_db_command)

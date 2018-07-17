import functools

from flask import (
     Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db, query_db, insert_db
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
     if request.method == 'POST':
          username = request.form['username']
          password = request.form['password']
          email = request.form['email']
          fname = request.form['fname']
          lname = request.form['lname']
          error = None

          if not username:
               error = 'Username is required.'
          elif not password:
               error = 'Password is required.'
          elif query_db("SELECT * FROM Users WHERE username='{0}'".format(username),1):
               error = 'User {} is already registered.'.format(username)

          if error is None:
               register_user(username, email, password, fname, lname)
               return redirect(url_for('auth.login'))

          flash(error)

     return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
     if request.method == 'POST':
          username = request.form['username']
          password = request.form['password']
          db = get_db()
          error = None
          user = query_db("SELECT * FROM Users WHERE username='{0}'".format(username),1)
          if user is None:
               error = 'Incorrect username.'
          elif not check_password_hash(user['password'], password):
               error = 'Incorrect password.'

          if error is None:
               session.clear()
               session['username'] = user['username']
               return redirect(url_for('compete.index'))

          flash(error)

     return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
     username = session.get('username')

     if username is None:
          g.user = None
     else:
          g.user = query_db("SELECT * FROM Users WHERE username='{0}'".format(username),1)

def login_required(view):
     @functools.wraps(view)
     def wrapped_view(**kwargs):
          if g.user is None:
               return redirect(url_for('auth.login'))

          return view(**kwargs)

     return wrapped_view

@bp.route('/logout')
def logout():
     session.clear()
     return redirect(url_for('compete.index'))


def register_user(username, email, password, fname, lname):
     now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
     hashed_pw = generate_password_hash(password)
     insert_db(table='Users',
               username=username,
               email=email,
               password=hashed_pw,
               fname=fname,
               lname=lname,
               created_dt=now,
               commit=True)
     

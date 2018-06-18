import os
from flask import Flask, flash, g, request, redirect, url_for, render_template, Blueprint
from werkzeug.utils import secure_filename
from datetime import datetime
from . import db

UPLOAD_FOLDER = 'gaime/Players'
ALLOWED_EXTENSIONS = set(['py', 'txt'])

bp = Blueprint('players', __name__)

def allowed_file(filename):
     return '.' in filename and \
            filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def save_player_file(file, user, timestamp):
     user_folder = UPLOAD_FOLDER+'/User_'+str(user)
     try:
          os.makedirs(user_folder)
     except OSError:
          pass
     time_str = timestamp.strftime('%Y%m%d%H%M%S')
     filename = time_str+'_'+secure_filename(file.filename)
     try:
          file.save(os.path.join(user_folder, filename))
     except Exception as e:
          return (None, e)
     return (filename, None)

def save_player_db(filename, user, timestamp, game):
     time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
     language = '1'
     insert_statement = 'INSERT INTO Players (file_location, language_id, game_id, author_id, created_dt) ' \
                        'VALUES (\'{0}\', {1}, {2}, {3}, \'{4}\')'.format(filename, language, game, user, time_str)
     return db.insert_db(insert_statement)

def save_player(file, game):
     #needs to be replaced with the actual user once we get the auth setup
     user = 1
     timestamp = datetime.now()     
     filename, error = save_player_file(file, user, timestamp)
     if error:
          return 'Error saving file: '+str(error)
     success = save_player_db(filename, user, timestamp, game)
     if not success:
          return 'Error saving to database.'

@bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
     if request.method == 'POST':
          if 'file' not in request.files:
               flash('No file part')
               return redirect(url_for('upload_file'))
          file = request.files['file']
          if 'game' not in request.form:
               flash('Please choose a game')
               return redirect(url_for('upload_file'))
          game = request.form['game']
          if file.filename == '':
               flash('No selected file')
               return redirect(url_for('compete.index'))
          if file and not allowed_file(file.filename):
               flash('Please upload an approved file type!')
               return redirect(url_for('upload_file'))
          if file and allowed_file(file.filename):
               error = save_player(file, game)
               if error:
                    flash(error)
                    return redirect(url_for('upload_file'))
               else:
                    flash('File successfully uploaded!')
                    return redirect(url_for('compete.index'))
     query = 'SELECT game_id, name FROM Games'
     games = db.query_db(query)
     return render_template('upload.html', games=games)

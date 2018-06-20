import os
from flask import Flask, flash, g, request, redirect, url_for, render_template, Blueprint
from werkzeug.utils import secure_filename
from datetime import datetime
from .db import insert_db, query_db

UPLOAD_FOLDER = 'UserSubmissions'
ALLOWED_EXTENSIONS = set(['py', 'txt'])

bp = Blueprint('upload', __name__, url_prefix='/upload')

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
    insert_statement = 'INSERT INTO Uploads (filename, language_id, game_id, author_id, created_dt, type) ' \
                    'VALUES (\'{0}\', {1}, {2}, {3}, \'{4}\', \'Player\')'.format(filename, language, game, user, time_str)
    return insert_db(insert_statement)

def save_player(file, game):
    #needs to be replaced with the actual user once we get the auth setup
    user = g.user['id']
    timestamp = datetime.now()    
    filename, error = save_player_file(file, user, timestamp)
    if error:
        return 'Error saving file: '+str(error)
    success = save_player_db(filename, user, timestamp, game)
    if not success:
        return 'Error saving to database.'

def save_game(author_id, title, description, referee_code, language_id):
    ref_dir = UPLOAD_FOLDER + '/Referees/' + str(author_id)
    desc_dir = UPLOAD_FOLDER + '/GameDescriptions/' + str(author_id)
    try:
        os.makedirs(ref_dir)
        os.makedirs(desc_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            return e
    except Exception as e:
        return e

    time_str = datetime.now().strftime('%Y%m%d%H%M%S')
    extension = ""
    if language_id == 1:
        ext = '.py'
    ref_filename = secure_filename(time_str + title + ext)
    desc_filename = secure_filename(time_str + title + '.md')
    try:
        with open(os.path.join(ref_dir, 'ref_filename')) as f:
            f.write(referee_code)
        with open(os.path.join(desc_dir, 'desc_filename')) as f:
            f.write(description)
    except Exception as e:
        return e

    success = insert_db(Uploads,
                        filename=ref_filename,
                        language_id=language_id,
                        game_id=
    success = insert_db(Uploads,
                        filename,

    
    return(filename, None)
        
    

@bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('You must choose a file to upload')
            return redirect(url_for('upload.upload_file'))
        file = request.files['file']
        if 'game' not in request.form:
            flash('Please choose a game')
            return redirect(url_for('upload.upload_file'))
        game = request.form['game']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('compete.index'))
        if file and not allowed_file(file.filename):
            flash('Please upload an approved file type!')
            return redirect(url_for('upload.upload_file'))
        if file and allowed_file(file.filename):
            error = save_player(file, game)
            if error:
                flash(error)
                return redirect(url_for('upload_file'))
            else:
                flash('File successfully uploaded!')
                return redirect(url_for('compete.index'))
    query = 'SELECT game_id, name FROM Games'
    games = query_db(query)
    return render_template('upload.html', games=games)

@bp.route('/game', methods=['GET', 'POST']))
def upload_game():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        referee_code = request.form['referee_code']

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            error = save_game(g.user['id'], title, description, referee_code)
        return redirect(url_for('compete.index'))

    return render_template('upload/game.html')

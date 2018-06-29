import os, errno
from flask import Flask, flash, g, request, redirect, url_for, render_template, Blueprint
from werkzeug.utils import secure_filename
from datetime import datetime
from .db import insert_db, query_db, rollback_db, commit_db

PLAYER_FOLDER = 'UserSubmissions/Players/User_{0}'
GAME_FOLDER = 'UserSubmissions/Games/Game_{0}'
ALLOWED_EXTENSIONS = set(['py', 'txt'])

bp = Blueprint('upload', __name__, url_prefix='/upload')

def allowed_file(filename):
    return '.' in filename and \
          filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def save_player_file(name, code, user, timestamp):
    user_folder = PLAYER_FOLDER.format(user)
    try:
        os.makedirs(user_folder)
    except OSError:
        pass
    time_str = timestamp.strftime('%Y%m%d%H%M%S')
    filename = time_str+'_'+name+'.py'
    try:
        with open(os.path.join(user_folder, filename), 'w') as file:
            file.write(code)
    except Exception as e:
        return (None, e)
    return (filename, None)

def save_player_db(filename, user, timestamp, game):
    time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    language = '1'
    return insert_db(table='Uploads',
                     filename=filename,
                     language_id=language,
                     game_id=game,
                     author_id=user,
                     created_dt=time_str,
                     type='Player',
                     status='Unpublished')

def save_player(code, name, game):
    user = g.user['id']
    timestamp = datetime.now()    
    filename, error = save_player_file(name, code, user, timestamp)
    if error:
        return 'Error saving file: '+str(error)
    success = save_player_db(filename, user, timestamp, game)
    if not success:
        return 'Error saving to database.'

def save_game(author_id, title, description, referee_code,
              language_id):

    desc_filename = "doc.md"
    ref_filename = "ref.py" 

    success = insert_db(table='Games', commit=False,
                        name=title,
                        doc_file=desc_filename,
                        min_num_players=1,
                        max_num_players=1,
                        author_id=author_id,
                        status='Published')
    if not success:
        rollback_db()
        return "Transaction Error: unable to insert Game"
    game_id = query_db('SELECT LAST_INSERT_ID()', 1)['LAST_INSERT_ID()']

    success = insert_db(table='Uploads', commit=False,
                        filename=ref_filename,
                        language_id=language_id,
                        game_id=game_id,
                        author_id=author_id,
                        type='Ref',
                        status='Published')
    if not success:
        rollback_db()
        return "Transaction Error: unable to insert Upload"

    game_dir = GAME_FOLDER.format(game_id)

    try:
        os.makedirs(game_dir)
    except Exception as e:
        if e.errno != errno.EEXIST:
            rollback_db()
            return e

    try:
        with open(os.path.join(game_dir, ref_filename), 'w+') as f:
            f.write(referee_code)
        with open(os.path.join(game_dir, desc_filename), 'w+') as f:
            f.write(description)
    except Exception as e:
        rollback_db()
        return e

    commit_db()

    return None

@bp.route('/player', methods=['GET', 'POST'])
def upload_player():
    if request.method == 'POST':
        if request.form['player_code'] == '':
            flash('Your player must have some code!')
            return redirect(url_for('upload.upload_player'))
        code = request.form['player_code']
        if request.form['name'] == '':
            flash('Your player must have a name!')
            return redirect(url_for('upload.upload_player'))
        name = request.form['name']
        if 'game' not in request.form:
            flash('Please choose a game')
            return redirect(url_for('upload.upload_player'))
        game = request.form['game']
        error = save_player(code, name, game)
        if error:
            flash(error)
            return redirect(url_for('upload_player'))
        else:
            flash('Player successfully saved!')
            return redirect(url_for('compete.index'))
    query = 'SELECT game_id, name FROM Games'
    games = query_db(query)
    return render_template('upload/player.html', games=games)

@bp.route('/game', methods=['GET', 'POST'])
def upload_game():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        referee_code = request.form['referee_code']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            error = save_game(g.user['id'], title, description, referee_code, 1)
            if error:
                flash(error)
            else:
                flash('Game submitted!')
                return redirect(url_for('compete.index'))
    return render_template('upload/game.html')

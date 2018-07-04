import os, errno
from flask import Flask, flash, g, request, redirect, url_for, render_template, Blueprint
from werkzeug.utils import secure_filename
from datetime import datetime
from .db import insert_db, query_db, rollback_db, commit_db, get_all_rows
from .input_checks import check_game_input, check_player_input

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
            file.write(code.replace('\r\n','\n'))
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
              language_id, min_players, max_players):

    desc_filename = "doc.md"
    ref_filename = "ref.py" 

    success = insert_db(table='Games', commit=False,
                        name=title,
                        doc_file=desc_filename,
                        min_num_players=min_players,
                        max_num_players=max_players,
                        author_id=author_id,
                        status='Unpublished')
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
                        status='Unpublished')
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
            f.write(referee_code.replace('\r\n','\n'))
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
        player_name = request.form.get('player_name')
        player_code = request.form.get('player_code')
        player_game = request.form.get('player_game')
        
        errors = check_player_input(player_name, player_code, player_game)
        if not errors:
            errors = save_player(player_code, player_name, player_game)
        if errors:
            flash('ERRORS:')
            for error in errors:
                flash(str(error))
            try:
                player_game = int(player_game)
            except:
                player_game = 0
            games = get_all_rows('games')
            return render_template('upload/player.html',
                                   games=games,
                                   player_name=player_name,
                                   player_code=player_code,
                                   player_game=player_game)
        else:
            flash('Player successfully saved!')
            return redirect(url_for('compete.index'))
        
    games = get_all_rows('Games')
    return render_template('upload/player.html',
                           games=games,
                           player_name='',
                           player_code='',
                           player_game='')


@bp.route('/game', methods=['GET', 'POST'])
def upload_game():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        referee_code = request.form.get('referee_code')
        min_players = request.form.get('min_players')
        max_players = request.form.get('max_players')
        try:
            min_players = int(min_players)
            max_players = int(max_players)
        except:
            min_players = None
            max_players = None

        errors = check_game_input(name, description, referee_code, min_players, max_players)
        if not errors:
            errors = save_game(g.user['id'], name, description, referee_code, 1,
                                    min_players, max_players)
        if errors:
            flash('ERROR:')
            for error in errors:
                flash(str(error))
            return render_template('upload/game.html',
                                   name=name,
                                   description=description,
                                   referee_code=referee_code,
                                   min_players=min_players,
                                   max_players=max_players)
        else:
            flash('Game submitted!')
            return redirect(url_for('games.view_games', username=g.user['username']))
    return render_template('upload/game.html',
                           name='',
                           description='',
                           referee_code='')

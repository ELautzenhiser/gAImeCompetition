import os
from flask import Blueprint, flash, g, request, redirect, url_for, render_template
from .db import query_db, get_db_row, update_db, rollback_db, commit_db, open_db
from .input_checks import check_game_input

GAME_FOLDER = 'UserSubmissions/Games/Game_{0}/'

bp = Blueprint('games', __name__)

@bp.route('/user/<username>/games', methods=['GET','POST'])
def view_games(username):
    games = get_games(username)
    return render_template('games.html', games=games, username=username)

def get_games(username):
    games_query = 'SELECT * FROM Games g ' \
                  'INNER JOIN Users u on g.author=u.username ' \
                  'WHERE u.username="{0}" ' \
                  'ORDER BY g.created_dt DESC'.format(username)

    return query_db(games_query)

def get_ref_filename(game_id, filename='ref.py'):
    folder = GAME_FOLDER.format(game_id)
    return os.path.join(folder, filename)

def get_desc_filename(game_id, filename='doc.md'):
    folder = GAME_FOLDER.format(game_id)
    return os.path.join(folder, filename)

def update_game(game_id, name, desc_filename, description, ref_filename, referee_code, min_players, max_players):
    errors = []
    update_query = 'UPDATE Games SET name="{0}", min_num_players={1}, max_num_players={2} ' \
                   'WHERE game_id={3};'.format(name, min_players, max_players, game_id)
    
    update_db(update_query, commit=False)
    try:
        with open(ref_filename, 'w') as ref_file:
            ref_file.write(referee_code.replace('\r\n','\n'))
        with open(desc_filename, 'w') as desc_file:
            desc_file.write(description)
    except Exception as e:
        rollback_db()
        errors.append(e)
        return errors

    commit_db()
    return None
    

@bp.route('/game/<int:game_id>/edit', methods=('POST','GET'))
def edit_game(game_id):
    game = get_db_row('Games', game_id)
    ref_filename = get_ref_filename(game_id)
    desc_filename = get_desc_filename(game_id)
    if request.method == 'GET':
        try:
            with open(ref_filename, 'r') as ref_file:
                game['referee_code'] = ref_file.read()
        except Exception as e:
            flash(str(e))
            game['ref_code'] = ''
        try:
            with open(desc_filename, 'r') as desc_file:
                game['description'] = desc_file.read()
        except Exception as e:
            flash(str(e))
            game['description'] = ''
        return render_template('edit_game.html', game=game)
    else:
        if request.form.get('action') == 'Save':
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
                errors = update_game(game_id,
                                    name,
                                    desc_filename,
                                    description,
                                    ref_filename,
                                    referee_code,
                                    min_players,
                                    max_players)
            if errors:
                for error in errors:
                    flash(error)
                game['name'] = name
                game['description'] = description
                game['referee_code'] = referee_code
                game['min_num_players'] = min_players
                game['max_num_players'] = max_players
                return render_template('edit_game.html',
                                       game=game)
            flash('Game updated!')
        return redirect(url_for('games.view_games',username=g.user.get('username')))

def change_game_status(game_id,status):
    statement = 'UPDATE Games SET status="{0}" WHERE ' \
                'game_id={1}'.format(status,game_id)
    return update_db(statement)


@bp.route('/game/<int:game_id>/retire', methods=('POST',))
def retire_game(game_id):
    success = change_game_status(game_id,'Retired')
    if not success:
        flash('Could not retire game')
    return redirect(url_for('games.view_games',username=g.user.get('username')))
     
@bp.route('/game/<int:game_id>/publish', methods=('POST',))
def publish_game(game_id):
    success = change_game_status(game_id,'Published')
    if not success:
        flash('Could not publish player')
    return redirect(url_for('games.view_games',username=g.user.get('username')))

import os
from flask import Blueprint, flash, g, request, redirect, url_for, render_template
from .db import query_db, get_db_row, update_db, rollback_db, commit_db, open_db
from .input_checks import check_game_input

GAME_PATH = 'UserSubmissions/Games/Game_{0}/{1}'

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

@bp.route('/game_info/<int:game_id>', methods=('POST','GET'))
def game_info(game_id):
    if g.user:
        username = g.user.get('username')
        players_query = 'SELECT up.upload_id, ' \
                        'SUBSTRING(up.filename, 16) as filename, ' \
                        'up.created_dt, l.name as language, ' \
                        'COALESCE(SUM(m.points),0) as score ' \
                        'FROM Uploads up inner join Languages l ' \
                        'ON up.language_id = l.language_id ' \
                        'LEFT JOIN Match_players m ON up.upload_id=m.player_id ' \
                        'WHERE up.author="{0}" AND up.status="Published" ' \
                        'AND up.type=\'Player\' AND up.game_id={1} ' \
                        'GROUP BY up.upload_id ' \
                        'ORDER BY up.created_dt DESC'.format(username, game_id)
        players = query_db(players_query)
    else:
        username = None
        players = None
    
    game_query = 'SELECT g.author, g.name, g.created_dt, g.max_num_players, g.game_id, ' \
                 'g.min_num_players, g.doc_file, u.username from Games g INNER JOIN Users u ' \
                 'ON g.author=u.username WHERE g.game_id={0}'.format(game_id)
    game = query_db(game_query, 1)
    doc_filename = GAME_PATH.format(game['game_id'],game['doc_file'])
    with open(doc_filename, 'r') as doc_file:
        game['documentation'] = doc_file.read()

    top_query = 'SELECT COALESCE(SUM(m.points),0) score, up.upload_id, u.username, ' \
                'up.created_dt ' \
                'FROM Uploads up INNER JOIN Users u on up.author=u.username ' \
                'LEFT JOIN Match_players m on up.upload_id=m.player_id ' \
                'WHERE up.type="Player" AND up.status="Published" ' \
                'AND up.game_id={0} GROUP BY up.upload_id ' \
                'ORDER BY score DESC limit 1'.format(game_id)
    
    top_player = query_db(top_query, 1)

    return render_template('compete/game_info.html',game=game, players=players,
                           top_player=top_player, username=username)

def get_ref_filename(game_id, filename='ref.py'):
    return GAME_PATH.format(game_id, filename)

def get_desc_filename(game_id, filename='doc.md'):
    return GAME_PATH.format(game_id, filename)

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
    if not (g.user and g.user['username']==game['author']):
        flash('You are not authorized to edit this game.')
        if game['status'] == 'Published':
            return redirect(url_for('games.game_info', game_id=game['game_id']))
        else:
            return redirect(url_for('compete.index'))
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
    game = get_db_row('Games', game_id)
    if not (g.user and g.user['username']==game['author']):
        flash('You are not authorized to retire this game.')
        if game['status'] == 'Published':
            return redirect(url_for('games.game_info', game_id=game['game_id']))
        else:
            return redirect(url_for('compete.index'))
    success = change_game_status(game_id,'Retired')
    if not success:
        flash('Could not retire game')
    return redirect(url_for('games.view_games',username=g.user.get('username')))
     
@bp.route('/game/<int:game_id>/publish', methods=('POST',))
def publish_game(game_id):
    game = get_db_row('Games', game_id)
    if not (g.user and g.user['username']==game['author']):
        flash('You are not authorized to publish this game.')
        if game['status'] == 'Published':
            return redirect(url_for('games.game_info', game_id=game['game_id']))
        else:
            return redirect(url_for('compete.index'))
    success = change_game_status(game_id,'Published')
    if not success:
        flash('Could not publish player')
    return redirect(url_for('games.view_games',username=g.user.get('username')))

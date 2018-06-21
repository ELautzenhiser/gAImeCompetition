from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from .db import query_db
import random

bp = Blueprint('compete', __name__)
DOCUMENTATION_FOLDER = 'UserSubmissions/GameDescriptions/'

@bp.route('/')
def index():
    #The query will need to be updated to only show games with an active referee
    game_query = 'SELECT g.game_id, g.name, g.max_num_players, u.username, ' \
                 'g.created_dt, COALESCE(up.count,0) as num_competitors ' \
                 'FROM Games g INNER JOIN Users u ON g.author_id = u.user_id ' \
                 'LEFT JOIN (SELECT count(upload_id) as count, ' \
                 'game_id from Uploads where active="Active" and ' \
                 'type="Player" GROUP BY game_id) up on g.game_id=up.game_id ' \
                 'GROUP BY g.game_id ORDER BY g.game_id DESC '
    games = query_db(game_query, -1)
    return render_template('compete/index.html', games=games)

@bp.route('/game_info/<int:game_id>', methods=('POST','GET'))
def game_info(game_id):
<<<<<<< HEAD
    #user to be added
    print(dir(session))
    user = 1
=======
    user_id = g.user['id']
>>>>>>> edward
    players_query = 'SELECT up.upload_id, ' \
                    'SUBSTRING(up.filename, 16) as filename, ' \
                    'up.created_dt, l.name as language, ' \
                    'COALESCE(SUM(m.points),0) as score ' \
                    'FROM Uploads up inner join Languages l ' \
                    'ON up.language_id = l.language_id ' \
                    'LEFT JOIN Match_players m ON up.upload_id=m.player_id ' \
                    'WHERE up.author_id={0} AND up.active=\'Active\' ' \
                    'AND up.type=\'Player\' AND up.game_id={1} ' \
                    'GROUP BY up.upload_id ' \
                    'ORDER BY up.created_dt DESC'.format(user_id, game_id)
    players = query_db(players_query)
    
    game_query = 'SELECT g.author_id, g.name, g.created_dt, g.max_num_players, g.game_id, ' \
                 'g.min_num_players, g.doc_file, u.username from Games g INNER JOIN Users u ' \
                 'ON g.author_id=u.user_id WHERE g.game_id={0}'.format(game_id)
    game = query_db(game_query, 1)
    doc_filename = DOCUMENTATION_FOLDER+str(game['author_id'])+'/'+game['doc_file']
    with open(doc_filename, 'r') as doc_file:
        game['documentation'] = doc_file.read()

    top_query = 'SELECT COALESCE(SUM(m.points),0) score, up.upload_id, u.username, ' \
                'up.created_dt ' \
                'FROM Uploads up INNER JOIN Users u on up.author_id=u.user_id ' \
                'LEFT JOIN Match_players m on up.upload_id=m.player_id ' \
                'WHERE up.type=\'Player\' AND up.active=\'Active\' ' \
                'AND up.game_id={0} GROUP BY up.upload_id ' \
                'ORDER BY score DESC limit 1'.format(game_id)
    
    top_player = query_db(top_query, 1)

    return render_template('compete/game_info.html',game=game, players=players,
<<<<<<< HEAD
                           top_player=top_player, user=user)


=======
                           top_player=top_player, user_id=user_id)

def compete(challenger, challenged, ref, game_id):
    flash('This is a placeholder! Good fight!')
    return redirect(url_for('compete.index'))

@bp.route('/game/<int:game_id>/compete/<int:player_id>', methods=('POST','GET'))
def start_competition(player_id,game_id):
    user_id = g.user['id']

    game = get_game_from_id(game_id)

    if not game:
        flash('Something went wrong! Try again later.')
        return redirect(url_for('compete.index'))
    
    ref = get_ref_for_game(game_id)

##    if not ref:
##        flash('There is no referee for that game. Sorry!')
##        return redirect(url_for('compete.index'))
    
    #For right now, prevent player from competing against itself
    #In future, prevent player from competing against any from the same user
    other_players = get_other_players_for_game(game_id, player_id)
    
    if len(other_players) < (game['min_num_players'] - 1):
        flash("There aren't enough players! Wait for another user to join the game, or push one of your friends to!")
        return redirect(url_for('compete.game_info', game_id=game_id))

    num_challenged = random.randint(game['min_num_players']-1, min(len(other_players), game['max_num_players']-1))
    challenged = []
    for i in range(num_challenged):
        challenged.append(other_players.pop())

    challenger = get_player_from_id(player_id)
    
    return compete(challenger, challenged, ref, game_id)


def get_game_from_id(game_id):
    query = 'SELECT min_num_players, max_num_players ' \
           'FROM Games WHERE game_id={0}'.format(game_id)
    return query_db(query, 1)

def get_ref_for_game(game_id):
    query = 'SELECT upload_id, filename FROM Uploads WHERE active="Active" ' \
            'AND game_id={0} AND type="Ref" ORDER BY created_dt DESC LIMIT 1'.format(game_id)
    return query_db(query, 1)

def get_other_players_for_game(game_id, player_id):
    query = 'SELECT upload_id, author_id, filename FROM Uploads ' \
            'WHERE type="Player" AND active="Active" AND ' \
            'game_id={0} AND upload_id<>{1} ' \
            'ORDER BY RAND()'.format(game_id,player_id)
    return query_db(query, -1)

def get_player_from_id(player_id):
    query = 'SELECT upload_id, author_id, filename FROM Uploads ' \
            'WHERE upload_id={0}'.format(player_id)
    return query_db(query, 1)
>>>>>>> edward

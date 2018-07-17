from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from .db import query_db, get_db_row
import random

bp = Blueprint('compete', __name__)

@bp.route('/')
def index():
    #The query will need to be updated to only show games with an active referee
    game_query = 'SELECT g.game_id, g.name, g.max_num_players, u.username, ' \
                 'g.created_dt, COALESCE(up.count,0) as num_competitors ' \
                 'FROM Games g INNER JOIN Users u ON g.author = u.username ' \
                 'LEFT JOIN (SELECT count(upload_id) as count, ' \
                 'game_id from Uploads where status="Published" and ' \
                 'type="Player" GROUP BY game_id) up on g.game_id=up.game_id ' \
                 'WHERE g.status="Published" ' \
                 'GROUP BY g.game_id ORDER BY g.game_id DESC '
    games = query_db(game_query, -1)
    return render_template('compete/index.html', games=games)

def compete(challenger, challenged, ref, game_id):
    flash('This is a placeholder! Good fight!')
    return redirect(url_for('compete.index'))

@bp.route('/game/<int:game_id>/compete/<int:player_id>', methods=('POST','GET'))
def start_competition(player_id,game_id):
    username = g.user['username']

    game = get_db_row('games',game_id)

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

    challenger = get_db_row('uploads',player_id)
    
    return compete(challenger, challenged, ref, game_id)


def get_ref_for_game(game_id):
    query = 'SELECT upload_id, filename FROM Uploads WHERE status="Published" ' \
            'AND game_id={0} AND type="Ref" ORDER BY created_dt DESC LIMIT 1'.format(game_id)
    return query_db(query, 1)

def get_other_players_for_game(game_id, player_id):
    query = 'SELECT upload_id, author, filename FROM Uploads ' \
            'WHERE type="Player" AND status="Published" AND ' \
            'game_id={0} AND upload_id<>{1} ' \
            'ORDER BY RAND()'.format(game_id,player_id)
    return query_db(query, -1)


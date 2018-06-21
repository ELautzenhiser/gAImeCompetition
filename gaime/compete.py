from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .db import query_db

bp = Blueprint('compete', __name__)
DOCUMENTATION_FOLDER = 'UserSubmissions/GameDescriptions/'

@bp.route('/')
def index():
    game_query = 'SELECT g.game_id, g.name, g.max_num_players, u.username, ' \
                 'g.created_dt, COALESCE(up.count,0) as num_competitors ' \
                 'FROM Games g INNER JOIN Users u ON g.author_id = u.user_id ' \
                 'LEFT JOIN (SELECT count(upload_id) as count, ' \
                 'game_id from Uploads where active="Active" and ' \
                 'type="Player" GROUP BY game_id) up on g.game_id=up.game_id ' \
                 'GROUP BY g.game_id ORDER BY g.game_id DESC '
    games = query_db(game_query, -1)
    print(games)
    return render_template('compete/index.html', games=games)

@bp.route('/game_info/<int:game_id>', methods=('POST','GET'))
def game_info(game_id):
    #user to be added
    user = 1
    players_query = 'SELECT up.upload_id, ' \
                    'SUBSTRING(up.filename, 16) as filename, ' \
                    'up.created_dt, l.name as language, ' \
                    'COALESCE(SUM(m.points),0) as score ' \
                    'FROM Uploads up inner join Languages l ' \
                    'ON up.language_id = l.language_id ' \
                    'LEFT JOIN Matches m ON up.upload_id=m.winner_id ' \
                    'WHERE up.author_id={0} AND up.active=\'Active\' ' \
                    'AND up.type=\'Player\' AND up.game_id={1} ' \
                    'GROUP BY up.upload_id ' \
                    'ORDER BY up.created_dt DESC'.format(user, game_id)
    players = query_db(players_query)
    
    game_query = 'SELECT g.author_id, g.name, g.created_dt, g.max_num_players, u.username, ' \
                 'g.min_num_players, g.doc_file from Games g INNER JOIN Users u ' \
                 'ON g.author_id=u.user_id WHERE g.game_id={0}'.format(game_id)
    game = query_db(game_query, 1)
    doc_filename = DOCUMENTATION_FOLDER+str(game['author_id'])+'/'+game['doc_file']
    with open(doc_filename, 'r') as doc_file:
        game['documentation'] = doc_file.read()

    top_query = 'SELECT COALESCE(SUM(m.points),0) score, up.upload_id, u.username, ' \
                'up.created_dt ' \
                'FROM Uploads up INNER JOIN Users u on up.author_id=u.user_id ' \
                'LEFT JOIN Matches m on up.upload_id=m.winner_id ' \
                'WHERE up.type=\'Player\' AND up.active=\'Active\' ' \
                'AND up.game_id={0} GROUP BY up.upload_id ' \
                'ORDER BY score DESC limit 1'.format(game_id)
    
    top_player = query_db(top_query, 1)

    return render_template('compete/game_info.html',game=game, players=players,
                           top_player=top_player, user=user)

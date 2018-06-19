from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .db import query_db

bp = Blueprint('compete', __name__)

@bp.route('/')
def index():
    game_query = 'SELECT g.name, g.max_num_players, u.username, g.created_dt, ' \
                 'count(up.upload_id) as num_competitors ' \
                 'FROM Games g INNER JOIN Users u ON g.author_id = u.user_id ' \
                 'LEFT JOIN Uploads up on g.game_id=up.game_id ' \
                 'WHERE up.active=\'Active\' AND up.type=\'Player\' ' \
                 'GROUP BY g.game_id ORDER BY g.game_id DESC '
    games = query_db(game_query, 20)
    return render_template('compete/index.html', games=games)

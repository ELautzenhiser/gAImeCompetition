from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .db import query_db

bp = Blueprint('compete', __name__)

@bp.route('/')
def index():
    game_query = 'SELECT g.name, g.max_num_players, u.username, g.created_dt' \
    ' FROM Games g JOIN Users u ON g.author_id = u.user_id' \
    ' ORDER BY game_id DESC'
    games = query_db(game_query, 20)
    return render_template('compete/index.html', games=games)

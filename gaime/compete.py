from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .db.db import get_db

bp = Blueprint('compete', __name__)

@bp.route('/')
def index():
    db = get_db()
    db.execute(
        'SELECT name, max_num_players, username, created_dt'
        ' FROM Games JOIN Users ON Games.author_id = Users.user_id'
        ' ORDER BY game_id DESC'
    )
    games = db.fetchmany(20)
    return render_template('compete/index.html', games=games)

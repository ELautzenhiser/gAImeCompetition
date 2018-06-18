from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .db import get_db

bp = Blueprint('compete', __name__)

@bp.route('/')
def index():
    db = get_db()
    db.execute(
        'SELECT g.name, g.max_num_players, u.username, g.created_dt'
        ' FROM Games g JOIN Users u ON g.author_id = u.user_id'
        ' ORDER BY game_id DESC'
    )
    games = db.fetchmany(20)
    return render_template('compete/index.html', games=games)

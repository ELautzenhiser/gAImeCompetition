from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .db.db import db_connect

bp = Blueprint('compete', __name__)

@bp.route('/')
def index():
    db = db_connect()
    games = db.execute(
        'SELECT name, max_num_players, username, created'
        ' FROM Games JOIN Users ON Games.author_id = Users.id'
        ' ORDER BY game_id DESC'
    ).fetchmany(20)
    return render_template('compete/index.html', games=games)
    

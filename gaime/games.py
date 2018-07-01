import os
from flask import Blueprint, flash, g, request, redirect, url_for, render_template
from .db import query_db, get_db_row

bp = Blueprint('games', __name__)

@bp.route('/games', methods=['GET'])
def view_games():
    user_id = g.user['id']
    games = get_games(user_id)
    return render_template('games.html', games=games)

def get_games(user_id):
    games_query = 'SELECT * FROM Games ' \
                  'WHERE author_id={0} ' \
                  'ORDER BY created_dt DESC'.format(user_id)

    return query_db(games_query)
    

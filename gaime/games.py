import os
from flask import Blueprint, flash, g, request, redirect, url_for, render_template
from .db import query_db, get_db_row, update_db

bp = Blueprint('games', __name__)

@bp.route('/user/<username>/games', methods=['GET'])
def view_games(username):
    games = get_games(username)
    return render_template('games.html', games=games, username=username)

def get_games(username):
    games_query = 'SELECT * FROM Games g ' \
                  'INNER JOIN Users u on g.author_id=u.user_id ' \
                  'WHERE u.username="{0}" ' \
                  'ORDER BY g.created_dt DESC'.format(username)

    return query_db(games_query)

def change_game_status(game_id,status):
    statement = 'UPDATE Games SET status="{0}" WHERE ' \
                'game_id={1}'.format(status,game_id)
    return update_db(statement)

@bp.route('/game/<int:game_id>/retire', methods=('POST',))
def retire_game(game_id):
    success = change_game_status(game_id,'Retired')
    if not success:
        flash('Could not retire game')
    return redirect(url_for('games.view_games',username=g.user.get('username')))
     
@bp.route('/game/<int:game_id>/publish', methods=('POST',))
def publish_game(game_id):
    success = change_game_status(game_id,'Published')
    if not success:
        flash('Could not publish player')
    return redirect(url_for('games.view_games',username=g.user.get('username')))

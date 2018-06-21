import os
from flask import Blueprint, flash, g, request, redirect, url_for, render_template
from datetime import datetime
from .db import query_db, insert_db, update_db, get_db_row

PLAYER_FOLDER = 'UserSubmissions/Players/User_{0}/'
ARCHIVE_FOLDER = 'UserSubmissions/Archive/Players/User_{0}'

bp = Blueprint('players', __name__)

@bp.route('/players', methods=['GET', 'POST'])
def view_players():
     user_id = g.user['id']
     players_query = 'SELECT up.upload_id, ' \
                     'SUBSTRING(up.filename, 16) as filename, ' \
                     'up.created_dt, g.name as game, l.name as language, ' \
                     'COALESCE(SUM(m.points),0) as score ' \
                     'FROM Uploads up inner join Languages l ' \
                     'ON up.language_id = l.language_id ' \
                     'INNER JOIN Games g ON up.game_id = g.game_id ' \
                     'LEFT JOIN Match_players m ON up.upload_id=m.player_id ' \
                     'WHERE up.author_id={0} AND up.active=\'Active\' ' \
                     'AND up.type=\'Player\' GROUP BY up.upload_id ' \
                     'ORDER BY up.created_dt DESC'.format(user_id)
     
     players = query_db(players_query, -1)
     return render_template('players.html', player_dict=players)

def archive_player_file(upload_id):
     player = get_db_row('uploads',upload_id)
     
     user_id = player['author_id']
     filename = player['filename']
     
     origin_folder = PLAYER_FOLDER.format(user_id)
     destination_folder = ARCHIVE_FOLDER.format(user_id)
     try:
          os.makedirs(destination_folder)
     except OSError:
          pass
     try:
          os.rename(origin_folder+'/'+filename, destination_folder + '/' + filename)
     except OSError as e:
          return e

def deactivate_player(upload_id):
     update_statement = 'UPDATE Uploads SET active=\'Inactive\' ' \
                  'WHERE upload_id={0}'.format(upload_id)
     
     return update_db(update_statement)

@bp.route('/<int:upload_id>/delete', methods=('POST',))
def delete(upload_id):
     success = deactivate_player(upload_id)
     if not success:
          flash('Could not delete player')
          return redirect(url_for('players.view_players'))
     error = archive_player_file(upload_id)
     if error:
          flash('Error: '+str(error))
          return redirect(url_for('players.view_players'))
     return redirect(url_for('players.view_players'))

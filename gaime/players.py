import os
from flask import Blueprint, flash, g, request, redirect, url_for, render_template
from datetime import datetime
from .db import query_db, insert_db, update_db, get_db_row

PLAYER_FOLDER = 'UserSubmissions/Players/User_{0}/'
ARCHIVE_FOLDER = 'UserSubmissions/Archive/Players/User_{0}'

bp = Blueprint('players', __name__)

@bp.route('/user/<username>/players', methods=['GET', 'POST'])
def view_players(username):
     player_filter = request.form.get('Filter')
     players = get_players(username, player_filter)
     return render_template('players.html',
                            player_dict=players,
                            player_filter=player_filter,
                            username=username)

def get_players(username, player_filter):
     filter_dict = {'published' : 'AND up.status="Published" ',
                    'unpublished' : 'AND up.status="Unpublished" ',
                    'retired' : 'AND up.status="Retired" ',
                    'all' : '',
                    None : ''}
     
     players_query = 'SELECT up.upload_id, up.author_id, ' \
                     'SUBSTRING(up.filename, 16) as filename, ' \
                     'up.created_dt, g.name as game, l.name as language, ' \
                     'COALESCE(SUM(m.points),0) as score, up.status ' \
                     'FROM Uploads up inner join Languages l ' \
                     'ON up.language_id = l.language_id ' \
                     'INNER JOIN Games g ON up.game_id = g.game_id ' \
                     'INNER JOIN Users u ON up.author_id = u.user_id ' \
                     'LEFT JOIN Match_players m ON up.upload_id=m.player_id ' \
                     'WHERE u.username="{0}" AND ' \
                     'up.type="Player" {1}GROUP BY up.upload_id ' \
                     'ORDER BY CASE up.status WHEN "Unpublished" THEN 1 ' \
                     'WHEN "Published" THEN 2 ELSE 3 END, ' \
                     'up.created_dt DESC'.format(username, filter_dict[player_filter])
     
     players = query_db(players_query, -1)
     return players
     
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

     
def get_player_name(filename):
     name = os.path.splitext(os.path.basename(filename))[0][15:]
     return name

def get_player_file(user_id, filename):
     folder = PLAYER_FOLDER.format(user_id)
     return os.path.join(folder, filename)


def change_player_status(upload_id,status):
     statement = 'Update Uploads SET status="{0}" WHERE ' \
                 'upload_id={1}'.format(status,upload_id)
     return update_db(statement)

@bp.route('/player/<int:upload_id>/edit', methods=('POST','GET'))
def edit_player(upload_id):
     player = get_db_row('Uploads', upload_id)
     filename = get_player_file(player['author_id'], player['filename'])
     if request.method == 'GET':
          player['name'] = get_player_name(player['filename'])
          try:
               with open(filename, 'r') as file:
                    player['code'] = file.read()
          except Exception as e:
               flash(str(e))
               player['code'] = ''
          return render_template('edit_player.html', player=player)

     elif request.method == 'POST':
          if request.form.get('action') == 'Save':
               player = get_db_row('Uploads', upload_id)
               filename = get_player_file(player['author_id'], player['filename'])
               try:
                    with open(filename, 'w') as file:
                         file.write(request.form['code'].replace('\r\n', '\n'))
               except Exception as e:
                    flash(str(e))
          return redirect(url_for('players.view_players',username=g.user.get('username')))

@bp.route('/player/<int:upload_id>/retire', methods=('POST',))
def retire_player(upload_id):
     success = change_player_status(upload_id,'Retired')
     if success:
          error = archive_player_file(upload_id)
          if error:
               flash('Error: '+str(error))
     else:
          flash('Could not retire player')

     return redirect(url_for('players.view_players',username=g.user.get('username')))


@bp.route('/<int:upload_id>/publish', methods=('POST',))
def publish_player(upload_id):
     success = change_player_status(upload_id,'Published')
     if not success:
          flash('Could not publish player')
     return redirect(url_for('players.view_players',username=g.user.get('username')))





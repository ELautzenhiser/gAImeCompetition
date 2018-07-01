def check_name(name):
    errors = []
    bad_chars = []
    for char in name:
        if char in ';<>:"/\\\'|?*':
            if char not in bad_chars:
                bad_chars.append(char)
    for char in bad_chars:
        error = 'Character {0} is not allowed in your name.'.format(char)
        errors.append(error)
    if len(name) > 50:
        errors.append('Player names must be shorter than 50 characters.')
    return errors

def check_game_input(title, description, referee_code,
                     min_players, max_players):
    errors = []
    if title == '':
        errors.append('A game must have a name!')
    else:
        errors += check_name(title)
    if description == '':
        errors.append('A game must have a description!')
    if referee_code == '':
        errors.append('A game must have a referee attached.')
    try:
        if int(min_players) > int(max_players):
            errors.append('Max players must be higher than min players!')
    except Exception as e:
        errors.append('You must choose a minimum and maximum number of players.')
    return errors


def check_player_input(name, code, game):
    errors = []
    if name == '':
        errors.append('Your player must have a name!')
    else:
        errors += check_name(name)
    if code == '':
        errors.append('Your player must have some code!')
    if game == '':
        errors.append('Please choose a game.')
    return errors

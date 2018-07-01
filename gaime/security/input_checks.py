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

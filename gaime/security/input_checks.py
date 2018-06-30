def check_name(name):
    for char in name:
        if char in ';<>:"/\\\'|?*':
            error = 'Character {0} is not allowed in your name.'.format(char)
            return error
    return ''

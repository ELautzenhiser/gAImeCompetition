import subprocess
import sys
import os, errno
from datetime import datetime
from threading import Timer

def kill(*processes):
    for process in processes:
        process.kill()

def queryProcess(p, timeout = 1.0):
    """Gets one line of output from a process p.

    Warning: This function kills the process if no response within the
    alotted timeout period (Default: 1 second)
    """

    t = Timer(timeout, kill, [p])
    t.start()
    output = None
    output = p.stdout.readline()
    if not t.is_alive():
        raise TimeoutError('Process did not produce output in time.')
    t.cancel()
    output = output.rstrip()
    return output

def relay(num_lines, sender, *recipients, sender_name="", log_file=None):
    """Sends a message of length num_lines from sender to each recipient.

    Warning: If sender does not have output, the process is killed
    and a TimeoutError will be thrown

    Including log_file and sender_name will write the message to the log_file
    in the form

    sender_name: message
    """

    for i in range(num_lines):
        message = None
        message = queryProcess(sender, 2.0)
        for p in recipients:
            print(message, file=p.stdin)
            p.stdin.flush()
        if log_file:
            log_prefix = ""
            if sender_name:
                log_prefix = sender_name + ': '
            print(log_prefix + message, file=log_file)

def log_invalid_arg(log_file, arg, command=None):
    """Prints an invalid argument message to the log."""

    if log_file is None:
        return
    err_str = 'Invalid argument <{}>'.format(arg)
    if command is not None:
        err_str += ' in command: {}'.format(command)
    print(err_str, file=log_file)

def parse_args(command, players, log_file=None):
    """ Parse the arguments for either a SEND or LISTEN command.

    Returns a dictionary holding N, quiet, player_list, and player_nums.
    """

    args = command.split()[1:]
    player_list = []
    player_nums = []
    N = None
    quiet = False

    for arg in args:
        if arg[0] == 'P':
            p_num = None
            try:
                p_num = int(arg[1:])
            except ValueError:
                log_invalid_arg(log_file, arg, command)
                continue
            else:
                if 0 < p_num <= len(players):
                    player_list.append(players[p_num-1])
                    player_nums.append(p_num)
                else:
                    log_invalid_arg(log_file, arg, command)
            continue

        if arg == 'QUIET':
            quiet = True
            continue

        if N is None:
            try:
                N = int(arg)
            except ValueError:
                log_invalid_arg(log_file, arg, command)
            continue

        print('Error: superfluous argument <{}>'.format(arg)
              + ' in command: {}'.format(command),
              file = log_file)

    return {'N': N, 'quiet': quiet,
            'player_list': player_list,
            'player_nums': player_nums}

def run(outfile_dir, outfile_prefix, referee_cmd, *player_cmds):
    """The heart of manager.py.  Sets up connections between referee and
    players, and outputs anything necessary to a log_file.

    This function implements the commands that are available to the referee.
        SEND <N> [QUIET] [<players>]
            N: number of lines to send
            QUIET: specifies that message should not be sent to the log
            players: formatted P1, P2, P3 etc...
        LISTEN <N> [QUIET] <player>
            N: number of lines to get from player
            QUIET: specifies that message should not be sent to the log
            player: the player whose output is sent to referee
        GAMEOVER <scores>
            scores: WIN/LOSS or list of integers
                    there must be a value passed for each player

    Returns an integer:
        0 means no errors
        -1 means a timeout issue with the ref
        >0 means an issue with the corresponding player
    """

    try:
        os.makedirs(outfile_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e
    log_file = open(os.path.join(outfile_dir, outfile_prefix + 'log.txt'), 'w+')

    def log(s):
        """Helper function for logging to log_file."""
        print(s, file=log_file)

    try:
        ref = subprocess.Popen(
            referee_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True)
    except Exception as e:
        log(e)
        return -3, None

    players = []
    for cmd in player_cmds:
        try:
            players.append(subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True))
        except Exception as e:
            log("Failed to start running player " + str(i)
                  + " (" + cmd + "). Error:")
            log(e)
            kill(ref, *players)
            return -3, None

    print(len(players), file=ref.stdin)
    ref.stdin.flush()

    while True:
        try:
            ref_output = queryProcess(ref, 2.0)
        except TimeoutError:
            kill(ref, *players)
            return -1, None
        if not ref_output:
            log('\nNo output from ref.  This can be due to:\n'
                '    - ref output a blank line instead of a command\n'
                '    - ref program completed prematurely\n')
            kill(ref, *players)
            return -2, None

        # Commands are case-insensitive!
        ref_output = ref_output.upper()

        ref_cmd = ref_output.split()[0]

        if ref_cmd == 'SEND':
            arg_info = parse_args(ref_output, players, log_file)

            log_args = dict()
            if not arg_info['quiet']:
                log_args['sender_name'] = 'Referee'
                log_args['log_file'] = log_file

            try:
                relay(arg_info['N'], ref, *arg_info['player_list'], **log_args)
            except TimeoutError:
                kill(ref, *players)
                return -1, None

            continue

        if ref_cmd == 'LISTEN':
            arg_info = parse_args(ref_output, players, log_file)

            if not arg_info['player_list']:
                log('No player provided in command: {}'.format(ref_output))
                continue
            if len(arg_info['player_list']) > 1:
                log('Warning: more than one player provided.\n'
                    + 'Command: {}\n'.format(ref_output)
                    + 'Additional player args will be ignored.')

            player = arg_info['player_list'][0]

            log_args = dict()
            if not arg_info['quiet']:
                player_name = 'Player {}'.format(arg_info['player_nums'][0])
                log_args['sender_name'] = player_name
                log_args['log_file']=log_file

            try:
                relay(arg_info['N'], player, ref, **log_args)
            except TimeoutError:
                kill(ref, *players)
                return arg_info['player_nums'][0], None
            continue

        if ref_cmd == 'GAMEOVER':
            args = ref_output.split()[1:]
            log('Game Ended!')

            if len(args) != len(players):
                log('Error: Gameover arguments should match number of players.')
                log('    Command {}'.format(ref_output))
                log('    # players: {}'.format(len(players)))
                return -2, None
            else:
                results = []
                error = 0

                for i in range(len(args)):
                    log('Player {}: {}'.format(str(i+1), args[i]))
                    try:
                        score = int(args[i])
                    except ValueError:
                        if args[i] == 'WIN':
                            score = 1
                        elif args[i] == 'LOSE':
                            score = 0
                        else:
                            log_invalid_arg(log_file, args[i], ref_output)
                            error = -2
                            score = args[i]
                    results.append(score)

                kill(ref, *players)
                return error, results

        log("Invalid command: " + ref_output)

if __name__ == '__main__':
    files = sys.argv
    # assume they were all python scripts
    for i in range(len(files)):
        files[i] = ('python', files[i])

    ref_cmd = sys.argv[1]
    player_cmds = sys.argv[2:]

    date_str = datetime.now().strftime('%Y%b%d%H%M%S')

    error, results = run('manager_tests', date_str, ref_cmd, *player_cmds)

    print('Run function completed!')
    if results:
        print("Results:",results)

    if error > 0:
        print('Timeout error: Player {}'.format(error))
    if error == -1:
        print('Timeout Error: Referee')
    if error == -2:
        print('Referee returned results in incorrect format.')

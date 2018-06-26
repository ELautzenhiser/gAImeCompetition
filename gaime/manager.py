import subprocess
import sys
import os, errno
from datetime import datetime

def end_processes(*processes):
    pass

def run(outfile_dir, outfile_prefix, referee_cmd, *player_cmds):
    try:
        os.makedirs(outfile_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            print(e)

    log_file = open(os.path.join(outfile_dir, outfile_prefix + 'log.txt'), 'w+')

    def log(s):
        print(s, file=log_file)

    try:
        ref = subprocess.Popen(
            referee_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True)
    except Exception as e:
        print(e)
        return 3

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
            print("Failed to start running player " + str(i)
                  + " (" + cmd + "). Error:")
            print(e)
            continue

    if len(players) == 0:
        return 2

    print(len(players), file=ref.stdin)
    ref.stdin.flush()

    def invalid_argument(arg, cmd):
        log("Invalid argument <" + arg + "> in command: " + cmd)

    while True:
        ref_output = None
        try:
            ref_output = ref.stdout.readline()
            if not ref_output:
                return 1
        except Exception as e:
            print(e)
            return 1

        if ref_output[:4] == 'SEND':
            out_pipes = []
            args = ref_output.split()[1:]
            N = None
            for arg in args:
                arg = arg.upper()
                if arg[0] == 'P':
                    try:
                        arg = int(arg[1:])
                    except ValueError as e:
                        invalid_argument(arg, ref_output)
                        continue
                    if 0 <= arg < len(players):
                        out_pipes.append(players[arg].stdin)
                    continue
                if arg == 'LOG' or arg == 'L':
                    out_pipes.append(log_file)
                    continue
                try:
                    N = int(arg)
                except:
                    invalid_argument(arg, ref_output)
            if N is None or N == 0:
                continue
            for i in range(N):
                message = None
                try:
                    message = ref.stdout.readline()
                    if not message:
                        return 4
                except Exception as e:
                    print(e)
                    return 4
                for pipe in out_pipes:
                    print(message, file=pipe, end="")

            continue

        if ref_output[:6] == "LISTEN":
            arg = ref_output.split()[1]
            if arg[0] != 'P':
                invalid_argument(arg, ref_output)
                break

            p = None
            try:
                p = int(arg[1:])
            except:
                invalid_argument(arg, ref_output)
                break
            if p < 0 or p >= len(players):
                invalid_argument(arg, ref_output)
                break

            N = None
            try:
                N = int(ref_output.split()[2])
            except:
                invalid_argument(arg, ref_output)
                break

            for i in range(N):
                message = players[p].stdout.readline()
                print(message, file=ref.stdin, end="")

            continue

        if ref_output[:8] == 'GAMEOVER':
            args = ref_output.split()[1:]
            log('Game Ended!')
            for i in range(len(args)):
                log('Player ' + str(i) + ': ' + args[i])
            return 0

        log("Invalid command: " + ref_output)

if __name__ == '__main__':
    files = sys.argv
    # assume they were all python scripts
    for i in range(len(files)):
        files[i] = ('python', files[i])

    ref_cmd = sys.argv[1]
    player_cmds = sys.argv[2:]

    date_str = datetime.now().strftime('%Y%b%d%H%M%S')

    error = run('manager_tests', date_str, ref_cmd, *player_cmds)

    if error == 1:
        print("Referee stopped output without a gameover. Game ended.")
    if error == 2:
        print("No players were successfully opened.")
    if error == 3:
        print("Referee was not successfully initialized.")
    if error == 4:
        print("Incomplete message from ref.")

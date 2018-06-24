import subprocess
import sys
import os, errno
from datetime import datetime

def run(outfile_dir, outfile_prefix, referee_cmd, *player_cmds):
    try:
        os.makedirs(outfile_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    
    log_file = open(os.path.join(outfile_dir, outfile_prefix + 'log.txt'), 'w+')

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

    while True:
        ref_input = None
        try:
            ref_input = p.stdout.readline()
            if not line:
                break
        except:
            return 1
        print("REF: ", ref_input, file=log_file)
    
    


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

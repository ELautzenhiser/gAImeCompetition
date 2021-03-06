def log(m):
    print('SEND 1')
    print(m)

N = int(input())
if N != 2:
    log("Not the right number of players (" + str(N) + "). Should be two!")

num_rounds = 21

log("ROCK, PAPER, SCISSORS")
log("=====================")
log("Best to " + str(num_rounds) + "!")

def compare(a, b):
    a = a.upper()
    b = b.upper()
    rps = {'ROCK', 'PAPER', 'SCISSORS'}

    # make sure a and b had valid input. Punish invalid input!
    if a not in rps:
        if b not in rps:
            return 0
        return -1
    if b not in rps:
        return 1

    if a == 'ROCK' and b == 'PAPER':
        if b == 'PAPER':
            return -1
        if b == 'SCISSORS':
            return 1
    if a == 'PAPER':
        if b == 'ROCK':
            return 1
        if b == 'SCISSORS':
            return -1
    if a == 'SCISSORS':
        if b == 'ROCK':
            return -1
        if b == 'PAPER':
            return 1
    return 0

score1 = 0
score2 = 0

i = 0

while True:
    i += 1
    print('SEND P1 P2 1')
    print('Round ' + str(i))
    print('LISTEN P1 1')
    m1 = input()
    print('LISTEN P2 1')
    m2 = input()
    result = compare(m1, m2)
    if result < 0:
        score2 += 1
    elif result > 0:
        score1 += 1
    log('Round #' + str(i) + ': ' + m1 + ' ' + m2)

    if score1 > num_rounds / 2:
        print('SEND P1 P2 1')
        print('GAMEOVER')
        print('GAMEOVER WIN LOSE')
        break
    if score2 > num_rounds / 2:
        print('SEND P1 P2 1')
        print('GAMEOVER')
        print('GAMEOVER LOSE WIN')
        break

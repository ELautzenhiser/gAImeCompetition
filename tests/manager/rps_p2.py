rps = ['ROCK', 'PAPER', 'SCISSORS']

i = 0

while input()[:5] == 'Round':
    print(rps[i%2])
    i += 1
    while (True):
        i += 1

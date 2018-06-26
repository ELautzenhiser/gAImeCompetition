rps = ['ROCK', 'PAPER', 'SCISSORS']

i = 0

while input()[:5] == 'Round':
    print(rps[i%3])
    i += 1

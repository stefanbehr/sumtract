# Kathryn Nichols
# Stefan Behr
# LING 571
# Project 2

# Generates tiles for given file, w=40 and k=20

import nltk, sys

text = open(sys.argv[1]).read()
t = nltk.tokenize.TextTilingTokenizer(w=40, k=20)
tiles = t.tokenize(text)
index = 1

with open('tiles.txt', 'w') as f:
    for tile in tiles:
        print '*'*20 + ' TILE ' + str(index) + ' ' + '*'*20
        print tile
        index += 1

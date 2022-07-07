import string
import unidecode

alphabet = list(string.ascii_lowercase)

def processLines(inp):
    inp = inp.lower()
    inp = unidecode.unidecode(inp)

    output = []
    lines = inp.splitlines()
    for line in lines:
        if line != "":
            words = line.split()
            output.append(words)

    return output

def removePunctuation(inp):
    for i in range(0, len(inp)):
        for j in range(0, len(inp[i])):
            inp[i][j] = inp[i][j].translate(str.maketrans('', '', string.punctuation))
    return inp
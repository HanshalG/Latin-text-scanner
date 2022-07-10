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

            tokenised=[]

            for i in range(len(words)):
                words[i] = words[i].translate(str.maketrans('', '', string.punctuation))
                if words[i].endswith("que"):
                    tokenised.append(words[i][:-3])
                    tokenised.append("que")
                else:
                    tokenised.append(words[i])
            no_integers = [x for x in tokenised if not (x.isdigit()
                                                     or x[0] == '-' and x[1:].isdigit())]
            output.append(no_integers)

    return output

def removePunctuation(inp):
    for i in range(0, len(inp)):
        for j in range(0, len(inp[i])):
            inp[i][j] = inp[i][j].translate(str.maketrans('', '', string.punctuation))
    return inp
import string
import unidecode
import re

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
                elif words[i].endswith("ve"):
                    tokenised.append(words[i][:-2])
                    tokenised.append("ve")
                else:
                    tokenised.append(words[i])
            no_integers = [x for x in tokenised if not (x.isdigit()
                                                     or x[0] == '-' and x[1:].isdigit())]
            output.append(no_integers)

    return output

def processLinesSentence(inp):
    inp = inp.lower()
    inp = unidecode.unidecode(inp)

    output = []
    inp = inp.replace(";",".")
    lines = inp.split(".")

    for line in lines:
        if line != "":
            words = line.split()

            tokenised=[]

            for i in range(len(words)):
                words[i] = words[i].translate(str.maketrans('', '', string.punctuation))
                if words[i].endswith("que"):
                    tokenised.append(words[i][:-3])
                    tokenised.append("que")
                elif words[i].endswith("ve"):
                    tokenised.append(words[i][:-2])
                    tokenised.append("ve")
                else:
                    tokenised.append(words[i])
            no_integers = [x for x in tokenised if not (x.isdigit()
                                                     or x[0] == '-' and x[1:].isdigit())]
            output.append(no_integers)

    for i in range(len(output)):
        if output[i] == []:
           output.pop(i)

    return output

def removePunctuation(inp):
    for i in range(0, len(inp)):
        for j in range(0, len(inp[i])):
            inp[i][j] = inp[i][j].translate(str.maketrans('', '', string.punctuation))
    return inp

def convertLinesIndexToWordsIndex(inp, processed):
    #inp [i,j]
    x = 0
    for i in range(len(processed)):
        for j in range((processed[i])):
            if inp == [i,j]:
                return x
            x+=1
    return None

def convertWordsIndextoLinesIndex(inp, processed):

    x = 0

    for i in range(len(processed)):
        for j in range(len(processed[i])):
            if inp == x:
                return [i, j]
            x += 1

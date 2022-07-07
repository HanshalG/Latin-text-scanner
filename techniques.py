import string

#finds enjambements by scanning the first word
def enjambement(inp):

    output = []

    for i in range(0, len(inp)):
        if inp[i][0].endswith(',') or inp[i][0].endswith('.'):
            output.append([[i], "enjambement", inp[i][0].translate(str.maketrans('', '', string.punctuation))])

    return output

def alliteration(inp):

    output = []

    for i in range(0, len(inp)):
        #if previous word is part of an alliteration
        allit = False
        phrase = []

        #loop through every word in the line
        for j in range(1, len(inp[i])):
            #if current starting letter equal previous starting letter
            if inp[i][j][0] == inp[i][j-1][0]:
                if allit:
                    phrase.append(inp[i][j])
                else:
                    phrase.append(inp[i][j - 1])
                    phrase.append(inp[i][j])
                    allit = True
            #alliteration has ended
            elif allit == True:
                output.append([[i], "alliteration", phrase])
                phrase = []
                allit = False
        #newline
        #print("line scanned")

    return output

def metonymy(inp, metWords):

    output = []

    for i in range(0, len(inp)):
        for j in range(0, len(inp[i])):
            for word in metWords:
                if inp[i][j] == word:
                    output.append([[i], "metonymy", inp[i][j]])

    return output

def simile(inp, simileWords):

    output = []

    for i in range(0, len(inp)):
        for j in range(0, len(inp[i])):
            for word in simileWords:
                if inp[i][j] == word:
                    output.append([[i], "simile", inp[i][j]])

    return output
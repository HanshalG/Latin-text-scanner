import argparse

from pywebio.input import *
from pywebio.output import *
from pywebio import start_server
from processLines import processLines
from techniques import alliteration, enjambement
import latindictionary_io
from pywebio.session import set_env
#from scansion import scan_lines

def linesEntered(text):

    #parser = Parse()
    dictionary = latindictionary_io.Client()

    remove(scope="scopeMain")

    processedLines = processLines(text)
    alliterations = alliteration(processedLines)
    enjambements = enjambement(processedLines)
    techs = alliterations + enjambements
    #scannedLines = scan_lines(text)

    with use_scope("scopeRows"):

        put_processbar('translations', label="Scanning", auto_close=True)

        put_row([
            put_scrollable(put_scope("text", content=put_markdown(text)), height=500),
            put_scrollable(put_scope("techniques", content=put_text("placeholder")), height=500)
        ])

        put_button('Go back', onclick=goBack)

    with use_scope('techniques', clear=True):
        for i in range(len(processedLines)):
            put_collapse("Line {}".format(i + 1), content=put_scope("line{}".format(i)))

    linesWTechniques = []

    for t in techs:
        if t[0][0] not in linesWTechniques:
            put_markdown("### Possible Poetic Techniques", scope="line{}".format(t[0][0]))
            linesWTechniques.append(t[0][0])

        put_text("{0}: {1}".format(t[1], t[2]), scope="line{}".format(t[0][0]))

    totalWords = sum( [len(line) for line in processedLines])
    count = 0

    pofsForWord = [[[] for x in range(len(processedLines[y]))] for y in range(len(processedLines))]
    inflsForWord = [[[] for x in range(len(processedLines[y]))] for y in range(len(processedLines))]

    for i in range(len(processedLines)):
        for j in range(len(processedLines[i])):
            count +=1
            put_markdown("### " + processedLines[i][j], scope="line{}".format(i))
            try:
                data = dictionary.analyze_word(processedLines[i][j])
                for entry in data[0]:
                    grammarInfo = []

                    print(entry)

                    #print(type(entry['entry']['infl']))

                    if isinstance(entry['entry']['infl'], dict):
                        entry['entry']['infl'] = [entry['entry']['infl']]
                        #print("esffes")


                    for info in entry['entry']['infl']:

                        pofsForWord[i][j].append(info['pofs'])
                        inflsForWord[i][j].append(info)

                        #entry is noun format as case number declension
                        if info['pofs'] == 'noun':
                            grammarInfo.append("Noun: {0} {1} {2} Declension".format(info['case'], info['num'], info['decl']))
                        #verb  person number tense voice mood
                        elif info['pofs'] == 'verb':
                            try:
                                grammarInfo.append("Verb: {0} person {1} {2} {3} {4}".format(info['pers'], info['num'], info['tense'], info['voice'], info['mood']))
                            except Exception as e:
                                print(e)
                                if entry['entry']['dict']['kind'] == 'deponent':
                                    grammarInfo.append(
                                        "Verb: {0} person {1} {2} {3} {4}".format(info['pers'], info['num'],
                                                                                  info['tense'], "deponent",
                                                                                  info['mood']))

                            #add case if deponent(not transitive) (no mood)

                        #adjective   case gender number
                        elif info['pofs'] == 'adjective':
                            grammarInfo.append("Adjective: {0} {1} {2}".format(info['case'], info['gend'], info['num']))
                        #conjunction
                        #pronoun
                        #preposition
                        #verb participle
                        else:
                            grammarInfo.append("{}: {}".format(info['pofs'], info))


                    #print(grammarInfo)

                    outputString = "{}: {}, {}".format(processedLines[i][j], entry['word'], entry['entry']['mean'])

                    if grammarInfo != []:
                        for z in grammarInfo:
                            outputString += "\n- {}".format(str(z))

                    put_markdown(outputString,
                                 scope="line{}".format(i))

                #put_markdown(
                    #str(len(data[0])),
                    #scope="line{}".format(i))

            except Exception as e:
                print(e)
                pass

            set_processbar(name='translations', value=count/totalWords, label="Scanning")

    #print(pofsForWord, inflsForWord)

    #colour coding logic

    verbWords = identifyDefiniteVerbs(pofsForWord, inflsForWord)
    abldatWords = identifyDefiniteDativeAndAblatives(pofsForWord, inflsForWord)

    outputString =""

    clear("text")

    for i in range(len(processedLines)):
        for j in range(len(processedLines[i])):
            if [i,j] in verbWords:
                outputString += """<span style="color: #ff0000">{} </span>""".format(processedLines[i][j])
            elif [i,j] in abldatWords:
                outputString += """<span style="color: #FF00FF">{} </span>""".format(processedLines[i][j])
            else:
                outputString += processedLines[i][j] + " "

        put_html("""<p>{}
            </p>""".format(outputString), scope="text")
        outputString = ""


def goBack():
    remove("scopeRows")

    loadHomePage()




def startApp():

    set_env(title="Latin Poetry Scanner")

    put_markdown("# Latin Poetry Scanner")

    loadHomePage()

def loadHomePage():

    with use_scope("scopeMain"):
        put_markdown("""This is a latin poetry scanner
            It can provide translation, scansion and poetic technique suggestions to aid students to interpret latin verse more wholistically
            - Make sure to have line breaks inbetween lines
            - Techniques are just suggestions

            Translations from [latindictionary.io](https://www.latindictionary.io/)
            Scansion from latin-scansion""")
        put_markdown("Access latin lines from here: [Latin Library](https://www.thelatinlibrary.com/)")
        textBox = textarea(placeholder="Enter latin lines here: ", rows=10,
                           value="""Arma virumque canō, Trōiae quī prīmus ab ōrīs
Ītaliam, fātō profugus, Lāvīniaque vēnit
""")

    linesEntered(textBox)

def identifyDefiniteVerbs(pofInfo, inflsInfo):

    output = []

    for i in range(len(pofInfo)):
        for j in range(len(pofInfo[i])):
            if all(elem == "verb" for elem in pofInfo[i][j]) and pofInfo[i][j] != []:
                print("only verb", pofInfo[i][j])
                output.append([i,j])

    return output

def identifyDefiniteDativeAndAblatives(pofInfo, inflsInfo):

    output = []

    for i in range(len(pofInfo)):
        for j in range(len(pofInfo[i])):
            if all(elem == "noun" for elem in pofInfo[i][j]) and pofInfo[i][j] != []:
                if all(e['case'] in ['locative', 'dative', 'ablative'] for e in inflsInfo[i][j]):
                    output.append([i,j])

    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8080)
    args = parser.parse_args()
    start_server(startApp, port=args.port)


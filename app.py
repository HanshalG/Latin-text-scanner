from pywebio.input import *
from pywebio.output import *
from pywebio import platform
from processLines import processLines
from techniques import alliteration, enjambement
import latindictionary_io

def linesEntered(text):

    #parser = Parse()
    dictionary = latindictionary_io.Client()

    remove(scope="scopeMain")

    processedLines = processLines(text)
    alliterations = alliteration(processedLines)
    enjambements = enjambement(processedLines)
    techs = alliterations + enjambements

    with use_scope("scopeRows"):

        put_processbar('translations', label="Scanning", auto_close=True)

        put_row([
            put_scrollable(put_markdown("{}".format(text)), height=500),
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

    for i in range(len(processedLines)):
        for j in range(len(processedLines[i])):
            count +=1
            put_markdown("### " + processedLines[i][j], scope="line{}".format(i))
            try:
                data = dictionary.analyze_word(processedLines[i][j])
                for entry in data[0]:
                    grammarInfo = []

                    #print(entry)

                    #print(type(entry['entry']['infl']))

                    if isinstance(entry['entry']['infl'], dict):
                        entry['entry']['infl'] = [entry['entry']['infl']]
                        #print("esffes")


                    for info in entry['entry']['infl']:
                        #entry is noun format as case number declension
                        if info['pofs'] == 'noun':
                            grammarInfo.append("Noun: {0} {1} {2} Declension".format(info['case'], info['num'], info['decl']))
                        #verb  person number tense voice mood
                        elif info['pofs'] == 'verb':
                            grammarInfo.append("Verb: {0} person {1} {2} {3} {4}".format(info['pers'], info['num'], info['tense'], info['voice'], info['mood']))

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


def goBack():
    remove("scopeRows")

    loadHomePage()





def main():
    put_markdown("# Latin Poetry Scanner")

    loadHomePage()

def loadHomePage():
    with use_scope("scopeMain"):
        put_markdown("""This is a latin poetry scanner
            It can provide translation, scansion and poetic technique suggestions
            - Make sure to have line breaks inbetween lines
            - Techniques are just suggestions

            Translations from [latindictionary.io](https://www.latindictionary.io/)""")
        put_markdown("Access latin lines from here: [Latin Library](https://www.thelatinlibrary.com/)")
        textBox = textarea(placeholder="Enter latin lines here: ", rows=10,
                           value="""Arma virumque canō, Trōiae quī prīmus ab ōrīs
Ītaliam, fātō profugus, Lāvīniaque vēnit
lītora, multum ille et terrīs iactātus et altō
vī superum saevae memorem Iūnōnis ob īram;
multa quoque et bellō passus, dum conderet urbem,               5
inferretque deōs Latiō, genus unde Latīnum,
Albānīque patrēs, atque altae moenia Rōmae.

Mūsa, mihī causās memorā, quō nūmine laesō,
quidve dolēns, rēgīna deum tot volvere cāsūs
īnsīgnem pietāte virum, tot adīre labōrēs                                   10
impulerit. Tantaene animīs caelestibus īrae?

""")

    linesEntered(textBox)



if __name__ == "__main__":
    platform.tornado.start_server(main, port=8080, debug=False)
import argparse
import thelatinlibrary
import pywebio
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import put_select, put_slider, put_textarea
from pywebio import start_server
from processLines import processLines, convertWordsIndextoLinesIndex, convertLinesIndexToWordsIndex, processLinesSentence
from techniques import alliteration, enjambement
import latindictionary_io
from pywebio.session import set_env
from pywebio import session
#from scansion import scan_lines
from functools import partial
#from lamonpy import Lamon

js_file = "https://www.googletagmanager.com/gtag/js?id=G-21Q3SXV68D"
js_code = """
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());

gtag('config', 'G-21Q3SXV68D');
"""

aeneidLines = """Arma virumque canō, Trōiae quī prīmus ab ōrīs
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

Urbs antīqua fuit, Tyriī tenuēre colōnī,
Karthāgō, Ītaliam contrā Tiberīnaque longē
ōstia, dīves opum studiīsque asperrima bellī,
quam Iūnō fertur terrīs magis omnibus ūnam                           15
posthabitā coluisse Samō; hīc illius arma,
hīc currus fuit; hōc rēgnum dea gentibus esse,
sī quā Fāta sinant, iam tum tenditque fovetque.
Prōgeniem sed enim Trōiānō ā sanguine dūcī
audierat, Tyriās olim quae verteret arcēs;                                   20
"""

def linesEntered(text, radius, lineBreaks):

    #parser = Parse()
    dictionary = latindictionary_io.Client()
    #lamon = Lamon()
    remove(scope="scopeMain")

    if lineBreaks == "Line Breaks (Poetry)":
        processedLines = processLines(text)
    else:
        processedLines = processLinesSentence(text)
        #print(processedLines)
    alliterations = alliteration(processedLines)
    enjambements = enjambement(processedLines)
    techs = alliterations + enjambements
    #scannedLines = scan_lines(text)

    with use_scope("scopeRows"):

        put_processbar('translations', label="Scanning", auto_close=True).style("margin-bottom: 5px")

        put_row([
            put_scrollable(put_scope("text", content=put_markdown(text).style("line-height: 200%")), height=500),
            put_tabs([
                {'title': "Definitions", "content": put_scrollable(put_scope("techniques"), height=455).style("margin: -15px")},
                {'title': "Noun-Adj Agreements", "content": put_scrollable(put_scope("agreements"), height=455).style("margin: -15px")}
            ]).style("margin-top: 0px; height:500px")
        ])

        put_html("""<b>Colour coding: </b><span style="color: #ff0000">Verb </span> <span style="color: #B0C4DE">Conjunction </span> <span style="color: #0000FF">Preposition </span> <span style="color: #097969">Adverb </Span>""").style("padding-bottom:5px; float: left")


        put_button('Go back', onclick=goBack, small=True).style("float: right")

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
            #score, tagged = lamon.tag(processedLines[i][j])[0]
            #print(tagged)

            put_markdown("### " + processedLines[i][j], scope="line{}".format(i))

            #prediction from tagger
            #put_markdown("Prediction: {}".format(tagged[0][3]), scope="line{}".format(i))

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

                        pofsForWord[i][j].append(info['pofs'])
                        inflsForWord[i][j].append(info)

                        #entry is noun format as case number declension
                        if info['pofs'] == 'noun':
                            grammarInfo.append("Noun: **{0}** {1} {2} {3} Declension".format(info['case'], info['gend'], info['num'], info['decl']))
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
                            grammarInfo.append("Adjective: **{0}** {1} {2}".format(info['case'], info['gend'], info['num']))
                        #conjunction
                        elif info['pofs'] == 'conjunction':
                            grammarInfo.append("Conjunction")
                        #pronoun
                        elif info['pofs'] == 'pronoun':
                            grammarInfo.append("Pronoun: **{}** {} {}".format(info['case'], info['gend'], info['num']))
                        #preposition
                        elif info['pofs'] == "preposition":
                            grammarInfo.append("Preposition")
                        #verb participle
                        elif info['pofs'] == "verb participle":
                            grammarInfo.append("Verb Participle: {} **{}** {} {}".format(info['tense'], info['case'], info['gend'], info['num']))
                        else:
                            grammarInfo.append("{}: {}".format(info['pofs'], info))


                    #print(grammarInfo)

                    try:
                        outputString = "***{}***:\n{}".format(entry['entry']['dict']['hdwd'], entry['entry']['mean'])
                    except Exception as e:
                        print(e)
                        #FIX FOR DICT ENTRIES THAT HAVE A LIST, I THINK ITS DEPONENT VERBS
                        outputString = "***{}***:\n{}".format(processedLines[i][j], entry['entry']['mean'])

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
            #print(count, totalWords, count/totalWords)

    #print(pofsForWord, inflsForWord)

    #colour coding logic

    verbWords = identifyDefiniteVerbs(pofsForWord, inflsForWord)
    #abldatWords = identifyDefiniteDativeAndAblatives(pofsForWord, inflsForWord)
    conjunctionWords = identifyDefiniteConjunctions(pofsForWord, inflsForWord)
    prepositionWords = identifyDefinitePrepositions(pofsForWord, inflsForWord)
    adverbWords = identifyDefiniteAdverbs(pofsForWord, inflsForWord)

    pofsForWordNOLINES = [x for xs in pofsForWord for x in xs]
    inflsForWordNOLINES = [x for xs in inflsForWord for x in xs]
    wordsNOLINES = [x for xs in processedLines for x in xs]

    outputString ="1. "

    clear("text")

    for i in range(len(processedLines)):
        for j in range(len(processedLines[i])):
            if [i,j] in verbWords:
                outputString += """<span style="color: #ff0000">{} </span>""".format(processedLines[i][j])
            #elif [i,j] in abldatWords:
                #outputString += """<span style="color: #FF00FF">{} </span>""".format(processedLines[i][j])
            elif [i, j] in conjunctionWords:
                outputString += """<span style="color: #B0C4DE">{} </span>""".format(processedLines[i][j])
            elif [i,j] in prepositionWords:
                outputString += """<span style="color: #0000FF">{} </span>""".format(processedLines[i][j])
            elif [i,j] in adverbWords:
                outputString += """<span style="color: #097969">{} </span>""".format(processedLines[i][j])
            else:
                outputString += processedLines[i][j] + " "

        put_html("""<p>{}
            </p>""".format(outputString), scope="text").style("font-size:14px")
        #put_button("Line {}".format(i + 1), lambda : scroll_to(scope="line{}".format(i)), scope="text", small=True)
        outputString = "{}. ".format(i + 2)

    #put_html(" <br> <br> <b>Potential Noun-Adjective Agreements</b>", scope="scopeRows").style("float: none; font-size: 18px; margin-bottom: 10px")
    outputString = ""
    for i in range(totalWords):
        matches = nearbyMatches(inflsForWordNOLINES, radius, wordsNOLINES, i)
        indexMain = convertWordsIndextoLinesIndex(i, processedLines)
        if matches != []:
            outputString += "<b>" + str(wordsNOLINES[i]) + " (line {})</b>".format(indexMain[0] + 1)
            l = []
            for match in matches:
                indexTarget = convertWordsIndextoLinesIndex(match[0], processedLines)
                l.append(" - <b>{} (line {})</b>: {} {} {}".format(match[1], indexTarget[0] + 1, match[2]['case'], match[2]['gend'], match[2]['num']))

            outputString += "<br>" + "<br>".join(l)

            #print(outputString)

            put_html("""
            <div class="card" style="margin-bottom: 15px;">
              <div class="container">
                <p>{}</p>
              </div>
            </div>
                        """.format(outputString), scope="agreements").onclick(lambda: cardSelected())

            outputString =""


def goBack():
    remove("scopeRows")

    loadHomePage()




def startApp():
    set_env(title="Latin Helper - A Latin prose/poetry scanning tool", output_animation=False, output_max_width=1000)
    session.run_js('WebIO._state.CurrentSession.on_session_close(()=>{setTimeout(()=>location.reload(), 4000})')

    put_html("""<h1 style="font-weight: 280; font-size: 45px"><center><span style="font-weight:700">Latin</span><span>Helper</span></center></h1>""")

    loadHomePage()

def loadHomePage():

    #put_html("""
    #<button style="background:none; border:none;">arma</button> <button style="background:none; border:none;">virumque</button> <button style="background:none; border:none;">cano</button> """)
    #put_buttons(["arma", "virumque", "cano"], onclick=..., group=True, outline=True)

    with use_scope("scopeMain"):
        put_html(
            """
            <span style="color: #FF0000">Unfortunately latindictionary.io's API has been discontinued. Thus, LatinHelper is in the process of migrating to a new dictionary API, latinsimple. This means dictionary features are currently unavailable, apologies for the inconvenience. P.S Stay tuned for predictive parts of speech tagging integration in the next update </span>
            <br><br> This tool can provide <b>definitions, morphological information, possible noun-adjective agreements and basic poetic technique suggestions.</b> It is extremely helpful in aiding students to interpret and translate latin prose and view latin poetry more holistically. If you find the tool useful please share it with your fellow latin students!:) 
            <br><br>Website source-code: <a href="https://github.com/HanshalG/Latin-text-scanner" target="_blank">https://github.com/HanshalG/Latin-text-scanner</a>
            <br>Access latin works: <a href="https://www.thelatinlibrary.com/" target="_blank">Latin Library</a>
            <br>API for definitions and morphological information: <a href="https://www.latindictionary.io/" target="_blank">latindictionary.io</a>"""
        ).style("margin-bottom: 10px")

        put_row([
            put_scope("right"),
            put_scope("left")
        ])
        put_markdown(
            "**Text Seperation:** ",
            scope="left"
        ).style("padding-left: 20px")
        put_select("textSeperation", options=['Line Breaks (Poetry)', 'Full Stops (Prose)'], scope="left").style("width: 230px; padding-left: 20px")
        put_markdown(
            "**Search Radius For Noun-Adjective Agreements:** ",
            scope="left"
        ).style("padding-left: 20px")
        put_slider("searchRadius", value=5, min_value=2, max_value=15, scope="left").style("width: 250px; padding-left: 20px")
        put_markdown(
            "**Input Latin Text:** ",
            scope="right"
        )
        put_textarea("inputText", placeholder="Enter here: ", rows=10,
                           #value=aeneidLines,
                     scope="right").style("width: 550px")
        put_button("Submit", lambda : linesEntered(pywebio.pin.pin.inputText, pywebio.pin.pin.searchRadius, pywebio.pin.pin.textSeperation), scope="right")
        #put_button("Test Lines", lambda: linesEntered(aeneidLines, pywebio.pin.pin.searchRadius,
        #                                          pywebio.pin.pin.textSeperation), color="danger", scope="left", small=True).style("padding-left: 20px")
        #Make tabs dictionary
        authorList = [
            'virgil', 'caesar', 'augustus', 'cicero', 'gellius', 'livy', 'lucan', 'ovid', 'sallust', 'tacitus'
        ]

        authorsData = []

        tabsDicts = []
        for i in range(len(authorList)):
            author = thelatinlibrary.get_author_by_name(authorList[i])
            authorsData.append(author)
            tabsDicts.append({
                'title': author.name,
                'content': put_scope("{}".format(i))
            })

            #put_text("efsfes", scope="content0")
        '''
        put_html("<h3>Latin Library Text Selector (BETA)</h3>")

        put_tabs(tabsDicts)

        for i in range(len(authorsData)):
            for j in range(len(authorsData[i].works().sections)):
                #print(authorsData[i].works().sections[j].name)
                put_collapse(authorsData[i].works().sections[j].name, content=put_scope('{}{}'.format(i,j)), scope='{}'.format(i))

                for t in range(len(authorsData[i].works().sections[j].tomes)):
                    put_button(authorsData[i].works().sections[j].tomes[t].name, scope="{}{}".format(i,j), link_style=True, onclick=partial(linesEnteredLL, tome=authorsData[i].works().sections[j].tomes[t], sr=pywebio.pin.pin.searchRadius, ts=pywebio.pin.pin.textSeperation))
        '''
def identifyDefiniteVerbs(pofInfo, inflsInfo):

    output = []

    for i in range(len(pofInfo)):
        for j in range(len(pofInfo[i])):
            if all(elem == "verb" for elem in pofInfo[i][j]) and pofInfo[i][j] != []:
                output.append([i,j])

    return output

def identifyDefiniteConjunctions(pofInfo, inflsInfo):

    output = []

    for i in range(len(pofInfo)):
        for j in range(len(pofInfo[i])):
            if all(elem == "conjunction" for elem in pofInfo[i][j]) and pofInfo[i][j] != []:
                output.append([i,j])

    return output

def identifyDefinitePrepositions(pofInfo, inflsInfo):

    output = []

    for i in range(len(pofInfo)):
        for j in range(len(pofInfo[i])):
            if all(elem == "preposition" for elem in pofInfo[i][j]) and pofInfo[i][j] != []:
                output.append([i,j])

    return output

def identifyDefiniteAdverbs(pofInfo, inflsInfo):

    output = []

    for i in range(len(pofInfo)):
        for j in range(len(pofInfo[i])):
            if all(elem == "adverb" for elem in pofInfo[i][j]) and pofInfo[i][j] != []:
                output.append([i,j])

    return output

def identifyDefiniteDativeAndAblatives(pofInfo, inflsInfo):

    output = []

    for i in range(len(pofInfo)):
        for j in range(len(pofInfo[i])):
            if all(elem == "noun" for elem in pofInfo[i][j]) and pofInfo[i][j] != []:
                try:
                    if all(e['case'] in ['locative', 'dative', 'ablative'] for e in inflsInfo[i][j]):
                        output.append([i,j])
                except Exception as e:
                    print("error ", e, inflsInfo[i][j], [i,j])

    return output

def nearbyMatches(inflsInfo, searchRadius, words, targetIndex):

    #inputAsJustALiSt NOT LISTOFLISTS

    matches = []

    for i in range(-searchRadius, searchRadius):
        if targetIndex + i >= 0 and i != 0:
            try:
                for inflTarget in inflsInfo[targetIndex + i]:
                    for inflMain in inflsInfo[targetIndex]:
                        if (inflMain['pofs'] == 'noun' and inflTarget['pofs'] == 'adjective') or (inflMain['pofs'] == 'adjective' and inflTarget['pofs'] == 'noun'):
                            try:
                                if inflMain['case'] == inflTarget['case'] and inflMain['gend'] == inflTarget['gend'] and inflMain['num'] == inflTarget['num']:
                                    matches.append([targetIndex + i, words[targetIndex + i], {"case":inflMain['case'],
                                                                            "gend":inflMain['gend'],
                                                                            "num":inflMain['num']}])
                            except:
                                print("Noun doesn't have case,gender or number information")

            except IndexError:
                pass

    return matches

def cardSelected():
    return

def linesEnteredLL(tome, sr, ts):
    textJoined = ''.join(tome.text())
    print('fesfesf')
    print(textJoined)
    linesEntered(textJoined,sr,ts)


if __name__ == "__main__":

    pywebio.config(title="Latin Helper - A Latin prose/poetry scanning tool",
                   description="This tool can provide definitions, morphological information, possible noun-adjective agreements and basic poetic technique suggestions. It is extremely helpful in aiding students to interpret and translate latin prose and view latin poetry more holistically. If you find the tool useful please share it with your fellow latin students!:)",
                   css_style="""@import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');');
                       body{font-family: 'Roboto', sans-serif;};
                       """,
                   js_file=js_file,
                   js_code=js_code)

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8080)
    args = parser.parse_args()
    start_server(startApp, port=args.port, websocket_ping_interval=30)


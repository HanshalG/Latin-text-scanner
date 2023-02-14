from lamonpy import Lamon

lamon = Lamon()

score, tagged = lamon.tag("puella")[0]
print(tagged)
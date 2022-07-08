from cltk.prosody.lat.hexameter_scanner import HexameterScanner
import string

def scan_lines(lines):
    scanner = HexameterScanner()

    t = lines.maketrans('', '', string.punctuation)
    clean = lines.translate(t).lower()
    t = clean.maketrans('','', string.digits)
    noNumbers = clean.translate(t)

    clean_lines = noNumbers.splitlines()
    for i in range(len(clean_lines)):
        clean_lines[i] = clean_lines[i].strip()
    print(clean_lines)

    #macronizer = Macronizer('tag_ngram_123_backoff')

    output = []

    for line in clean_lines:
        v = scanner.scan(line)
        output.append([v.original, v.scansion])

    return outputScannedString(output)

def outputScannedString(scannedLines):

    output = ""

    for line in scannedLines:
        output += "{}\n{}\n".format(line[1], line[0])

    #print(output)

    return output
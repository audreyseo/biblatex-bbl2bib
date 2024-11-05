import sys
import os
import argparse
import re
from biblatex_bbl2bib.latex_command_parser import parse_command

def setupArgs():
    parser = argparse.ArgumentParser(prog="bbl2bib", description="Converts a biblatex-generated bbl file to .bib")
    parser.add_argument("--output", "-o", default=None, type=str, help="Name of the .bib file to output to. If not provided, will replace .bbl in the given file with .bib")
    parser.add_argument("bbl", type=str, help="Name of the input .bbl file.")

    return parser.parse_args()

def getFirstK(listy, k=1000):
    return listy[:min(len(listy), k)]

def printFirstKList(lol, k=1000):
    for l in lol:
        print(getFirstK(l, k))
        pass
    pass


def getEntries(sortlist):
    entries = [s.strip() for s in sortlist.split(r"\endentry")]
    printFirstKList(getFirstK(entries, k=10))
    return entries
    
def flattenLists(lol):
    if isinstance(lol, list):
        flattened = []
        for l in lol:
            f = flattenLists(l)
            if isinstance(f, list):
                flattened.extend(f)
                pass
            else:
                flattened.append(f)
                pass
            pass
        return flattened
    # it's not a list, so it's certainly not a list of lists
    return lol


def getSortLists(refsection):
    firstSortList = refsection.find(r"\sortlist")
    if firstSortList >= 0:
        firstnewline = refsection.find("\n", firstSortList)
        print(refsection[firstnewline:min(len(refsection), 1000)])
        sortlists = [s.strip() for s in refsection[firstnewline:].split(r"\endsortlist")]
        sortlists = [s for s in sortlists if s.startswith(r"\entry") or s.startswith(r"\sortlist")]
        parsedSortLists = []
        for s in sortlists:
            if s.startswith(r"\sortlist"):
                nextnewline = s.find("\n")
                parsedSortLists.append(s[nextnewline:])
                pass
            else:
                parsedSortLists.append(s)
                pass
            pass
        
        printFirstKList(parsedSortLists)
        
        return parsedSortLists
    return refsection


entryFieldsRe = re.compile(r"\\strng|\\field|\\range|\\verb|\\name")

simpleEntryFieldsRe = re.compile(r"\\strng|\\field|\\range")

verbRe = re.compile(r"\\verb\{([^}]*)\}\s*\\verb [^\n]*\s*\\endverb")

def parseNames(namesDict):
    # Parse raw output from parse_command

def parseName(entry):
    next = re.search(r"\\strng|\\field|\\range|\\verb|\\list", entry)
    names = ""
    if next:
        namesText = entry[:next.start()]
        print(parse_command(namesText))
        remaining = entry[next.start():].strip()
        pass
    return names, remaining

def splitByNextNewline(txt):
    newline = txt.find("\n")
    if newline >= 0:
        return txt[0:newline].strip(), txt[newline:].strip()
    return txt.strip(), ""

def parseSimpleEntryKey(entryLine):
    print("\"" + entryLine + "\"")
    entryLine = entryLine.strip()
    assert(len(entryLine) > 3)
    firstSlash = entryLine.find("\\")
    firstBracket = entryLine.find("{")
    if firstBracket > -1:
        middleBrackets = entryLine.find("}{", firstBracket)
        assert(entryLine.endswith("}"))
        return entryLine[firstSlash + 1:firstBracket], entryLine[firstBracket + 1:middleBrackets], entryLine[middleBrackets + 2:-1]
    pass


def parseSingleArg(entryLine):
    print("\"" + entryLine + "\"")
    entryLine = entryLine.strip()
    assert(len(entryLine) > 3)
    firstSlash = entryLine.find("\\")
    firstBracket = entryLine.find("{")
    assert(entryLine.endswith("}"))
    return entryLine[firstSlash + 1:firstBracket], entryLine[firstBracket + 1:-1]

def parseEntry(entry):
    # parsing an entry: \entry{Aitken1998}{article}{}
    entryMatch = re.match(r"\\entry\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}", entry)
    citation = {}
    remainingEntry = entry[len(entryMatch.group(0)):].strip()
    if entryMatch:
        citation["citationKey"] = entryMatch.group(1)
        citation["bibtype"] = entryMatch.group(2)
        pass
    while len(remainingEntry) > 0:
        if re.match(r"\\name\{author\}", remainingEntry):
            names, remainingEntry = parseName(remainingEntry)
            
            citation["author"] = names
            pass
        elif simpleEntryFieldsRe.match(remainingEntry):
            print("Remaining entry:", remainingEntry)
            firstLine, remainingEntry = splitByNextNewline(remainingEntry)
            keyType, keyName, value = parseSimpleEntryKey(firstLine)
            print(keyType, keyName, value)
            if keyType not in citation:
                citation[keyType] = {}
                pass
            citation[keyType][keyName] = value
            pass
        elif verbRe.match(remainingEntry):
            verbKeyLine, remainingEntry = splitByNextNewline(remainingEntry)
            verbValueLine, remainingEntry = splitByNextNewline(remainingEntry)
            temp, remainingEntry = splitByNextNewline(remainingEntry)
            print(verbKeyLine, verbValueLine, temp)
            verbVerb, verbKey = parseSingleArg(verbKeyLine)
            assert(verbValueLine.startswith("\\verb "))
            assert(temp.startswith("\\endverb"))
            verbValue = verbValueLine[5:].strip()
            print(verbKey, verbValue)
            if "verb" not in citation:
                citation["verb"] = {}
                pass
            citation["verb"][verbKey] = verbValue
        else:
            remainingEntry = ""
        # elif re.match(r"\\field")
        pass
    
    print(citation)
    return citation
    

if __name__ == '__main__':
    args = setupArgs()

    bbl = args.bbl
    if not args.output:
        if bbl.endswith(".bbl"):
            output = bbl[:-4] + ".bib"
            pass
        else:
            output = bbl + ".bib"
            pass
        pass
    else:
        output = args.output
        pass

    print(bbl)
    print(output)
    
    if not os.path.exists(bbl):
        print(f"Error: could not find bbl file {bbl}")
        exit(1)
        pass
    
    with open(bbl, "r") as f:
        contents = f.read()
        pass
        
    print(contents[:min(len(contents), 1000)])
    print(r"\refsection")
    firstRefSection = contents.find(r"\refsection")
    print(firstRefSection)
    contents = contents[firstRefSection:]
    
    print(contents[:min(len(contents), 1000)])

    
    refsections = [s.strip() for s in contents.split(r"\endrefsection")]
    refsections = [s for s in refsections if s.startswith(r"\refsection")]
    print(len(refsections))
    
    
    sortlists = flattenLists([getSortLists(s) for s in refsections])
    
    entrylists = [getEntries(p) for p in sortlists]
    entries = flattenLists(entrylists)
    print(len(entries))
    
    parsedEntries = [parseEntry(e) for e in getFirstK(entries, k=10)]
    
    

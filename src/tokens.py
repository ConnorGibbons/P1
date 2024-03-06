import sys
import re
import gzip

def applyApostropheRule(token):
    return token.replace("'","").replace("’","")

def simpleTok(input):
    input = input.replace("\n"," ").replace("\t"," ")
    multiSpacePattern = re.compile(" +")
    consistenlySpaced = re.sub(multiSpacePattern, " ", input)
    splitOnSpace = consistenlySpaced.split(" ")
    retList = []
    for token in splitOnSpace:
        token = token.replace(" ","")
        if(token == ""):
            continue
        retList.append(token)
    print(retList)
    return retList


def isURL(token):
    if(token.startswith("http://") or token.startswith("https://")):
        return True
    else:
        return False
    
def isNumber(token):
    if(token.replace(".","").replace(",","").replace("+","").replace("-","").isdigit()):
        return True
    else:
        return False

def isAbbreviation(token):
    if((not isURL(token) and  not isNumber(token)) and ("." in token)):
        return True
    else:
        return False
    
def processHyphenated(token):
    split = token.split("-")
    retList = []
    for word in split:
        retList.append(applyApostropheRule(word).lower())
    retList.append(applyApostropheRule(token.replace("-","").lower()))
    return retList

def tokenShouldBeSplit(token):
    tokList = []
    for char in token:
        if(not char.isalnum() and char != "." and char != "-"):
            token = token.replace(char, " ")
    multiSpacePattern = re.compile(" +")
    consistenlySpaced = re.sub(multiSpacePattern, " ", token)
    tokList = consistenlySpaced.split(" ")
    tokList = list(filter(lambda x: x != "", tokList))
    if(len(tokList) == 1):
        return (False, [])
    else:
        return (True, list(map(lambda x: x.replace(" ",""),tokList)))

def applyRules(token):
    #print(f"Applying rules to {token}")
    if(isURL(token)): #Base case 1
        return token
    elif(isNumber(token)): #Base case 2
        return token
    elif("-" in token):
        retList = []
        for tok in token.split("-"):
            retList.append(applyRules(tok))
        retList.append(applyRules(token.replace("-","")))
        return retList
    token = applyApostropheRule(token)
    if(not tokenShouldBeSplit(token)[0]): #Base case 3
        token = ''.join(filter(lambda char: char.isalnum() or char == ".",token.lower()))
        if(isNumber(token)):
            return token
        else:
            return token.replace(".","")
    else: # more recursion :(
        retList = []
        for tok in tokenShouldBeSplit(token)[1]:
            retList.append(applyRules(tok))
        return retList
    
def listExpander(ls):
    if(isinstance(ls, str)):
        return ls
    retList = []
    for elem in ls:
        if(isinstance(elem, list)):
            retList.extend(listExpander(elem))
        else:
            retList.append(elem)
    return retList

def fancyTok(input):
    simplyTokenized = simpleTok(input)
    fancyTokenized = []
    for token in simplyTokenized:
        rulesApplied = applyRules(token)
        fancyTokenized.append((token, listExpander(rulesApplied)))
    return fancyTokenized


def tokenize(input, type = "simple"):
    if type == "simple":
        return simpleTok(input)
    elif type == "fancy":
        return fancyTok(input)
    else:
        return simpleTok(input)

def numToks(tokenizedFile):
    sum = 0
    for token in tokenizedFile:
        if(isinstance(token[1], list)):
            sum += len(token[1])
        else:
            sum += 1
    return sum

def stop(tokenizedFile):
    retTokens = []
    origSum = numToks(tokenizedFile)
    for token in tokenizedFile:
        if(isinstance(token[1], list)):
            retList = []
            for elem in token[1]:
                if(elem not in stopword_lst):
                    retList.append(elem)
            retTokens.append((token[0],retList))
        else:
            if(token[1] not in stopword_lst):
                retTokens.append((token[0],token[1]))
    finalSum = numToks(retTokens)
    print(f"Orig: {origSum}, Final: {finalSum} --> trimmed {origSum - finalSum} tokens")
    return retTokens

def porter1a(word):
    print(f"1a Word: {word}")
    if(word.endswith("sses")):
        return word[:-2]
    elif((word.endswith("ies")) or word.endswith("ied") and len(word) > 4):
        return word[:-2]
    elif((word.endswith("ies")) or word.endswith("ied") and len(word) <= 4):
        return word[:-1]
    elif(word.endswith("ss") or word.endswith("us")):
        return word
    elif(word.endswith("s")):
        trimmedWord = word[:-2]
        if((len(trimmedWord) >= 1) and ("a" in trimmedWord or "e" in trimmedWord or "i" in trimmedWord or "o" in trimmedWord or "u" in trimmedWord or "y" in trimmedWord)):
            return trimmedWord
        else:
            return word
    else: 
        return word
    
def porter1b(word):
    print(f"1b Word: {word}")
    if(word.endswith("eed") or word.endswith("eedly")):
        trimmedWord = word[:-3] if word.endswith("eed") else word[:-5]
        firstVowelIndex = firstIndex(trimmedWord, isVowel)
        if(firstVowelIndex == -1):
            return word
        firstConsonantAfterVowel = firstIndex(trimmedWord[firstVowelIndex:], isConsonant)
        if(firstConsonantAfterVowel >= 0):
            return word[:-1]
        return word
    elif(word.endswith("ed") or word.endswith("edly") or word.endswith("ing") or word.endswith("ingly")):
        trimmedWord = word[:-2] if word.endswith("ed") else (word[:-4] if word.endswith("edly") else (word[:-3] if word.endswith("ing") else word[:-5]))
        firstVowelIndex = firstIndex(trimmedWord, isVowel)
        if(firstVowelIndex == -1):
            return word
        if(trimmedWord.endswith("at") or trimmedWord.endswith("bl") or trimmedWord.endswith("iz") or isShort(trimmedWord)):
            return trimmedWord + "e"
        if(trimmedWord[-1] == trimmedWord[-2] and ((trimmedWord[-1] in ["b","d","f","g","m","n","p","r"]))):
            return trimmedWord[:-1]
        return word
    else:
        return word
    
def porter1c(word):
    print(f"1c Word: {word}")
    if(word.endswith("y")):
        if(isVowel(word[-2]) and len(word) > 2):
            return word[:-1] + "i"
    else:
        return word
    
def porterStem(word):
    return porter1c(porter1b(porter1a(word)))

def applyPorterStem(tokenizedFile):
    retTokens = []
    for token in tokenizedFile:
        if(isinstance(token[1], list)):
            retList = []
            for elem in token[1]:
                retList.append(porterStem(elem))
            retTokens.append((token[0],retList))
        else:
            retTokens.append((token[0],porterStem(token[1])))
    return retTokens
        
def isShort(string):
    if(isVowel(string[0]) and isConsonant(string[1]) and len(string) == 2):
        return True
    elif(firstIndex(string, isVowel) != -1 and firstIndex(string, isConsonant) == 0 and countPred(string[firstIndex(string, isVowel):], isConsonantModded) == 1):
        return True
    else:
        return False

def isVowel(char):
    return char in ["a","e","i","o","u"]

def isConsonant(char):
    return char.isalpha() and not isVowel(char)

def isConsonantModded(char):
    return char.isalpha() and not isVowel(char) and char != "w" and char != "x"

def firstIndex(word, pred):
    for i in range(len(word)):
        if(pred(word[i])):
            return i
    return -1

def countPred(word, pred):
    count = 0
    for char in word:
        if(pred(char)):
            count += 1
    return count

def strFromList(ls):
    if(isinstance(ls, str)):
        return " " + ls
    retStr = ""
    for elem in ls:
        retStr += " " + elem
    return retStr

# def stripNewlines(tokenizedFile):
#     retTokens = []
#     for token in tokenizedFile:
#         if(isinstance(token[1], list)):
#             retList = []
#             for elem in token[1]:
#                 retList.append(elem.replace("\n",""))
#             retTokens.append((token[0],retList))
#         else:
#             retTokens.append((token[0],token[1].replace("\n","")))
#     return retTokens

if __name__ == '__main__':
   # tokens inputFile.gz outPrefix tokenize stoplist stemming
    stopword_lst = ["a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
"has", "he", "in", "is", "it", "its", "of", "on", "that", "the", "to",
"was", "were", "with"]
    argv_len = len(sys.argv)
    inputFile = gzip.open(sys.argv[1]) if argv_len >= 2 else gzip.open("../P1-train.gz") 
    outputPrefix = sys.argv[2] if argv_len >= 3 else "../P1-train"
    tokenizeType = sys.argv[3] if argv_len >= 4 else "simple"
    stopList = (sys.argv[4] == "yesStop") if argv_len >= 5 else False
    stemming = (sys.argv[5] == "porterStem") if argv_len >= 5 else False

    tokenizedFile = tokenize(inputFile.read().decode('utf-8'),tokenizeType)
    tokensFile = open(outputPrefix + "-tokens.txt", "w+")
    heapsFile = open(outputPrefix + "-heaps.txt", "w+")
    statsFile = open(outputPrefix + "-stats.txt", "w+")
    allTokens = []

    # tokenizedFile = stripNewlines(tokenizedFile)

    for token in tokenizedFile: 
        if(isinstance(token[1], list)):
            allTokens.extend(token[1])
        else:
            allTokens.append(token[1])

    if(stopList):
        tokenizedFile = stop(tokenizedFile)
    if(stemming):
        tokenizedFile = applyPorterStem(tokenizedFile)

    for token in tokenizedFile:
        tokensFile.write(f"{token[0]}{strFromList(token[1])}\n")

    
    i = 0
    n = 1
    dupNum = 0
    strList = []
    seen = []
    for elem in allTokens:
        i += 1
        if(i % 10 == 0 and i!= 0):
            strList.append(f"{n*i} {(n*i)-dupNum}")
            i = 0
            n += 1
        if(elem in seen):
            dupNum += 1
        seen.append(elem)
    if(i != 0):
        strList.append(f"{(10*n)+i} {((10*n)+i)-dupNum}")
    for elem in strList:
        heapsFile.write(f"{elem}\n")

    tokenDict = {}
    for token in allTokens:
        if token in tokenDict:
            tokenDict[token] += 1
        else:
            tokenDict[token] = 1
    tokenDict = sorted(tokenDict.items(), key=lambda x: x[1], reverse=True)
    i2 = 0 
    for token in tokenDict:
        if(i2 == 100):
            break
        statsFile.write(f"{token[0]} {token[1]}\n")
        i2 += 1

    inputFile.close()
    

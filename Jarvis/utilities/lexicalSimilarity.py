# -*- coding: utf-8 -*-

def compareWord(targets, word, distancePenalty = 0):
    scores = list()
    for index, e in enumerate(targets):
        scores.append({"i": index, "s": scoreWord(e, word) + index*distancePenalty})
    scores = sorted(scores, key = lambda k: (k["s"]))
    return (scores[0]["i"], scores[0]["s"])

def scoreWord(target, word):
    lastIndex = -1
    score = 0
    notFound = 0
    found = 0
    target = list(target)
    for e in word:
        index = findLetter(target, e, lastIndex)
        if index == -1:
            notFound += 1
            continue
        elif index < lastIndex:
            score += (lastIndex - index) * 0.5
        lastIndex = max(index, lastIndex)
        found += 1
    score += notFound * 2
    score += (len(target) - found) * 1
    return score*1.0/len(target)

def findLetter(letters, l, index):
    try:
        indexOffset = letters.index(l, index + 1)
    except ValueError:
        letters.reverse()
        try:
            indexOffset = len(letters) - letters.index(l, len(letters) - index) - 1
        except ValueError:
            indexOffset = -1
    return indexOffset

def compareSentence(targets, sentence):
    scores = list()
    for index, e in enumerate(targets):
        score, indexList = scoreSentence(e, sentence)
        scores.append({"i": index, "s": score, "l": indexList})
    scores = sorted(scores, key = lambda k: (k["s"]))
    return (scores[0]["i"], scores[0]["s"], scores[0]["l"])

def scoreSentence(target, sentence, distancePenalty = 0, additionalTargetPenalty = 1, wordMatchPenalty = 0):
    lastIndex = -1
    score = 0
    notFound = 0
    found = 0
    indexList = list()
    target = target.split()
    sentence = sentence.split()
    for e in sentence:
        index, wordScore = findWord(target, e, lastIndex)
        if index == -1 or index in indexList:
            notFound += 1
            continue
        else:
            if index < lastIndex:
                score += (lastIndex - index) * 0.5
            else:
                score += (index - lastIndex - 1) * distancePenalty
            score += wordScore * wordMatchPenalty
            lastIndex = max(index, lastIndex)
            found += 1
            indexList.append(index)
    score += notFound * 2
    score += (len(target) - found) * additionalTargetPenalty
    return (score*1.0/len(target), indexList)

def findWord(words, w, index, distancePenalty = 0):
    index = min(len(words), max(index, -1))
    if index < len(words) - 1:
        indexOffset, relScore = compareWord(words[index + 1:], w, distancePenalty)
        indexOffset += index + 1
    else:
        relScore = 2
    if relScore > 1:
        if index > 0:
            words = words[:index]
            words.reverse()
            indexOffset, relScore = compareWord(words, w, distancePenalty)
            indexOffset = index - indexOffset - 1
        else:
            relScore = 2
        if relScore > 1:
            indexOffset = -1
    return (indexOffset, relScore)

def findTrigger(string, trigger):
    index, score = findWord(string.split(), trigger, -1, 0.5)
    return index


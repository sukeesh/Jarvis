# -*- coding: utf-8 -*-

def compareWord(targets, word, distancePenalty = 0):
    """
    Select the best matching word out of a list of targets.

    :param targets: A list of words from which the best match is chosen
    :param word: Word to compare with
    :param distancePenalty: A Penalty that is applied to the normalized similarity score.
        It is the product of index in the target array and the given value. This can be
        used to find triggers at the beginning of a sentence.
    :return: Tuple of the index of the best match and the calculated score for this word.
    """
    scores = list()
    for index, e in enumerate(targets):
        scores.append({"i": index, "s": scoreWord(e, word) + index*distancePenalty})
    scores = sorted(scores, key = lambda k: (k["s"]))
    if len(scores) == 0:
        return (-1, -1)
    else:
        return (scores[0]["i"], scores[0]["s"])

def scoreWord(target, word):
    """
    Generate a score reflecting the similarity between a target and a given word.

    Beginning with the first letter search for occurrences of the letters
    in the target word. When a letter is missing in either the target word
    or given word or an occurence is before a previous occurrence of a
    different letter, a penalty score is increased.
    The result is normalized by the wordlength of the given word.

    A perfect match results in a score of 0. A good partial match results in
    a score less then one. For moderate strictness a score between 0.5 and 1.0
    should be used.

    :return: The normalized penalty score
    """
    lastIndex = -1
    score = 0
    notFound = 0
    word = word.lower()
    target = list(target.lower())
    indexList = list()
    for e in word:
        index = findLetter(target, e, lastIndex)
        if index == -1 or index in indexList:
            notFound += 1
            continue
        elif index < lastIndex:
            score += (lastIndex - index) * 0.5
        indexList.append(index)
        lastIndex = max(index, lastIndex)
    score += notFound * 2
    score += (len(target) - len(indexList)) * 1
    return score*1.0/len(word)

def findLetter(letters, l, index):
    """
    Find the first occurrence of a letter in a word after a given index.

    Searches forward in the word after index-th letter. If no matching letter is found,
    search backwards for the latest occurrence before the index-th letter.

    :return: index of the found occurrence, otherwise -1
    """
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
    """
    Select the best matching sentence out of a list of targets.

    :param targets: List of sentences
    :param sentence: Sentence to be found
    :return: Triple of the index of the best match, score for that
        match and list of used words (as indices) from the target
    """
    scores = list()
    for index, e in enumerate(targets):
        score, indexList = scoreSentence(e, sentence)
        scores.append({"i": index, "s": score, "l": indexList})
    scores = sorted(scores, key = lambda k: (k["s"]))
    return (scores[0]["i"], scores[0]["s"], scores[0]["l"])

def scoreSentence(target, sentence, distancePenalty = 0, additionalTargetPenalty = 1, wordMatchPenalty = 0):
    """
    Generate a score reflecting the similarity between a target and a given sentence.

    Search for matching words and compose a score of penalties.
    Compare to scoreWord() for a stripped down version of the algorithm.

    :param target: Sentence to compare to
    :param sentence: Sentence to be compared
    :param distancePenalty: Penalty for skipping words
    :param additionalTargetPenalty: Penalty for unmatched words in the target
    :param wordMatchPenalty: Modifier to be applied to the raw word scores
    :return: Tuple of normalized score and a list of words used from the
        target that are matched
    """
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
        elif index < lastIndex:
            score += (lastIndex - index) * 0.5
        else:
            score += (index - lastIndex - 1) * distancePenalty
        score += wordScore * wordMatchPenalty
        lastIndex = max(index, lastIndex)
        found += 1
        indexList.append(index)
    score += notFound * 2
    score += (len(target) - found) * additionalTargetPenalty
    return (score*1.0/len(sentence), indexList)

def findWord(words, w, index, distancePenalty = 0):
    """
    Find the first occurrence of a word in a sentence after a given word.

    Searches forward and if no match is found backward around the index-th
    word in the sentence.

    :param words: List of words that should be searched
    :param w: Word to be searched for
    :param index: Position in the array at which the search begins
    :param distancePenalty: Penalty applied to find the first best matching
        word in the targets. See compareWord() for more information
    :return: Tuple of index and score for the best matching word
    """
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
    """
    Find the best matching word at the beginning of a sentence.
    """
    index, score = findWord(string.split(), trigger, -1, 0.5)
    return index


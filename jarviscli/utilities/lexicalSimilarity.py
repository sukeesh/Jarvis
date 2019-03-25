# -*- coding: utf-8 -*-


def compare_word(targets, word, distance_penalty=0.0):
    """
    Select the best matching word out of a list of targets.

    :param targets: A list of words from which the best match is chosen
    :param word: Word to compare with
    :param distance_penalty: A Penalty that is applied to the normalized similarity score.
        It is the product of index in the target array and the given value. This can be
        used to find triggers at the beginning of a sentence.
    :return: Tuple of the index of the best match and the calculated score for this word.
    """
    scores = list()
    for index, e in enumerate(targets):
        scores.append({"i": index, "s": score_word(
            e, word) + index * distance_penalty})
    scores = sorted(scores, key=lambda k: (k["s"]))
    if not scores:
        return -1, -1
    else:
        return scores[0]["i"], scores[0]["s"]


def score_word(target, word):
    """
    Generate a score reflecting the similarity between a target and a given word.

    Beginning with the first letter search for occurrences of the letters
    in the target word. When a letter is missing in either the target word
    or given word or an occurrence is before a previous occurrence of a
    different letter, a penalty score is increased.
    The result is normalized by the word length of the given word.

    A perfect match results in a score of 0. A good partial match results in
    a score less then one. For moderate strictness a score between 0.5 and 1.0
    should be used.

    :return: The normalized penalty score
    """
    last_index = -1
    score = 0
    not_found = 0
    word = word.lower()
    target = list(target.lower())
    index_list = list()
    for e in word:
        index = find_letter(target, e, last_index)
        if index == -1 or index in index_list:
            not_found += 1
            continue
        elif index < last_index:
            score += (last_index - index) * 0.5
        index_list.append(index)
        last_index = max(index, last_index)
    score += not_found * 2
    score += (len(target) - len(index_list)) * 1
    return score * 1.0 / len(word)


def find_letter(letters, l, index):
    """
    Find the first occurrence of a letter in a word after a given index.

    Searches forward in the word after index-th letter. If no matching letter is found,
    search backwards for the latest occurrence before the index-th letter.

    :return: index of the found occurrence, otherwise -1
    """
    try:
        index_offset = letters.index(l, index + 1)
    except ValueError:
        letters.reverse()
        try:
            index_offset = len(letters) - letters.index(l,
                                                        len(letters) - index) - 1
        except ValueError:
            index_offset = -1
    return index_offset


def compare_sentence(targets, sentence):
    """
    Select the best matching sentence out of a list of targets.

    :param targets: List of sentences
    :param sentence: Sentence to be found
    :return: Triple of the index of the best match, score for that
        match and list of used words (as indices) from the target
    """
    scores = list()
    for index, e in enumerate(targets):
        score, index_list = score_sentence(e, sentence)
        scores.append({"i": index, "s": score, "l": index_list})
    scores = sorted(scores, key=lambda k: (k["s"]))
    return scores[0]["i"], scores[0]["s"], scores[0]["l"]


def score_sentence(target, sentence, distance_penalty=0,
                   additional_target_penalty=1, word_match_penalty=0):
    """
    Generate a score reflecting the similarity between a target and a given sentence.

    Search for matching words and compose a score of penalties.
    Compare to scoreWord() for a stripped down version of the algorithm.

    :param target: Sentence to compare to
    :param sentence: Sentence to be compared
    :param distance_penalty: Penalty for skipping words
    :param additional_target_penalty: Penalty for unmatched words in the target
    :param word_match_penalty: Modifier to be applied to the raw word scores
    :return: Tuple of normalized score and a list of words used from the
        target that are matched
    """
    last_index = -1
    score = 0
    not_found = 0
    found = 0
    index_list = list()
    target = target.split()
    sentence = sentence.split()
    for e in sentence:
        index, word_score = find_word(target, e, last_index)
        if index == -1 or index in index_list:
            not_found += 1
            continue
        elif index < last_index:
            score += (last_index - index) * 0.5
        else:
            score += (index - last_index - 1) * distance_penalty
        score += word_score * word_match_penalty
        last_index = max(index, last_index)
        found += 1
        index_list.append(index)
    score += not_found * 2
    score += (len(target) - found) * additional_target_penalty
    return score * 1.0 / len(sentence), index_list


def find_word(words, w, index, distance_penalty=0.0):
    """
    Find the first occurrence of a word in a sentence after a given word.

    Searches forward and if no match is found backward around the index-th
    word in the sentence.

    :param words: List of words that should be searched
    :param w: Word to be searched for
    :param index: Position in the array at which the search begins
    :param distance_penalty: Penalty applied to find the first best matching
        word in the targets. See compareWord() for more information
    :return: Tuple of index and score for the best matching word
    """
    index = min(len(words), max(index, -1))
    index_offset = -1
    if index < len(words) - 1:
        index_offset, rel_score = compare_word(
            words[index + 1:], w, distance_penalty)
        index_offset += index + 1
    else:
        rel_score = 2
    if rel_score > 1:
        if index > 0:
            words = words[:index]
            words.reverse()
            index_offset, rel_score = compare_word(words, w, distance_penalty)
            index_offset = index - index_offset - 1
        else:
            rel_score = 2
        if rel_score > 1:
            index_offset = -1
    return index_offset, rel_score


def find_trigger(string, trigger):
    """
    Find the best matching word at the beginning of a sentence.
    """
    index, score = find_word(string.split(), trigger, -1, 0.5)
    return index

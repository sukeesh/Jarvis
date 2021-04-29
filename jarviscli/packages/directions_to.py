from . import mapps


def main(data):
    """
    Extracts the names of start(if given) and destination cities,
    from the given argument.

    Parameters
    ----------
    data: str
        A variable that contains the names of start(if given) and
        destination cities.
    """
    word_list = data.split()
    to_index = word_list.index("to")
    if "from" in word_list:
        from_index = word_list.index("from")
        if from_index > to_index:
            to_city = " ".join(word_list[to_index + 1:from_index])
            from_city = " ".join(word_list[from_index + 1:])
        else:
            from_city = " ".join(word_list[from_index + 1:to_index])
            to_city = " ".join(word_list[to_index + 1:])
    else:
        to_city = " ".join(word_list[to_index + 1:])
        from_city = 0
    mapps.directions(to_city, from_city)

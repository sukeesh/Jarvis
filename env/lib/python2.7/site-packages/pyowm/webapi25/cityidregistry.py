from pyowm.webapi25.location import Location
from pyowm.abstractions.decorators import deprecated
from pkg_resources import resource_stream

"""
Module containing a registry with lookup methods for OWM-provided city IDs
"""


class CityIDRegistry:

    MATCHINGS = {
        'exact': lambda city_name, toponym: city_name == toponym,
        'nocase': lambda city_name, toponym: city_name.lower() == toponym.lower(),
        'like': lambda city_name, toponym: city_name.lower() in toponym.lower()
    }

    def __init__(self, filepath_regex):
        """
        Initialise a registry that can be used to lookup info about cities.

        :param filepath_regex: Python format string that gives the path of the files
               that store the city IDs information.
               Eg: ``folder1/folder2/%02d-%02d.txt``
        :type filepath_regex: str
        :returns: a *CityIDRegistry* instance

        """
        self._filepath_regex = filepath_regex

    @deprecated(will_be='removed', on_version=(3, 0, 0))
    def id_for(self, city_name):
        """
        Returns the long ID corresponding to the first city found that matches
        the provided city name. The lookup is case insensitive.

        .. deprecated:: 3.0.0
           Use :func:`ids_for` instead.

        :param city_name: the city name whose ID is looked up
        :type city_name: str
        :returns: a long or ``None`` if the lookup fails

        """
        line = self._lookup_line_by_city_name(city_name)
        return int(line.split(",")[1]) if line is not None else None

    def ids_for(self, city_name, country=None, matching='nocase'):
        """
        Returns a list of tuples in the form (long, str, str) corresponding to
        the int IDs and relative toponyms and 2-chars country of the cities
        matching the provided city name.
        The rule for identifying matchings is according to the provided
        `matching` parameter value.
        If `country` is provided, the search is restricted to the cities of
        the specified country.
        :param country: two character str representing the country where to
        search for the city. Defaults to `None`, which means: search in all
        countries.
        :param matching: str among `exact` (literal, case-sensitive matching),
        `nocase` (literal, case-insensitive matching) and `like` (matches cities
        whose name contains as a substring the string fed to the function, no
        matter the case). Defaults to `nocase`.
        :raises ValueError if the value for `matching` is unknown
        :return: list of tuples
        """
        if not city_name:
            return []
        if matching not in self.MATCHINGS:
            raise ValueError("Unknown type of matching: "
                             "allowed values are %s" % ", ".join(self.MATCHINGS))
        if country is not None and len(country) != 2:
            raise ValueError("Country must be a 2-char string")
        splits = self._filter_matching_lines(city_name, country, matching)
        return [(int(item[1]), item[0], item[4]) for item in splits]

    @deprecated(will_be='removed', on_version=(3, 0, 0))
    def location_for(self, city_name):
        """
        Returns the *Location* object corresponding to the first city found
        that matches the provided city name. The lookup is case insensitive.

        :param city_name: the city name you want a *Location* for
        :type city_name: str
        :returns: a *Location* instance or ``None`` if the lookup fails

        .. deprecated:: 3.0.0
           Use :func:`locations_for` instead.


        """
        line = self._lookup_line_by_city_name(city_name)
        if line is None:
            return None
        tokens = line.split(",")
        return Location(tokens[0], float(tokens[3]), float(tokens[2]),
                        int(tokens[1]), tokens[4])

    def locations_for(self, city_name, country=None, matching='nocase'):
        """
        Returns a list of Location objects corresponding to
        the int IDs and relative toponyms and 2-chars country of the cities
        matching the provided city name.
        The rule for identifying matchings is according to the provided
        `matching` parameter value.
        If `country` is provided, the search is restricted to the cities of
        the specified country.
        :param country: two character str representing the country where to
        search for the city. Defaults to `None`, which means: search in all
        countries.
        :param matching: str among `exact` (literal, case-sensitive matching),
        `nocase` (literal, case-insensitive matching) and `like` (matches cities
        whose name contains as a substring the string fed to the function, no
        matter the case). Defaults to `nocase`.
        :raises ValueError if the value for `matching` is unknown
        :return: list of `webapi25.location.Location` objects
        """
        if not city_name:
            return []
        if matching not in self.MATCHINGS:
            raise ValueError("Unknown type of matching: "
                             "allowed values are %s" % ", ".join(self.MATCHINGS))
        if country is not None and len(country) != 2:
            raise ValueError("Country must be a 2-char string")
        splits = self._filter_matching_lines(city_name, country, matching)
        return [Location(item[0], float(item[3]), float(item[2]),
                         int(item[1]), item[4]) for item in splits]

    # helper functions

    def _filter_matching_lines(self, city_name, country, matching):
        """
        Returns an iterable whose items are the lists of split tokens of every
        text line matched against the city ID files according to the provided
        combination of city_name, country and matching style
        :param city_name: str
        :param country: str or `None`
        :param matching: str
        :return: list of lists
        """
        result = list()

        # find the right file to scan and extract its lines. Upon "like"
        # matchings, just read all files
        if matching == 'like':
            lines = [l.strip() for l in self._get_all_lines()]
        else:
            filename = self._assess_subfile_from(city_name)
            lines = [l.strip() for l in self._get_lines(filename)]

        # look for toponyms matching the specified city_name and according to
        # the specified matching style
        for line in lines:
            tokens = line.split(",")
            # sometimes city names have an inner comma...
            if len(tokens) == 6:
                tokens = [tokens[0]+','+tokens[1], tokens[2], tokens[3],
                          tokens[4], tokens[5]]
            # check country
            if country is not None:
                if tokens[4] != country:
                    continue

            # check city_name
            if self._city_name_matches(city_name, tokens[0], matching):
                result.append(tokens)

        return result

    def _city_name_matches(self, city_name, toponym, matching):
        comparison_function = self.MATCHINGS[matching]
        return comparison_function(city_name, toponym)

    def _lookup_line_by_city_name(self, city_name):
        filename = self._assess_subfile_from(city_name)
        lines = self._get_lines(filename)
        return self._match_line(city_name, lines)

    def _assess_subfile_from(self, city_name):
        c = ord(city_name.lower()[0])
        if c < 97:  # not a letter
            raise ValueError('Error: city name must start with a letter')
        elif c in range(97, 103):  # from a to f
            return self._filepath_regex % (97, 102)
        elif c in range(103, 109):  # from g to l
            return self._filepath_regex % (103, 108)
        elif c in range(109, 115):  # from m to r
            return self._filepath_regex % (109, 114)
        elif c in range(115, 123):  # from s to z
            return self._filepath_regex % (115, 122)
        else:
            raise ValueError('Error: city name must start with a letter')

    def _get_lines(self, filename):
        with resource_stream(__name__, filename) as f:
            lines = f.readlines()
            if type(lines[0]) is bytes:
                lines = map(lambda l: l.decode("utf-8"), lines)
            return lines

    def _get_all_lines(self):
        all_lines = list()
        for city_name in ['a', 'g', 'm', 's']:  # all available city ID files
            filename = self._assess_subfile_from(city_name)
            all_lines.extend(self._get_lines(filename))
        return all_lines

    def _match_line(self, city_name, lines):
        """
        The lookup is case insensitive and returns the first matching line,
        stripped.
        :param city_name: str
        :param lines: list of str
        :return: str
        """
        for line in lines:
            toponym = line.split(',')[0]
            if toponym.lower() == city_name.lower():
                return line.strip()
        return None

    def __repr__(self):
        return "<%s.%s - filepath_regex=%s>" % (__name__, \
          self.__class__.__name__, self._filepath_regex)
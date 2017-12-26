"""This module implements the WordSub class, modelled after a recipe
in "Python Cookbook" (Recipe 3.14, "Replacing Multiple Patterns in a
Single Pass" by Xavier Defrang).

Usage:
Use this class like a dictionary to add before/after pairs:
    > subber = TextSub()
    > subber["before"] = "after"
    > subber["begin"] = "end"
Use the sub() method to perform the substitution:
    > print subber.sub("before we begin")
    after we end
All matching is intelligently case-insensitive:
    > print subber.sub("Before we BEGIN")
    After we END
The 'before' words must be complete words -- no prefixes.
The following example illustrates this point:
    > subber["he"] = "she"
    > print subber.sub("he says he'd like to help her")
    she says she'd like to help her
Note that "he" and "he'd" were replaced, but "help" and "her" were
not.
"""

# 'dict' objects weren't available to subclass from until version 2.2.
# Get around this by importing UserDict.UserDict if the built-in dict
# object isn't available.
try: dict
except: from UserDict import UserDict as dict

import ConfigParser
import re
import string

class WordSub(dict):
    """All-in-one multiple-string-substitution class."""

    def _wordToRegex(self, word):
        """Convert a word to a regex object which matches the word."""
        if word != "" and word[0].isalpha() and word[-1].isalpha():
            return "\\b%s\\b" % re.escape(word)
        else: 
            return r"\b%s\b" % re.escape(word)
    
    def _update_regex(self):
        """Build re object based on the keys of the current
        dictionary.

        """
        self._regex = re.compile("|".join(map(self._wordToRegex, self.keys())))
        self._regexIsDirty = False

    def __init__(self, defaults = {}):
        """Initialize the object, and populate it with the entries in
        the defaults dictionary.

        """
        self._regex = None
        self._regexIsDirty = True
        for k,v in defaults.items():
            self[k] = v

    def __call__(self, match):
        """Handler invoked for each regex match."""
        return self[match.group(0)]

    def __setitem__(self, i, y):
        self._regexIsDirty = True
        # for each entry the user adds, we actually add three entrys:
        super(type(self),self).__setitem__(string.lower(i),string.lower(y)) # key = value
        super(type(self),self).__setitem__(string.capwords(i), string.capwords(y)) # Key = Value
        super(type(self),self).__setitem__(string.upper(i), string.upper(y)) # KEY = VALUE

    def sub(self, text):
        """Translate text, returns the modified text."""
        if self._regexIsDirty:
            self._update_regex()
        return self._regex.sub(self, text)

# self-test
if __name__ == "__main__":
    subber = WordSub()
    subber["apple"] = "banana"
    subber["orange"] = "pear"
    subber["banana" ] = "apple"
    subber["he"] = "she"
    subber["I'd"] = "I would"

    # test case insensitivity
    inStr =  "I'd like one apple, one Orange and one BANANA."
    outStr = "I Would like one banana, one Pear and one APPLE."
    if subber.sub(inStr) == outStr: print "Test #1 PASSED"    
    else: print "Test #1 FAILED: '%s'" % subber.sub(inStr)

    inStr = "He said he'd like to go with me"
    outStr = "She said she'd like to go with me"
    if subber.sub(inStr) == outStr: print "Test #2 PASSED"    
    else: print "Test #2 FAILED: '%s'" % subber.sub(inStr)

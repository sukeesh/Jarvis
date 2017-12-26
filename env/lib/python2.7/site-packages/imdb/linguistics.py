"""
linguistics module (imdb package).

This module provides functions and data to handle in a smart way
languages and articles (in various languages) at the beginning of movie titles.

Copyright 2009-2012 Davide Alberani <da@erlug.linux.it>
          2012 Alberto Malagoli <albemala AT gmail.com>
          2009 H. Turgut Uyar <uyar@tekir.org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

# List of generic articles used when the language of the title is unknown (or
# we don't have information about articles in that language).
# XXX: Managing titles in a lot of different languages, a function to recognize
# an initial article can't be perfect; sometimes we'll stumble upon a short
# word that is an article in some language, but it's not in another; in these
# situations we have to choose if we want to interpret this little word
# as an article or not (remember that we don't know what the original language
# of the title was).
# Example: 'en' is (I suppose) an article in Some Language.  Unfortunately it
# seems also to be a preposition in other languages (French?).
# Running a script over the whole list of titles (and aliases), I've found
# that 'en' is used as an article only 376 times, and as another thing 594
# times, so I've decided to _always_ consider 'en' as a non article.
#
# Here is a list of words that are _never_ considered as articles, complete
# with the cound of times they are used in a way or another:
# 'en' (376 vs 594), 'to' (399 vs 727), 'as' (198 vs 276), 'et' (79 vs 99),
# 'des' (75 vs 150), 'al' (78 vs 304), 'ye' (14 vs 70),
# 'da' (23 vs 298), "'n" (8 vs 12)
#
# I've left in the list 'i' (1939 vs 2151) and 'uno' (52 vs 56)
# I'm not sure what '-al' is, and so I've left it out...
#
# Generic list of articles in utf-8 encoding:
GENERIC_ARTICLES = ('the', 'la', 'a', 'die', 'der', 'le', 'el',
            "l'", 'il', 'das', 'les', 'i', 'o', 'ein', 'un', 'de', 'los',
            'an', 'una', 'las', 'eine', 'den', 'het', 'gli', 'lo', 'os',
            'ang', 'oi', 'az', 'een', 'ha-', 'det', 'ta', 'al-',
            'mga', "un'", 'uno', 'ett', 'dem', 'egy', 'els', 'eines',
            '\xc3\x8f', '\xc3\x87', '\xc3\x94\xc3\xaf', '\xc3\x8f\xc3\xa9')


# Lists of articles separated by language.  If possible, the list should
# be sorted by frequency (not very important, but...)
# If you want to add a list of articles for another language, mail it
# it at imdbpy-devel@lists.sourceforge.net; non-ascii articles must be utf-8
# encoded.
LANG_ARTICLES = {
    'English': ('the', 'a', 'an'),
    'Italian': ('la', 'le', "l'", 'il', 'i', 'un', 'una', 'gli', 'lo', "un'",
                'uno'),
    'Spanish': ('la', 'lo', 'el', 'las', 'un', 'los', 'una', 'al', 'del',
                'unos', 'unas', 'uno'),
    'French': ('le', "l'", 'la', 'les', 'un', 'une', 'des', 'au', 'du', '\xc3\xa0 la',
                'de la', 'aux'),
    'Portuguese': ('a', 'as', 'o', 'os', 'um', 'uns', 'uma', 'umas'),
    'Turkish': (), # Some languages doesn't have articles.
}
LANG_ARTICLESget = LANG_ARTICLES.get


# Maps a language to countries where it is the main language.
# If you want to add an entry for another language or country, mail it at
# imdbpy-devel@lists.sourceforge.net .
LANG_COUNTRIES = {
    'English': ('Canada', 'Swaziland', 'Ghana', 'St. Lucia', 'Liberia', 'Jamaica', 'Bahamas', 'New Zealand', 'Lesotho', 'Kenya', 'Solomon Islands', 'United States', 'South Africa', 'St. Vincent and the Grenadines', 'Fiji', 'UK', 'Nigeria', 'Australia', 'USA', 'St. Kitts and Nevis', 'Belize', 'Sierra Leone', 'Gambia', 'Namibia', 'Micronesia', 'Kiribati', 'Grenada', 'Antigua and Barbuda', 'Barbados', 'Malta', 'Zimbabwe', 'Ireland', 'Uganda', 'Trinidad and Tobago', 'South Sudan', 'Guyana', 'Botswana', 'United Kingdom', 'Zambia'),
    'Italian': ('Italy', 'San Marino', 'Vatican City'),
    'Spanish': ('Spain', 'Mexico', 'Argentina', 'Bolivia', 'Guatemala', 'Uruguay', 'Peru', 'Cuba', 'Dominican Republic', 'Panama', 'Costa Rica', 'Ecuador', 'El Salvador', 'Chile', 'Equatorial Guinea', 'Spain', 'Colombia', 'Nicaragua', 'Venezuela', 'Honduras', 'Paraguay'),
    'French': ('Cameroon', 'Burkina Faso', 'Dominica', 'Gabon', 'Monaco', 'France', "Cote d'Ivoire", 'Benin', 'Togo', 'Central African Republic', 'Mali', 'Niger', 'Congo, Republic of', 'Guinea', 'Congo, Democratic Republic of the', 'Luxembourg', 'Haiti', 'Chad', 'Burundi', 'Madagascar', 'Comoros', 'Senegal'),
    'Portuguese': ('Portugal', 'Brazil', 'Sao Tome and Principe', 'Cape Verde', 'Angola',  'Mozambique', 'Guinea-Bissau'),
    'German': ('Liechtenstein', 'Austria', 'West Germany', 'Switzerland', 'East Germany', 'Germany'),
    'Arabic': ('Saudi Arabia', 'Kuwait', 'Jordan', 'Oman', 'Yemen', 'United Arab Emirates', 'Mauritania', 'Lebanon', 'Bahrain', 'Libya', 'Palestinian State (proposed)', 'Qatar', 'Algeria', 'Morocco', 'Iraq', 'Egypt', 'Djibouti', 'Sudan', 'Syria', 'Tunisia'),
    'Turkish': ('Turkey', 'Azerbaijan'),
    'Swahili': ('Tanzania',),
    'Swedish': ('Sweden',),
    'Icelandic': ('Iceland',),
    'Estonian': ('Estonia',),
    'Romanian': ('Romania',),
    'Samoan': ('Samoa',),
    'Slovenian': ('Slovenia',),
    'Tok Pisin': ('Papua New Guinea',),
    'Palauan': ('Palau',),
    'Macedonian': ('Macedonia',),
    'Hindi': ('India',),
    'Dutch': ('Netherlands', 'Belgium', 'Suriname'),
    'Marshallese': ('Marshall Islands',),
    'Korean': ('Korea, North', 'Korea, South', 'North Korea', 'South Korea'),
    'Vietnamese': ('Vietnam',),
    'Danish': ('Denmark',),
    'Khmer': ('Cambodia',),
    'Lao': ('Laos',),
    'Somali': ('Somalia',),
    'Filipino': ('Philippines',),
    'Hungarian': ('Hungary',),
    'Ukrainian': ('Ukraine',),
    'Bosnian': ('Bosnia and Herzegovina',),
    'Georgian': ('Georgia',),
    'Lithuanian': ('Lithuania',),
    'Malay': ('Brunei',),
    'Tetum': ('East Timor',),
    'Norwegian': ('Norway',),
    'Armenian': ('Armenia',),
    'Russian': ('Russia',),
    'Slovak': ('Slovakia',),
    'Thai': ('Thailand',),
    'Croatian': ('Croatia',),
    'Turkmen': ('Turkmenistan',),
    'Nepali': ('Nepal',),
    'Finnish': ('Finland',),
    'Uzbek': ('Uzbekistan',),
    'Albanian': ('Albania', 'Kosovo'),
    'Hebrew': ('Israel',),
    'Bulgarian': ('Bulgaria',),
    'Greek': ('Cyprus', 'Greece'),
    'Burmese': ('Myanmar',),
    'Latvian': ('Latvia',),
    'Serbian': ('Serbia',),
    'Afar': ('Eritrea',),
    'Catalan': ('Andorra',),
    'Chinese': ('China', 'Taiwan'),
    'Czech': ('Czech Republic', 'Czechoslovakia'),
    'Bislama': ('Vanuatu',),
    'Japanese': ('Japan',),
    'Kinyarwanda': ('Rwanda',),
    'Amharic': ('Ethiopia',),
    'Persian': ('Afghanistan', 'Iran'),
    'Tajik': ('Tajikistan',),
    'Mongolian': ('Mongolia',),
    'Dzongkha': ('Bhutan',),
    'Urdu': ('Pakistan',),
    'Polish': ('Poland',),
    'Sinhala': ('Sri Lanka',),
}

# Maps countries to their main language.
COUNTRY_LANG = {}
for lang in LANG_COUNTRIES:
    for country in LANG_COUNTRIES[lang]:
        COUNTRY_LANG[country] = lang


def toUnicode(articles):
    """Convert a list of articles utf-8 encoded to unicode strings."""
    return tuple([art.decode('utf_8') for art in articles])


def toDicts(articles):
    """Given a list of utf-8 encoded articles, build two dictionary (one
    utf-8 encoded and another one with unicode keys) for faster matches."""
    uArticles = toUnicode(articles)
    return dict([(x, x) for x in articles]), dict([(x, x) for x in uArticles])


def addTrailingSpace(articles):
    """From the given list of utf-8 encoded articles, return two
    lists (one utf-8 encoded and another one in unicode) where a space
    is added at the end - if the last char is not ' or -."""
    _spArticles = []
    _spUnicodeArticles = []
    for article in articles:
        if article[-1] not in ("'", '-'):
            article += ' '
        _spArticles.append(article)
        _spUnicodeArticles.append(article.decode('utf_8'))
    return _spArticles, _spUnicodeArticles


# Caches.
_ART_CACHE = {}
_SP_ART_CACHE = {}

def articlesDictsForLang(lang):
    """Return dictionaries of articles specific for the given language, or the
    default one if the language is not known."""
    if lang in _ART_CACHE:
        return _ART_CACHE[lang]
    artDicts = toDicts(LANG_ARTICLESget(lang, GENERIC_ARTICLES))
    _ART_CACHE[lang] = artDicts
    return artDicts


def spArticlesForLang(lang):
    """Return lists of articles (plus optional spaces) specific for the
    given language, or the default one if the language is not known."""
    if lang in _SP_ART_CACHE:
        return _SP_ART_CACHE[lang]
    spArticles = addTrailingSpace(LANG_ARTICLESget(lang, GENERIC_ARTICLES))
    _SP_ART_CACHE[lang] = spArticles
    return spArticles


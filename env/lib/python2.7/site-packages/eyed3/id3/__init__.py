################################################################################
#  Copyright (C) 2002-2012  Travis Shirk <travis@pobox.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
#
################################################################################
import string, re, types
import logging

from ..utils import requireUnicode
from ..utils.log import getLogger

log = getLogger(__name__)

# Version constants and helpers
ID3_V1              = (1, None, None)
'''Version 1, 1.0 or 1.1'''
ID3_V1_0            = (1, 0, 0)
'''Version 1.0, specifically'''
ID3_V1_1            = (1, 1, 0)
'''Version 1.1, specifically'''
ID3_V2              = (2, None, None)
'''Version 2, 2.2, 2.3 or 2.4'''
ID3_V2_2            = (2, 2, 0)
'''Version 2.2, specifically'''
ID3_V2_3            = (2, 3, 0)
'''Version 2.3, specifically'''
ID3_V2_4            = (2, 4, 0)
'''Version 2.4, specifically'''
ID3_DEFAULT_VERSION = ID3_V2_4
'''The default version for eyeD3 tags and save operations.'''
ID3_ANY_VERSION     = (ID3_V1[0] | ID3_V2[0], None, None)
'''Useful for operations where any version will suffice.'''

LATIN1_ENCODING   = b"\x00"
'''Byte code for latin1'''
UTF_16_ENCODING   = b"\x01"
'''Byte code for UTF-16'''
UTF_16BE_ENCODING = b"\x02"
'''Byte code for UTF-16 (big endian)'''
UTF_8_ENCODING    = b"\x03"
'''Byte code for UTF-8 (Not supported in ID3 versions < 2.4)'''

DEFAULT_LANG = b"eng"
'''Default language code for frames that contain a language portion.'''

def isValidVersion(v, fully_qualified=False):
    '''Check the tuple ``v`` against the list of valid ID3 version constants.
    If ``fully_qualified`` is ``True`` it is enforced that there are 3
    components to the version in ``v``. Returns ``True`` when valid and
    ``False`` otherwise.'''
    valid = v in [ID3_V1, ID3_V1_0, ID3_V1_1,
                  ID3_V2, ID3_V2_2, ID3_V2_3, ID3_V2_4,
                  ID3_ANY_VERSION]
    if not valid:
        return False

    if fully_qualified:
        return (None not in (v[0], v[1], v[2]))
    else:
        return True


def normalizeVersion(v):
    '''If version tuple ``v`` is of the non-specific type (v1 or v2, any, etc.)
    a fully qualified version is returned.'''
    if v == ID3_V1:
        v = ID3_V1_1
    elif v == ID3_V2:
        assert(ID3_DEFAULT_VERSION[0] & ID3_V2[0])
        v = ID3_DEFAULT_VERSION
    elif v == ID3_ANY_VERSION:
        v = ID3_DEFAULT_VERSION

    # Now, correct bogus version as seen in the wild
    if v[:2] == (2, 2) and v[2] != 0:
        v = (2, 2, 0)

    return v


## Convert an ID3 version constant to a display string
def versionToString(v):
    '''Conversion version tuple ``v`` to a string description.'''
    if v == ID3_ANY_VERSION:
       return "v1.x/v2.x"
    elif v[0] == 1:
       if v == ID3_V1_0:
          return "v1.0"
       elif v == ID3_V1_1:
          return "v1.1"
       elif v == ID3_V1:
          return "v1.x"
    elif v[0] == 2:
       if v == ID3_V2_2:
          return "v2.2"
       elif v == ID3_V2_3:
          return "v2.3"
       elif v == ID3_V2_4:
          return "v2.4"
       elif v == ID3_V2:
          return "v2.x"
    raise ValueError("Invalid ID3 version constant: %s" % str(v))


from .. import Error
class GenreException(Error):
    '''Excpetion type for exceptions related to genres.'''

class Genre(object):
    '''A genre in terms of a ``name`` and and ``id``. Only when ``name`` is
    a "standard" genre (as defined by ID3 v1) will ``id`` be a value other
    than ``None``.'''

    @requireUnicode("name")
    def __init__(self, name=None, id=None):
        '''Constructor takes an optional ``name`` and ``id``. If ``id`` is
        provided the ``name``, regardless of value, is set to the string the
        id maps to. Likewise, if ``name`` is passed and is a standard genre the
        ``id`` is set to the correct value. Any invalid id values cause a
        ``ValueError`` to be raised. Genre names that are not in the standard
        list are still accepted but the ``id`` value is set to ``None``.'''
        self.id, self.name = None, None
        if not name and id is None:
            return

        # An ID always takes precedence
        if id is not None:
            try:
                self.id = id
                # valid id will set name
                assert(self.name)
                if name and name != self.name:
                    log.warning("Genre ID takes precedence and remapped "
                                "'%s' to '%s'" % (name, self.name))
            except ValueError:
                log.warning("Invalid numeric genre ID: %d" % id)
                if not name:
                    # Gave an invalid ID and no name to fallback on
                    raise
                self.name = name
                self.id = None
        else:
            # All we have is a name
            self.name = name

        assert(self.id or self.name)


    @property
    def id(self):
        '''The Genre's id property.
        When setting the value is strictly enforced and if the value is not
        a valid genre code a ``ValueError`` is raised. Otherwise the id is
        set **and** the ``name`` property is updated to the code's string
        name.
        '''
        return self._id

    @id.setter
    def id(self, val):
        global genres

        if val is None:
            self._id = None
            return

        val = int(val)
        if val not in list(genres.keys()):
            raise ValueError("Invalid numeric genre ID: %d" % val)

        name = genres[val]
        self._id = val
        self._name = name

    @property
    def name(self):
        '''The Genre's name property.
        When setting the value the name is looked up in the standard genre
        map and if found the ``id`` ppropery is set to the numeric valud **and**
        the name is normalized to the sting found in the map. Non standard
        genres are set (with a warning log) and the ``id`` is set to ``None``.
        It is valid to set the value to ``None``.
        '''
        return self._name

    @name.setter
    @requireUnicode(1)
    def name(self, val):
        global genres
        if val is None:
            self._name = None
            return

        if val.lower() in list(genres.keys()):
            self._id = genres[val]
            # normalize the name
            self._name = genres[self._id]
        else:
            log.warning("Non standard genre name: %s" % val)
            self._id = None
            self._name = val

    ##
    # Parses genre information from \a genre_str.
    # The following formats are supported:
    # 01, 2, 23, 125 - ID3 v1.x style.
    # (01), (2), (129)Hardcore, (9)Metal, Indie - ID3 v2 style with and without
    #                                             refinement.
    #
    # \throws GenreException when an invalid string is passed.
    @staticmethod
    @requireUnicode(1)
    def parse(g_str):
        g_str = g_str.strip()
        if not g_str:
            return None

        def strip0Padding(s):
            if len(s) > 1:
                return s.lstrip("0")
            else:
                return s

        # ID3 v1 style.
        # Match 03, 34, 129.
        regex = re.compile("[0-9][0-9]*$")
        if regex.match(g_str):
            return Genre(id=int(strip0Padding(g_str)))

        # ID3 v2 style.
        # Match (03), (0)Blues, (15) Rap
        regex = re.compile("\(([0-9][0-9]*)\)(.*)$")
        m = regex.match(g_str)
        if m:
            (id, name) = m.groups()

            id = int(strip0Padding(id))
            if id and name:
                id = id
                name = name.strip()
            else:
                id = id
                name = None

            return Genre(id=id, name=name)

        # Let everything else slide, genres suck anyway
        return Genre(id=None, name=g_str)

    def __unicode__(self):
        s = u""
        if self.id != None:
           s += u"(%d)" % self.id
        if self.name:
           s += self.name
        return s

    def __eq__(self, rhs):
        return self.id == rhs.id and self.name == rhs.name

    def __ne__(self, rhs):
        return not self.__eq__(rhs)


class GenreMap(dict):
    '''Classic genres defined around ID3 v1 but suitable anywhere.  This class
    is used primarily as a way to map numeric genre values to a string name.
    Genre strings on the other hand are not required to exist in this list.
    '''
    GENRE_MIN = 0
    GENRE_MAX = None
    ID3_GENRE_MIN = 0
    ID3_GENRE_MAX = 79
    WINAMP_GENRE_MIN = 80
    WINAMP_GENRE_MAX = 147

    def __init__(self, *args):
        '''The optional ``*args`` are passed directly to the ``dict``
        constructor.'''
        global ID3_GENRES
        super(GenreMap, self).__init__(*args)

        # ID3 genres as defined by the v1.1 spec with WinAmp extensions.
        for i, g in enumerate(ID3_GENRES):
            self[i] = g
            self[g.lower()] = i

        GenreMap.GENRE_MAX = len(ID3_GENRES) - 1
        # Pad up to 255
        for i in range(GenreMap.GENRE_MAX + 1, 255 + 1):
            self[i] = u"<not-set>"
        self[u"<not-set>".lower()] = 255


    def __getitem__(self, key):
        if type(key) is not int:
            key = key.lower()
        return super(GenreMap, self).__getitem__(key)


from .. import core
class TagFile(core.AudioFile):
    '''
    A shim class for dealing with files that contain only ID3 data, no audio.
    '''
    def __init__(self, path, version=ID3_ANY_VERSION):
        self._tag_version = version
        core.AudioFile.__init__(self, path)
        assert(self.type == core.AUDIO_NONE)

    def _read(self):
        from .tag import Tag

        with file(self.path, 'rb') as file_obj:
            tag = Tag()
            tag_found = tag.parse(file_obj, self._tag_version)
            self._tag = tag if tag_found else None

        self.type = core.AUDIO_NONE

    def initTag(self, version=ID3_DEFAULT_VERSION):
        '''Add a id3.Tag to the file (removing any existing tag if one exists).
        '''
        from .tag import Tag, FileInfo
        self.tag = Tag()
        self.tag.version = version
        self.tag.file_info = FileInfo(self.path)


ID3_GENRES = [
u'Blues',
u'Classic Rock',
u'Country',
u'Dance',
u'Disco',
u'Funk',
u'Grunge',
u'Hip-Hop',
u'Jazz',
u'Metal',
u'New Age',
u'Oldies',
u'Other',
u'Pop',
u'R&B',
u'Rap',
u'Reggae',
u'Rock',
u'Techno',
u'Industrial',
u'Alternative',
u'Ska',
u'Death Metal',
u'Pranks',
u'Soundtrack',
u'Euro-Techno',
u'Ambient',
u'Trip-Hop',
u'Vocal',
u'Jazz+Funk',
u'Fusion',
u'Trance',
u'Classical',
u'Instrumental',
u'Acid',
u'House',
u'Game',
u'Sound Clip',
u'Gospel',
u'Noise',
u'AlternRock',
u'Bass',
u'Soul',
u'Punk',
u'Space',
u'Meditative',
u'Instrumental Pop',
u'Instrumental Rock',
u'Ethnic',
u'Gothic',
u'Darkwave',
u'Techno-Industrial',
u'Electronic',
u'Pop-Folk',
u'Eurodance',
u'Dream',
u'Southern Rock',
u'Comedy',
u'Cult',
u'Gangsta Rap',
u'Top 40',
u'Christian Rap',
u'Pop / Funk',
u'Jungle',
u'Native American',
u'Cabaret',
u'New Wave',
u'Psychedelic',
u'Rave',
u'Showtunes',
u'Trailer',
u'Lo-Fi',
u'Tribal',
u'Acid Punk',
u'Acid Jazz',
u'Polka',
u'Retro',
u'Musical',
u'Rock & Roll',
u'Hard Rock',
u'Folk',
u'Folk-Rock',
u'National Folk',
u'Swing',
u'Fast  Fusion',
u'Bebob',
u'Latin',
u'Revival',
u'Celtic',
u'Bluegrass',
u'Avantgarde',
u'Gothic Rock',
u'Progressive Rock',
u'Psychedelic Rock',
u'Symphonic Rock',
u'Slow Rock',
u'Big Band',
u'Chorus',
u'Easy Listening',
u'Acoustic',
u'Humour',
u'Speech',
u'Chanson',
u'Opera',
u'Chamber Music',
u'Sonata',
u'Symphony',
u'Booty Bass',
u'Primus',
u'Porn Groove',
u'Satire',
u'Slow Jam',
u'Club',
u'Tango',
u'Samba',
u'Folklore',
u'Ballad',
u'Power Ballad',
u'Rhythmic Soul',
u'Freestyle',
u'Duet',
u'Punk Rock',
u'Drum Solo',
u'A Cappella',
u'Euro-House',
u'Dance Hall',
u'Goa',
u'Drum & Bass',
u'Club-House',
u'Hardcore',
u'Terror',
u'Indie',
u'BritPop',
u'Negerpunk',
u'Polsk Punk',
u'Beat',
u'Christian Gangsta Rap',
u'Heavy Metal',
u'Black Metal',
u'Crossover',
u'Contemporary Christian',
u'Christian Rock',
u'Merengue',
u'Salsa',
u'Thrash Metal',
u'Anime',
u'JPop',
u'Synthpop',
u'Rock/Pop',
]
'''ID3 genres, as defined in ID3 v1. The position in the list is the genre's
numeric byte value.'''

from .tag import Tag, FileInfo, TagException, TagTemplate
genres = GenreMap()
'''A map of standard genre names and IDs per the ID3 v1 genre definition.'''

from . import frames

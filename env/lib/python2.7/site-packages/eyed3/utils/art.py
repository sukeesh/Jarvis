# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2014  Travis Shirk <travis@pobox.com>
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
from os.path import basename, splitext
from fnmatch import fnmatch
from ..id3.frames import ImageFrame


FRONT_COVER = "FRONT_COVER"
'''Album front cover.'''
BACK_COVER = "BACK_COVER"
'''Album back cover.'''
MISC_COVER = "MISC_COVER"
'''Other part of the album cover; liner notes, gate-fold, etc.'''
LOGO = "LOGO"
'''Artist/band logo.'''
ARTIST = "ARTIST"
'''Artist/band images.'''
LIVE = "LIVE"
'''Artist/band images.'''

FILENAMES = {
        FRONT_COVER: ["cover-front", "cover-alternate*", "cover",
                      "folder", "front", "cover-front_*", "flier"],
        BACK_COVER: ["cover-back", "back", "cover-back_*"],
        MISC_COVER: ["cover-insert*", "cover-liner*", "cover-disc",
                     "cover-media*"],
        LOGO: ["logo*"],
        ARTIST: ["artist*"],
        LIVE: ["live*"],
}
'''A mapping of art types to lists of filename patterns (excluding file
extension): type -> [file_pattern, ..].'''

TO_ID3_ART_TYPES = {
        FRONT_COVER: [ImageFrame.FRONT_COVER, ImageFrame.OTHER, ImageFrame.ICON,
                      ImageFrame.LEAFLET],
        BACK_COVER: [ImageFrame.BACK_COVER],
        MISC_COVER: [ImageFrame.MEDIA],
        LOGO: [ImageFrame.BAND_LOGO],
        ARTIST: [ImageFrame.LEAD_ARTIST, ImageFrame.ARTIST, ImageFrame.BAND],
        LIVE: [ImageFrame.DURING_PERFORMANCE, ImageFrame.DURING_RECORDING]
}
'''A mapping of art types to ID3 APIC (image) types: type -> [apic_type, ..]'''
# ID3 image types not mapped above:
#    OTHER_ICON          = 0x02
#    CONDUCTOR           = 0x09
#    COMPOSER            = 0x0B
#    LYRICIST            = 0x0C
#    RECORDING_LOCATION  = 0x0D
#    VIDEO               = 0x10
#    BRIGHT_COLORED_FISH = 0x11
#    ILLUSTRATION        = 0x12
#    PUBLISHER_LOGO      = 0x14

FROM_ID3_ART_TYPES = {}
'''A mapping of ID3 art types to eyeD3 art types; the opposite of
TO_ID3_ART_TYPES.'''
for _type in TO_ID3_ART_TYPES:
    for _id3_type in TO_ID3_ART_TYPES[_type]:
        FROM_ID3_ART_TYPES[_id3_type] = _type
del _type
del _id3_type


def matchArtFile(filename):
    '''Compares ``filename`` (case insensitive) with lists of common art file
    names and returns the type of art that was matched, or None if no types
    were matched.'''
    base = splitext(basename(filename))[0]
    for type_ in FILENAMES.keys():
        if True in [fnmatch(base.lower(), fname) for fname in FILENAMES[type_]]:
            return type_
    return None


def getArtFromTag(tag, type_=None):
    '''Returns a list of eyed3.id3.frames.ImageFrame objects matching ``type_``,
    all if ``type_`` is None, or empty if tag does not contain art.'''
    art = []
    for img in tag.images:
        if not type_ or type_ == img.picture_type:
            art.append(img)
    return art

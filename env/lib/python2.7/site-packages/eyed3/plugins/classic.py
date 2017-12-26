# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2007-2016  Travis Shirk <travis@pobox.com>
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
from __future__ import print_function

import os, stat, re
import warnings
from argparse import ArgumentTypeError, SUPPRESS

from eyed3 import LOCAL_ENCODING
from eyed3.plugins import LoaderPlugin
from eyed3 import core, id3, mp3, utils, compat
from eyed3.utils import makeUniqueFileName
from eyed3.utils.console import (printMsg, printError, printWarning, boldText,
                                 HEADER_COLOR, Fore)
from eyed3.id3.frames import ImageFrame

from ..utils.log import getLogger
log = getLogger(__name__)

FIELD_DELIM = ':'

DEFAULT_MAX_PADDING = 64*1024

class ClassicPlugin(LoaderPlugin):
    SUMMARY = u"Classic eyeD3 interface for viewing and editing tags."
    DESCRIPTION = u"""
All PATH arguments are parsed and displayed. Directory paths are searched
recursively. Any editing options (--artist, --title) are applied to each file
read.

All date options (-Y, --release-year excepted) follow ISO 8601 format. This is
``yyyy-mm-ddThh:mm:ss``. The year is required, and each component thereafter is
optional. For example, 2012-03 is valid, 2012--12 is not.
"""
    NAMES = ["classic"]

    def __init__(self, arg_parser):
        super(ClassicPlugin, self).__init__(arg_parser)
        g = self.arg_group

        def UnicodeArg(arg):
            return unicode(arg, LOCAL_ENCODING)

        def PositiveIntArg(i):
            i = int(i)
            if i < 0:
                raise ArgumentTypeError("positive number required")
            return i

        # Common options
        g.add_argument("-a", "--artist", type=UnicodeArg, dest="artist",
                       metavar="STRING", help=ARGS_HELP["--artist"])
        g.add_argument("-A", "--album", type=UnicodeArg, dest="album",
                       metavar="STRING", help=ARGS_HELP["--album"])
        g.add_argument("-b", "--album-artist", type=UnicodeArg,
                       dest="album_artist", metavar="STRING",
                       help=ARGS_HELP["--album-artist"])
        g.add_argument("-t", "--title", type=UnicodeArg, dest="title",
                       metavar="STRING", help=ARGS_HELP["--title"])
        g.add_argument("-n", "--track", type=PositiveIntArg, dest="track",
                       metavar="NUM", help=ARGS_HELP["--track"])
        g.add_argument("-N", "--track-total", type=PositiveIntArg,
                       dest="track_total", metavar="NUM",
                       help=ARGS_HELP["--track-total"])

        g.add_argument("--track-offset", type=int, dest="track_offset",
                       metavar="N", help=ARGS_HELP["--track-offset"])

        g.add_argument("-d", "--disc-num", type=PositiveIntArg, dest="disc_num",
                       metavar="NUM", help=ARGS_HELP["--disc-num"])
        g.add_argument("-D", "--disc-total", type=PositiveIntArg,
                       dest="disc_total", metavar="NUM",
                       help=ARGS_HELP["--disc-total"])
        g.add_argument("-G", "--genre", type=UnicodeArg, dest="genre",
                       metavar="GENRE", help=ARGS_HELP["--genre"])
        g.add_argument("-Y", "--release-year", type=PositiveIntArg,
                       dest="release_year", metavar="YEAR",
                       help=ARGS_HELP["--release-year"])
        g.add_argument("-c", "--comment", dest="simple_comment",
                       type=UnicodeArg, metavar="STRING",
                       help=ARGS_HELP["--comment"])
        g.add_argument("--rename", dest="rename_pattern", metavar="PATTERN",
                       help=ARGS_HELP["--rename"])

        gid3 = arg_parser.add_argument_group("ID3 options")

        def _splitArgs(arg, maxsplit=None):
            NEW_DELIM = "#DELIM#"
            arg = re.sub(r"\\%s" % FIELD_DELIM, NEW_DELIM, arg)
            t = tuple(re.sub(NEW_DELIM, FIELD_DELIM, s)
                         for s in arg.split(FIELD_DELIM))
            if maxsplit is not None and maxsplit < 2:
                raise ValueError("Invalid maxsplit value: {}".format(maxsplit))
            elif maxsplit and len(t) > maxsplit:
                t = t[:maxsplit - 1] + (FIELD_DELIM.join(t[maxsplit - 1:]),)
                assert len(t) <= maxsplit
            return t

        def _unicodeArgValue(arg):
            if compat.PY2:
                return compat.unicode(arg, LOCAL_ENCODING)
            else:
                assert(isinstance(arg, str))
                return arg

        def DescLangArg(arg):
            """DESCRIPTION[:LANG]"""
            arg = _unicodeArgValue(arg)
            vals = _splitArgs(arg, 2)
            desc = vals[0]
            lang = vals[1] if len(vals) > 1 else id3.DEFAULT_LANG
            return (desc, str(lang)[:3] or id3.DEFAULT_LANG)

        def DescTextArg(arg):
            """DESCRIPTION:TEXT"""
            arg = _unicodeArgValue(arg)
            vals = _splitArgs(arg, 2)
            desc = vals[0].strip()
            text = FIELD_DELIM.join(vals[1:] if len(vals) > 1 else [])
            return (desc or u"", text or u"")
        KeyValueArg = DescTextArg

        def DescUrlArg(arg):
            desc, url = DescTextArg(arg)
            return (desc, url.encode("latin1"))

        def FidArg(arg):
            arg = _unicodeArgValue(arg)
            fid = arg.strip().encode("ascii")
            if not fid:
                raise ArgumentTypeError("No frame ID")
            return fid

        def TextFrameArg(arg):
            """FID:TEXT"""
            arg = _unicodeArgValue(arg)
            vals = _splitArgs(arg, 2)
            fid = vals[0].strip().encode("ascii")
            if not fid:
                raise ArgumentTypeError("No frame ID")
            text = vals[1] if len(vals) > 1 else u""
            return (fid, text)

        def UrlFrameArg(arg):
            """FID:TEXT"""
            fid, url = TextFrameArg(arg)
            return (fid, url.encode("latin1"))

        def DateArg(date_str):
            return core.Date.parse(date_str) if date_str else ""

        def CommentArg(arg):
            """
            COMMENT[:DESCRIPTION[:LANG]
            """
            arg = _unicodeArgValue(arg)
            vals = _splitArgs(arg, 3)
            text = vals[0]
            if not text:
                raise ArgumentTypeError("text required")
            desc = vals[1] if len(vals) > 1 else u""
            lang = vals[2] if len(vals) > 2 else id3.DEFAULT_LANG
            return (text, desc, str(lang)[:3])

        def LyricsArg(arg):
            text, desc, lang = CommentArg(arg)
            try:
                with open(text, "rb") as fp:
                    data = fp.read()
            except:
                raise ArgumentTypeError("Unable to read file")
            return (_unicodeArgValue(data), desc, lang)

        def PlayCountArg(pc):
            if not pc:
                raise ArgumentTypeError("value required")
            increment = False
            if pc[0] == "+":
                pc = int(pc[1:])
                increment = True
            else:
                pc = int(pc)
            if pc < 0:
                raise ArgumentTypeError("out of range")
            return (increment, pc)

        def BpmArg(bpm):
            bpm = int(float(bpm) + 0.5)
            if bpm <= 0:
                raise ArgumentTypeError("out of range")
            return bpm

        def DirArg(d):
            if not d or not os.path.isdir(d):
                raise ArgumentTypeError("invalid directory: %s" % d)
            return d

        def ImageArg(s):
            """PATH:TYPE[:DESCRIPTION]
            Returns (path, type_id, mime_type, description)
            """
            args = _splitArgs(s, 3)
            if len(args) < 2:
                raise ArgumentTypeError("Format is: PATH:TYPE[:DESCRIPTION]")

            path, type_str = args[:2]
            desc = unicode(args[2], LOCAL_ENCODING) if len(args) > 2 else u""
            mt = None
            try:
                type_id = id3.frames.ImageFrame.stringToPicType(type_str)
            except:
                raise ArgumentTypeError("invalid pic type: {}".format(type_str))

            if not path:
                raise ArgumentTypeError("path required")
            elif True in [path.startswith(prefix)
                          for prefix in ["http://", "https://"]]:
                mt = ImageFrame.URL_MIME_TYPE
            else:
                if not os.path.isfile(path):
                    raise ArgumentTypeError("file does not exist")
                mt = utils.guessMimetype(path)
                if mt is None:
                    raise ArgumentTypeError("Cannot determine mime-type")

            return (path, type_id, mt, desc)

        def ObjectArg(s):
            """OBJ_PATH:MIME-TYPE[:DESCRIPTION[:FILENAME]],
            Returns (path, mime_type, description, filename)
            """
            args = _splitArgs(s, 4)
            if len(args) < 2:
                raise ArgumentTypeError("too few parts")

            path = args[0]
            mt = None
            desc = None
            filename = None
            if path:
                mt = args[1]
                desc = unicode(args[2], LOCAL_ENCODING) \
                         if len(args) > 2 else u""
                filename = unicode(args[3], LOCAL_ENCODING) \
                           if len(args) > 3 else unicode(os.path.basename(path))
                if not os.path.isfile(path):
                    raise ArgumentTypeError("file does not exist")
                if not mt:
                    raise ArgumentTypeError("mime-type required")
            else:
                raise ArgumentTypeError("path required")
            return (path, mt, desc, filename)

        def UniqFileIdArg(arg):
            owner_id, id = KeyValueArg(arg)
            if not owner_id:
                raise ArgumentTypeError("owner_id required")
            id = str(id)  # don't want to pass unicocode
            if len(id) > 64:
                raise ArgumentTypeError("id must be <= 64 bytes")
            return (owner_id, id)

        def PopularityArg(arg):
            """EMAIL:RATING[:PLAY_COUNT]
            Returns (email, rating, play_count)
            """
            args = _splitArgs(arg, 3)
            if len(args) < 2:
                raise ArgumentTypeError("Incorrect number of argument "
                                        "components")
            email = args[0]
            rating = int(float(args[1]))
            if rating < 0 or rating > 255:
                raise ArgumentTypeError("Rating out-of-range")
            play_count = 0
            if len(args) > 2:
                play_count = int(args[2])
            if play_count < 0:
                raise ArgumentTypeError("Play count out-of-range")
            return (email, rating, play_count)

        # Tag versions
        gid3.add_argument("-1", "--v1", action="store_const", const=id3.ID3_V1,
                          dest="tag_version", default=id3.ID3_ANY_VERSION,
                          help=ARGS_HELP["--v1"])
        gid3.add_argument("-2", "--v2", action="store_const", const=id3.ID3_V2,
                          dest="tag_version", default=id3.ID3_ANY_VERSION,
                          help=ARGS_HELP["--v2"])
        gid3.add_argument("--to-v1.1", action="store_const", const=id3.ID3_V1_1,
                          dest="convert_version", help=ARGS_HELP["--to-v1.1"])
        gid3.add_argument("--to-v2.3", action="store_const", const=id3.ID3_V2_3,
                          dest="convert_version", help=ARGS_HELP["--to-v2.3"])
        gid3.add_argument("--to-v2.4", action="store_const", const=id3.ID3_V2_4,
                          dest="convert_version", help=ARGS_HELP["--to-v2.4"])

        # Dates
        gid3.add_argument("--release-date", type=DateArg, dest="release_date",
                          metavar="DATE",
                          help=ARGS_HELP["--release-date"])
        gid3.add_argument("--orig-release-date", type=DateArg,
                          dest="orig_release_date", metavar="DATE",
                          help=ARGS_HELP["--orig-release-date"])
        gid3.add_argument("--recording-date", type=DateArg,
                          dest="recording_date", metavar="DATE",
                          help=ARGS_HELP["--recording-date"])
        gid3.add_argument("--encoding-date", type=DateArg, dest="encoding_date",
                          metavar="DATE", help=ARGS_HELP["--encoding-date"])
        gid3.add_argument("--tagging-date", type=DateArg, dest="tagging_date",
                          metavar="DATE", help=ARGS_HELP["--tagging-date"])

        # Deprecated opts (removed in 0.8)
        gid3.add_argument("--year", type=int, dest="year_deprecated",
                          help=SUPPRESS)
        gid3.add_argument("--no-tagging-time-frame", action="store_true",
                          help=SUPPRESS)

        # Misc
        gid3.add_argument("--publisher", action="store", type=UnicodeArg,
                          dest="publisher", metavar="STRING",
                          help=ARGS_HELP["--publisher"])
        gid3.add_argument("--play-count", type=PlayCountArg, dest="play_count",
                          metavar="<+>N", default=None,
                          help=ARGS_HELP["--play-count"])
        gid3.add_argument("--bpm", type=BpmArg, dest="bpm", metavar="N",
                          default=None, help=ARGS_HELP["--bpm"])
        gid3.add_argument("--unique-file-id", action="append",
                          type=UniqFileIdArg, dest="unique_file_ids",
                          metavar="OWNER_ID:ID", default=[],
                          help=ARGS_HELP["--unique-file-id"])

        # Comments
        gid3.add_argument("--add-comment", action="append", dest="comments",
                          metavar="COMMENT[:DESCRIPTION[:LANG]", default=[],
                          type=CommentArg, help=ARGS_HELP["--add-comment"])
        gid3.add_argument("--remove-comment", action="append", type=DescLangArg,
                          dest="remove_comment", default=[],
                          metavar="DESCRIPTION[:LANG]",
                          help=ARGS_HELP["--remove-comment"])
        gid3.add_argument("--remove-all-comments", action="store_true",
                          dest="remove_all_comments",
                          help=ARGS_HELP["--remove-all-comments"])

        gid3.add_argument("--add-lyrics", action="append", type=LyricsArg,
                          dest="lyrics", default=[],
                          metavar="LYRICS_FILE[:DESCRIPTION[:LANG]]",
                          help=ARGS_HELP["--add-lyrics"])
        gid3.add_argument("--remove-lyrics", action="append", type=DescLangArg,
                          dest="remove_lyrics", default=[],
                          metavar="DESCRIPTION[:LANG]",
                          help=ARGS_HELP["--remove-lyrics"])
        gid3.add_argument("--remove-all-lyrics", action="store_true",
                          dest="remove_all_lyrics",
                          help=ARGS_HELP["--remove-all-lyrics"])

        gid3.add_argument("--text-frame", action="append", type=TextFrameArg,
                          dest="text_frames", metavar="FID:TEXT", default=[],
                          help=ARGS_HELP["--text-frame"])
        gid3.add_argument("--user-text-frame", action="append",
                          type=DescTextArg,
                          dest="user_text_frames", metavar="DESC:TEXT",
                          default=[], help=ARGS_HELP["--user-text-frame"])

        gid3.add_argument("--url-frame", action="append", type=UrlFrameArg,
                          dest="url_frames", metavar="FID:URL", default=[],
                          help=ARGS_HELP["--url-frame"])
        gid3.add_argument("--user-url-frame", action="append", type=DescUrlArg,
                          dest="user_url_frames", metavar="DESCRIPTION:URL",
                          default=[], help=ARGS_HELP["--user-url-frame"])

        gid3.add_argument("--add-image", action="append", type=ImageArg,
                          dest="images", metavar="IMG_PATH:TYPE[:DESCRIPTION]",
                          default=[], help=ARGS_HELP["--add-image"])
        gid3.add_argument("--remove-image", action="append", type=UnicodeArg,
                          dest="remove_image", default=[],
                          metavar="DESCRIPTION",
                          help=ARGS_HELP["--remove-image"])
        gid3.add_argument("--remove-all-images", action="store_true",
                          dest="remove_all_images",
                          help=ARGS_HELP["--remove-all-images"])
        gid3.add_argument("--write-images", dest="write_images_dir",
                          metavar="DIR", type=DirArg,
                          help=ARGS_HELP["--write-images"])

        gid3.add_argument("--add-object", action="append", type=ObjectArg,
                          dest="objects", default=[],
                          metavar="OBJ_PATH:MIME-TYPE[:DESCRIPTION[:FILENAME]]",
                          help=ARGS_HELP["--add-object"])
        gid3.add_argument("--remove-object", action="append", type=UnicodeArg,
                          dest="remove_object", default=[],
                          metavar="DESCRIPTION",
                          help=ARGS_HELP["--remove-object"])
        gid3.add_argument("--write-objects", action="store",
                          dest="write_objects_dir", metavar="DIR", default=None,
                          help=ARGS_HELP["--write-objects"])
        gid3.add_argument("--remove-all-objects", action="store_true",
                          dest="remove_all_objects",
                          help=ARGS_HELP["--remove-all-objects"])

        gid3.add_argument("--add-popularity", action="append",
                          type=PopularityArg, dest="popularities", default=[],
                          metavar="EMAIL:RATING[:PLAY_COUNT]",
                          help=ARGS_HELP["--add-popularty"])
        gid3.add_argument("--remove-popularity", action="append", type=str,
                          dest="remove_popularity", default=[],
                          metavar="EMAIL",
                          help=ARGS_HELP["--remove-popularity"])

        gid3.add_argument("--remove-v1", action="store_true", dest="remove_v1",
                          default=False, help=ARGS_HELP["--remove-v1"])
        gid3.add_argument("--remove-v2", action="store_true", dest="remove_v2",
                          default=False, help=ARGS_HELP["--remove-v2"])
        gid3.add_argument("--remove-all", action="store_true", default=False,
                          dest="remove_all", help=ARGS_HELP["--remove-all"])
        gid3.add_argument("--remove-frame", action="append", default=[],
                          dest="remove_fids", metavar="FID", type=FidArg,
                          help=ARGS_HELP["--remove-frame"])

        # 'True' means 'apply default max_padding, but only if saving anyhow'
        gid3.add_argument("--max-padding", type=int, dest="max_padding",
                          default=True, metavar="NUM_BYTES",
                          help=ARGS_HELP["--max-padding"])
        gid3.add_argument("--no-max-padding", dest="max_padding",
                          action="store_const", const=None,
                          help=ARGS_HELP["--no-max-padding"])

        _encodings = ["latin1", "utf8", "utf16", "utf16-be"]
        gid3.add_argument("--encoding", dest="text_encoding", default=None,
                          choices=_encodings, metavar='|'.join(_encodings),
                          help=ARGS_HELP["--encoding"])

        # Misc options
        gid4 = arg_parser.add_argument_group("Misc options")
        gid4.add_argument("--force-update", action="store_true", default=False,
                          dest="force_update", help=ARGS_HELP["--force-update"])
        gid4.add_argument("-v", "--verbose", action="store_true",
                          dest="verbose", help=ARGS_HELP["--verbose"])
        gid4.add_argument("--preserve-file-times", action="store_true",
                          dest="preserve_file_time",
                          help=ARGS_HELP["--preserve-file-times"])


    def handleFile(self, f):
        parse_version = self.args.tag_version

        super(ClassicPlugin, self).handleFile(f, tag_version=parse_version)

        if not self.audio_file:
            return

        self.printHeader(f)
        printMsg("-" * 79)

        new_tag = False
        if (not self.audio_file.tag or
                self.handleRemoves(self.audio_file.tag)):
            self.audio_file.initTag(version=parse_version)
            new_tag = True

        try:
            save_tag = (self.handleEdits(self.audio_file.tag) or
                        self.handlePadding(self.audio_file.tag) or
                        self.args.force_update or self.args.convert_version)
        except ValueError as ex:
            printError(str(ex))
            return

        self.printAudioInfo(self.audio_file.info)

        if not save_tag and new_tag:
            printError("No ID3 %s tag found!" %
                       id3.versionToString(self.args.tag_version))
            return

        self.printTag(self.audio_file.tag)

        if save_tag:
            # Use current tag version unless a convert was supplied
            version = (self.args.convert_version or
                       self.audio_file.tag.version)
            printWarning("Writing ID3 version %s" %
                         id3.versionToString(version))

            # DEFAULT_MAX_PADDING is not set up as argument default,
            # because we don't want to rewrite the file if the user
            # did not trigger that explicitly:
            max_padding = self.args.max_padding
            if max_padding is True:
                max_padding = DEFAULT_MAX_PADDING

            self.audio_file.tag.save(
                    version=version, encoding=self.args.text_encoding,
                    backup=self.args.backup,
                    preserve_file_time=self.args.preserve_file_time,
                    max_padding=max_padding)

        if self.args.rename_pattern:
            # Handle file renaming.
            from eyed3.id3.tag import TagTemplate
            template = TagTemplate(self.args.rename_pattern)
            name = template.substitute(self.audio_file.tag, zeropad=True)
            orig = self.audio_file.path
            try:
                self.audio_file.rename(name)
                printWarning("Renamed '%s' to '%s'" %
                             (orig, self.audio_file.path))
            except IOError as ex:
                printError(ex.message)

        printMsg("-" * 79)

    def printHeader(self, file_path):
        file_len = len(file_path)
        from stat import ST_SIZE
        file_size = os.stat(file_path)[ST_SIZE]
        size_str = utils.formatSize(file_size)
        size_len = len(size_str) + 5
        if file_len + size_len >= 79:
            file_path = "..." + file_path[-(75 - size_len):]
            file_len = len(file_path)
        pat_len = 79 - file_len - size_len
        printMsg("%s%s%s[ %s ]%s" %
                 (boldText(file_path, c=HEADER_COLOR()),
                  HEADER_COLOR(), " " * pat_len, size_str, Fore.RESET))

    def printAudioInfo(self, info):
        if isinstance(info, mp3.Mp3AudioInfo):
            printMsg(boldText("Time: ") +
                     "%s\tMPEG%d, Layer %s\t[ %s @ %s Hz - %s ]" %
                     (utils.formatTime(info.time_secs),
                      info.mp3_header.version,
                      "I" * info.mp3_header.layer,
                      info.bit_rate_str,
                      info.mp3_header.sample_freq, info.mp3_header.mode))
            printMsg("-" * 79)

    def _getDefaultNameForObject(self, obj_frame, suffix=""):
        if obj_frame.filename:
            name_str = obj_frame.filename
        else:
            name_str = obj_frame.description
            name_str += ".%s" % obj_frame.mime_type.split("/")[1]
        if suffix:
            name_str += suffix
        return name_str

    def printTag(self, tag):
        if isinstance(tag, id3.Tag):
            if self.args.quiet:
                printMsg("ID3 %s: %d frames" %
                         (id3.versionToString(tag.version),
                          len(tag.frame_set)))
                return

            printMsg("ID3 %s:" % id3.versionToString(tag.version))
            artist = tag.artist if tag.artist else u""
            title = tag.title if tag.title else u""
            album = tag.album if tag.album else u""
            printMsg("%s: %s" % (boldText("title"), title))
            printMsg("%s: %s" % (boldText("artist"), artist))
            printMsg("%s: %s" % (boldText("album"), album))
            printMsg("%s: %s" % (boldText("album artist"), tag.album_artist))

            for date, date_label in [
                    (tag.release_date, "release date"),
                    (tag.original_release_date, "original release date"),
                    (tag.recording_date, "recording date"),
                    (tag.encoding_date, "encoding date"),
                    (tag.tagging_date, "tagging date"),
                    ]:
                if date:
                    printMsg("%s: %s" % (boldText(date_label), str(date)))

            track_str = ""
            (track_num, track_total) = tag.track_num
            if track_num is not None:
                track_str = str(track_num)
                if track_total:
                    track_str += "/%d" % track_total

            genre = tag.genre
            genre_str = "%s: %s (id %s)" % (boldText("genre"),
                                            genre.name,
                                            str(genre.id)) if genre else u""
            printMsg("%s: %s\t\t%s" % (boldText("track"), track_str, genre_str))

            disc_str = ""
            (num, total) = tag.disc_num
            if num is not None:
                disc_str = str(num)
                if total:
                    disc_str += "/%d" % total
                printMsg("%s: %s" % (boldText("disc"), disc_str))

            # PCNT
            play_count = tag.play_count
            if tag.play_count is not None:
                 printMsg("%s %d" % (boldText("Play Count:"), play_count))

            # POPM
            for popm in tag.popularities:
                printMsg("%s [email: %s] [rating: %d] [play count: %d]" %
                         (boldText("Popularity:"), popm.email, popm.rating,
                          popm.count))

            # TBPM
            bpm = tag.bpm
            if bpm is not None:
                 printMsg("%s %d" % (boldText("BPM:"), bpm))

            # TPUB
            pub = tag.publisher
            if pub is not None:
                 printMsg("%s %s" % (boldText("Publisher/label:"), pub))

            # UFID
            for ufid in tag.unique_file_ids:
                printMsg("%s [%s] : %s" % \
                        (boldText("Unique File ID:"), ufid.owner_id,
                         ufid.uniq_id.encode("string_escape")))

            # COMM
            for c in tag.comments:
                printMsg("%s: [Description: %s] [Lang: %s]\n%s" %
                         (boldText("Comment"), c.description or "",
                          c.lang or "", c.text or ""))

            # USLT
            for l in tag.lyrics:
                printMsg("%s: [Description: %s] [Lang: %s]\n%s" %
                         (boldText("Lyrics"), l.description or u"",
                          l.lang or "", l.text))

            # TXXX
            for f in tag.user_text_frames:
                printMsg("%s: [Description: %s]\n%s" %
                         (boldText("UserTextFrame"), f.description, f.text))

            # URL frames
            for desc, url in ( ("Artist URL", tag.artist_url),
                               ("Audio source URL", tag.audio_source_url),
                               ("Audio file URL", tag.audio_file_url),
                               ("Internet radio URL", tag.internet_radio_url),
                               ("Commercial URL", tag.commercial_url),
                               ("Payment URL", tag.payment_url),
                               ("Publisher URL", tag.publisher_url),
                               ("Copyright URL", tag.copyright_url),
                             ):
                if url:
                    printMsg("%s: %s" % (boldText(desc), url))


            # user url frames
            for u in tag.user_url_frames:
                printMsg("%s [Description: %s]: %s" % (u.id, u.description,
                                                       u.url))

            # APIC
            for img in tag.images:
                if img.mime_type != ImageFrame.URL_MIME_TYPE:
                    printMsg("%s: [Size: %d bytes] [Type: %s]" %
                        (boldText(img.picTypeToString(img.picture_type) +
                                  " Image"),
                        len(img.image_data),
                        img.mime_type))
                    printMsg("Description: %s" % img.description)
                    printMsg("")
                    if self.args.write_images_dir:
                        img_path = "%s%s" % (self.args.write_images_dir, os.sep)
                        if not os.path.isdir(img_path):
                            raise IOError("Directory does not exist: %s" %
                                          img_path)
                        img_file = makeUniqueFileName(
                                    os.path.join(img_path, img.makeFileName()))
                        printWarning("Writing %s..." % img_file)
                        with open(img_file, "wb") as fp:
                            fp.write(img.image_data)
                else:
                    printMsg("%s: [Type: %s] [URL: %s]" %
                        (boldText(img.picTypeToString(img.picture_type) +
                                  " Image"),
                        img.mime_type, img.image_url))
                    printMsg("Description: %s" % img.description)
                    printMsg("")

            # GOBJ
            for obj in tag.objects:
                printMsg("%s: [Size: %d bytes] [Type: %s]" %
                         (boldText("GEOB"), len(obj.object_data),
                          obj.mime_type))
                printMsg("Description: %s" % obj.description)
                printMsg("Filename: %s" % obj.filename)
                printMsg("\n")
                if self.args.write_objects_dir:
                    obj_path = "%s%s" % (self.args.write_objects_dir, os.sep)
                    if not os.path.isdir(obj_path):
                        raise IOError("Directory does not exist: %s" % obj_path)
                    obj_file = self._getDefaultNameForObject(obj)
                    count = 1
                    while os.path.exists(os.path.join(obj_path, obj_file)):
                        obj_file = self._getDefaultNameForObject(obj,
                                                                 str(count))
                        count += 1
                    printWarning("Writing %s..." % os.path.join(obj_path,
                                                                obj_file))
                    with open(os.path.join(obj_path, obj_file), "wb") as fp:
                        fp.write(obj.object_data)

            # PRIV
            for p in tag.privates:
                printMsg("%s: [Data: %d bytes]" % (boldText("PRIV"),
                                                   len(p.data)))
                printMsg("Owner Id: %s" % p.owner_id)

            # MCDI
            if tag.cd_id:
                printMsg("\n%s: [Data: %d bytes]" % (boldText("MCDI"),
                                                     len(tag.cd_id)))

            # USER
            if tag.terms_of_use:
                printMsg("\nTerms of Use (%s): %s" % (boldText("USER"),
                                                      tag.terms_of_use))

            if self.args.verbose:
                printMsg("-" * 79)
                printMsg("%d ID3 Frames:" % len(tag.frame_set))
                for fid in tag.frame_set:
                    frames = tag.frame_set[fid]
                    num_frames = len(frames)
                    count = " x %d" % num_frames if num_frames > 1 else ""
                    if not tag.isV1():
                        total_bytes = sum(
                                tuple(frame.header.data_size + frame.header.size
                                          for frame in frames))
                    else:
                        total_bytes = 30
                    printMsg("%s%s (%d bytes)" % (fid, count, total_bytes))
                printMsg("%d bytes unused (padding)" %
                         (tag.file_info.tag_padding_size, ))
        else:
            raise TypeError("Unknown tag type: " + str(type(tag)))

    def handleRemoves(self, tag):
        remove_version = 0
        status = False
        rm_str = ""
        if self.args.remove_all:
            remove_version = id3.ID3_ANY_VERSION
            rm_str = "v1.x and/or v2.x"
        elif self.args.remove_v1:
            remove_version = id3.ID3_V1
            rm_str = "v1.x"
        elif self.args.remove_v2:
            remove_version = id3.ID3_V2
            rm_str = "v2.x"

        if remove_version:
            status = id3.Tag.remove(
                    tag.file_info.name, remove_version,
                    preserve_file_time=self.args.preserve_file_time)
            printWarning("Removing ID3 %s tag: %s" %
                         (rm_str, "SUCCESS" if status else "FAIL"))

        return status

    def handlePadding(self, tag):
        max_padding = self.args.max_padding
        if max_padding is None or max_padding is True:
            return False
        padding = tag.file_info.tag_padding_size
        needs_change = padding > max_padding
        return needs_change

    def handleEdits(self, tag):
        retval = False

        # --remove-all-*, Handling removes first means later options are still
        # applied
        for what, arg, fid in (("comments", self.args.remove_all_comments,
                                id3.frames.COMMENT_FID),
                               ("lyrics", self.args.remove_all_lyrics,
                                id3.frames.LYRICS_FID),
                               ("images", self.args.remove_all_images,
                                id3.frames.IMAGE_FID),
                               ("objects", self.args.remove_all_objects,
                                id3.frames.OBJECT_FID),
                               ):
            if arg and tag.frame_set[fid]:
                printWarning("Removing all %s..." % what)
                del tag.frame_set[fid]
                retval = True

        # --artist, --title, etc. All common/simple text frames.
        for (what, arg, setFunc) in (
                ("artist", self.args.artist, tag._setArtist),
                ("album", self.args.album, tag._setAlbum),
                ("album artist", self.args.album_artist, tag._setAlbumArtist),
                ("title", self.args.title, tag._setTitle),
                ("genre", self.args.genre, tag._setGenre),
                ("release date", self.args.release_date, tag._setReleaseDate),
                ("original release date", self.args.orig_release_date,
                 tag._setOrigReleaseDate),
                ("recording date", self.args.recording_date,
                 tag._setRecordingDate),
                ("encoding date", self.args.encoding_date,
                 tag._setEncodingDate),
                ("tagging date", self.args.tagging_date,
                 tag._setTaggingDate),
                ("beats per minute", self.args.bpm, tag._setBpm),
                ("publisher", self.args.publisher, tag._setPublisher),
            ):
            if arg is not None:
                printWarning("Setting %s: %s" % (what, arg))
                setFunc(arg or None)
                retval = True

        def _checkNumberedArgTuples(curr, new):
            n = None
            if new not in [(None, None), curr]:
                n = [None] * 2
                for i in (0, 1):
                    if new[i] == 0:
                        n[i] = None
                    else:
                        n[i] = new[i] or curr[i]
                n = tuple(n)
            # Returing None means do nothing, (None, None) would clear both vals
            return n

        # --track, --track-total
        track_info = _checkNumberedArgTuples(tag.track_num,
                                             (self.args.track,
                                              self.args.track_total))
        if track_info is not None:
            printWarning("Setting track info: %s" % str(track_info))
            tag.track_num = track_info
            retval = True

        # --track-offset
        if self.args.track_offset:
            offset = self.args.track_offset
            tag.track_num = (tag.track_num[0] + offset, tag.track_num[1])
            printWarning("%s track info by %d: %d" %
                         ("Incrementing" if offset > 0 else "Decrementing",
                         offset, tag.track_num[0]))
            retval = True

        # --disc-num, --disc-total
        disc_info = _checkNumberedArgTuples(tag.disc_num,
                                            (self.args.disc_num,
                                             self.args.disc_total))
        if disc_info is not None:
            printWarning("Setting disc info: %s" % str(disc_info))
            tag.disc_num = disc_info
            retval = True

        if self.args.year_deprecated is not None:
            # XXX DEPRECATED
            warnings.warn("--year option replaced by -Y/--release-year",
                          DeprecationWarning, stacklevel=2)
            if self.args.release_year is None:
                self.args.release_year = self.args.year_deprecated
        # -Y, --release-year
        if self.args.release_year is not None:
            # empty string means clean, None means not given
            year = self.args.release_year
            printWarning("Setting release year: %s" % year)
            tag.release_date = int(year) if year else None
            retval = True

        # -c , simple comment
        if self.args.simple_comment:
            # Just add it as if it came in --add-comment
            self.args.comments.append((self.args.simple_comment, u"",
                                       id3.DEFAULT_LANG))

        # --remove-comment, remove-lyrics, --remove-image, --remove-object
        for what, arg, accessor in (("comment", self.args.remove_comment,
                                     tag.comments),
                                    ("lyrics", self.args.remove_lyrics,
                                     tag.lyrics),
                                    ("image", self.args.remove_image,
                                     tag.images),
                                    ("object", self.args.remove_object,
                                     tag.objects),
                                   ):
            for vals in arg:
                if type(vals) in compat.StringTypes:
                    frame = accessor.remove(vals)
                else:
                    frame = accessor.remove(*vals)
                if frame:
                    printWarning("Removed %s %s" % (what, str(vals)))
                    retval = True
                else:
                    printError("Removing %s failed, %s not found" %
                               (what, str(vals)))

        # --add-comment, --add-lyrics
        for what, arg, accessor in (("comment", self.args.comments,
                                     tag.comments),
                                    ("lyrics", self.args.lyrics, tag.lyrics),
                                   ):
            for text, desc, lang in arg:
                printWarning("Setting %s: %s/%s" % (what, desc, lang))
                accessor.set(text, desc, lang)
                retval = True

        # --play-count
        playcount_arg = self.args.play_count
        if playcount_arg:
            increment, pc = playcount_arg
            if increment:
                printWarning("Increment play count by %d" % pc)
                tag.play_count += pc
            else:
                printWarning("Setting play count to %d" % pc)
                tag.play_count = pc
            retval = True

        # --add-popularty
        for email, rating, play_count in self.args.popularities:
            tag.popularities.set(email, rating, play_count)
            retval = True

        # --remove-popularity
        for email in self.args.remove_popularity:
            popm = tag.popularities.remove(email)
            if popm:
                retval = True

        # --text-frame, --url-frame
        for what, arg, setter in (
                ("text frame", self.args.text_frames, tag.setTextFrame),
                ("url frame", self.args.url_frames, tag._setUrlFrame),
            ):
            for fid, text in arg:
                if text:
                    printWarning("Setting %s %s to '%s'" % (fid, what, text))
                else:
                    printWarning("Removing %s %s" % (fid, what))
                setter(fid, text)
                retval = True

        # --user-text-frame, --user-url-frame
        for what, arg, accessor in (
                ("user text frame", self.args.user_text_frames,
                 tag.user_text_frames),
                ("user url frame", self.args.user_url_frames,
                 tag.user_url_frames),
            ):
            for desc, text in arg:
                if text:
                    printWarning("Setting '%s' %s to '%s'" % (desc, what, text))
                    accessor.set(text, desc)
                else:
                    printWarning("Removing '%s' %s" % (desc, what))
                    accessor.remove(desc)
                retval = True

        # --add-image
        for img_path, img_type, img_mt, img_desc in self.args.images:
            assert(img_path)
            printWarning("Adding image %s" % img_path)
            if img_mt != ImageFrame.URL_MIME_TYPE:
                with open(img_path, "rb") as img_fp:
                    tag.images.set(img_type, img_fp.read(), img_mt, img_desc)
            else:
                tag.images.set(img_type, None, None, img_desc, img_url=img_path)
            retval = True

        # --add-object
        for obj_path, obj_mt, obj_desc, obj_fname in self.args.objects or []:
            assert(obj_path)
            printWarning("Adding object %s" % obj_path)
            with open(obj_path, "rb") as obj_fp:
                tag.objects.set(obj_fp.read(), obj_mt, obj_desc, obj_fname)
            retval = True

        # --unique-file-id
        for arg in self.args.unique_file_ids:
            owner_id, id = arg
            if not id:
                if tag.unique_file_ids.remove(owner_id):
                    printWarning("Removed unique file ID '%s'" % owner_id)
                    retval = True
                else:
                    printWarning("Unique file ID '%s' not found" % owner_id)
            else:
                tag.unique_file_ids.set(id, owner_id)
                printWarning("Setting unique file ID '%s' to %s" %
                              (owner_id, id))
                retval = True

        # --remove-frame
        for fid in self.args.remove_fids:
            assert(isinstance(fid, compat.BytesType))
            if fid in tag.frame_set:
                del tag.frame_set[fid]
                retval = True

        return retval


def _getTemplateKeys():
    from eyed3.id3.tag import TagTemplate
    keys = list(id3.TagTemplate("")._makeMapping(None, False).keys())
    keys.sort()
    return ", ".join(["$%s" % v for v in keys])


ARGS_HELP = {
        "--artist": "Set the artist name.",
        "--album": "Set the album name.",
        "--album-artist": "Set the album artist name. '%s', for "
                          "example. Another example is collaborations when the "
                          "track artist might be 'Eminem featuring Proof' "
                          "the album artist would be 'Eminem'." %
                          core.VARIOUS_ARTISTS,
        "--title": "Set the track title.",
        "--track": "Set the track number. Use 0 to clear.",
        "--track-total": "Set total number of tracks. Use 0 to clear.",
        "--disc-num": "Set the disc number. Use 0 to clear.",
        "--disc-total": "Set total number of discs in set. Use 0 to clear.",
        "--genre": "Set the genre. If the argument is a standard ID3 genre "
                   "name or number both will be set. Otherwise, any string "
                   "can be used. Run 'eyeD3 --plugin=genres' for a list of "
                   "standard ID3 genre names/ids.",

        "--release-year": "Set the year the track was released. Use the date "
                          "options for more precise values or dates other "
                          "than release.",

        "--v1": "Only read and write ID3 v1.x tags. By default, v1.x tags are "
                "only read or written if there is not a v2 tag in the file.",
        "--v2": "Only read/write ID3 v2.x tags. This is the default unless "
                "the file only contains a v1 tag.",

        "--to-v1.1": "Convert the file's tag to ID3 v1.1 (Or 1.0 if there is "
                     "no track number)",
        "--to-v2.3": "Convert the file's tag to ID3 v2.3",
        "--to-v2.4": "Convert the file's tag to ID3 v2.4",

        "--release-date": "Set the date the track/album was released",
        "--orig-release-date": "Set the original date the track/album was "
                               "released",
        "--recording-date": "Set the date the track/album was recorded",
        "--encoding-date": "Set the date the file was encoded",
        "--tagging-date": "Set the date the file was tagged",

        "--comment": "Set a comment. In ID3 tags this is the comment with "
                     "an empty description. See --add-comment to add multiple "
                     "comment frames.",
        "--add-comment":
          "Add or replace a comment. There may be more than one comment in a "
          "tag, as long as the DESCRIPTION and LANG values are unique. The "
          "default DESCRIPTION is '' and the default language code is '%s'." %
          id3.DEFAULT_LANG,
        "--remove-comment": "Remove comment matching DESCRIPTION and LANG. "
                            "The default language code is '%s'." %
                            id3.DEFAULT_LANG,
        "--remove-all-comments": "Remove all comments from the tag.",

        "--add-lyrics":
          "Add or replace a lyrics. There may be more than one set of lyrics "
          "in a tag, as long as the DESCRIPTION and LANG values are unique. "
          "The default DESCRIPTION is '' and the default language code is "
          "'%s'." % id3.DEFAULT_LANG,
        "--remove-lyrics": "Remove lyrics matching DESCRIPTION and LANG. "
                            "The default language code is '%s'." %
                            id3.DEFAULT_LANG,
        "--remove-all-lyrics": "Remove all lyrics from the tag.",

        "--publisher": "Set the publisher/label name",
        "--play-count": "Set the number of times played counter. If the "
                        "argument value begins with '+' the tag's play count "
                        "is incremented by N, otherwise the value is set to "
                        "exactly N.",
        "--bpm": "Set the beats per minute value.",

        "--text-frame": "Set the value of a text frame. To remove the "
                        "frame, specify an empty value. For example, "
                        "--text-frame='TDRC:'",
        "--user-text-frame": "Set the value of a user text frame (i.e., TXXX). "
                             "To remove the frame, specify an empty value. "
                             "e.g., --user-text-frame='SomeDesc:'",
        "--url-frame": "Set the value of a URL frame. To remove the frame, "
                       "specify an empty value. e.g., --url-frame='WCOM:'",
        "--user-url-frame": "Set the value of a user URL frame (i.e., WXXX). "
                            "To remove the frame, specify an empty value. "
                            "e.g., --user-url-frame='SomeDesc:'",

        "--add-image": "Add or replace an image. There may be more than one "
                       "image in a tag, as long as the DESCRIPTION values are "
                       "unique. The default DESCRIPTION is ''. If PATH begins "
                       "with 'http[s]://' then it is interpreted as a URL "
                       "instead of a file containing image data. The TYPE must "
                       "be one of the following: %s."
                       % (", ".join([ImageFrame.picTypeToString(t)
                                    for t in range(ImageFrame.MIN_TYPE,
                                                   ImageFrame.MAX_TYPE + 1)]),
                         ),
        "--remove-image": "Remove image matching DESCRIPTION.",
        "--remove-all-images": "Remove all images from the tag",
        "--write-images": "Causes all attached images (APIC frames) to be "
                          "written to the specified directory.",

        "--add-object": "Add or replace an object. There may be more than one "
                        "object in a tag, as long as the DESCRIPTION values "
                        "are unique. The default DESCRIPTION is ''.",
        "--remove-object": "Remove object matching DESCRIPTION.",
        "--remove-all-objects": "Remove all objects from the tag",
        "--write-objects": "Causes all attached objects (GEOB frames) to be "
                           "written to the specified directory.",

        "--add-popularty": "Adds a pupularity metric. There may be multiples "
                           "popularity values, but each must have a unique "
                           "email address component. The rating is a number "
                           "between 0 (worst) and 255 (best). The play count "
                           "is optional, and defaults to 0, since there is "
                           "already a dedicated play count frame.",
        "--remove-popularity": "Removes the popularity frame with the "
                               "specified email key.",

        "--remove-v1": "Remove ID3 v1.x tag.",
        "--remove-v2": "Remove ID3 v2.x tag.",
        "--remove-all": "Remove ID3 v1.x and v2.x tags.",

        "--remove-frame": "Remove all frames with the given ID. This option "
                          "may be specified multiple times.",

        "--max-padding": "Shrink file if tag padding (unused space) exceeds "
                         "the given number of bytes. "
                         "(Useful e.g. after removal of large cover art.) "
                         "Default is 64 KiB, file will be rewritten with "
                         "default padding (1 KiB) or max padding, whichever "
                         "is smaller.",
        "--no-max-padding": "Disable --max-padding altogether.",

        "--force-update": "Rewrite the tag despite there being no edit "
                          "options.",
        "--verbose": "Show all available tag data",
        "--unique-file-id": "Add a unique file ID frame. If the ID arg is "
                            "empty the frame is removed. An OWNER_ID is "
                            "required. The ID may be no more than 64 bytes.",
        "--encoding": "Set the encoding that is used for all text frames. "
                      "This option is only applied if the tag is updated "
                      "as the result of an edit option (e.g. --artist, "
                       "--title, etc.) or --force-update is specified.",
        "--rename": "Rename file (the extension is not affected) "
                    "based on data in the tag using substitution "
                    "variables: " + _getTemplateKeys(),
        "--preserve-file-times": "When writing, do not update file "
                                 "modification times.",
        "--track-offset": "Increment/decrement the track number by [-]N. "
                          "This option is applied after --track=N is set.",
}


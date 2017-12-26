# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2009-2012  Travis Shirk <travis@pobox.com>
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
import time
from eyed3 import LOCAL_ENCODING as ENCODING
from eyed3.utils.console import printMsg, printError
from eyed3.utils import formatSize, formatTime
from eyed3.info import VERSION
from eyed3.id3 import versionToString
from eyed3.plugins import LoaderPlugin

class NfoPlugin(LoaderPlugin):
    NAMES = ["nfo"]
    SUMMARY = u"Create NFO files for each directory scanned."
    DESCRIPTION = u"Each directory scanned is treated as an album and a "\
                   "`NFO <http://en.wikipedia.org/wiki/.nfo>`_ file is "\
                   "written to standard out.\n\n"\
                   "NFO files are often found in music archives."

    def __init__(self, arg_parser):
        super(NfoPlugin, self).__init__(arg_parser)
        self.albums = {}

    def handleFile(self, f):
        super(NfoPlugin, self).handleFile(f)

        if self.audio_file and self.audio_file.tag:
            tag = self.audio_file.tag
            album = tag.album
            if album and album not in self.albums:
                self.albums[album] = []
                self.albums[album].append(self.audio_file)
            elif album:
                self.albums[album].append(self.audio_file)

    def handleDone(self):
        if not self.albums:
            printMsg(u"No albums found.")
            return

        for album in self.albums:
            audio_files = self.albums[album]
            if not audio_files:
                continue
            audio_files.sort(key=lambda af: af.tag.track_num)

            max_title_len = 0
            avg_bitrate = 0
            encoder_info = ''
            for audio_file in audio_files:
                tag = audio_file.tag
                # Compute maximum title length
                title_len = len(tag.title)
                if title_len > max_title_len:
                    max_title_len = title_len
                # Compute average bitrate
                avg_bitrate += audio_file.info.bit_rate[1]
                # Grab the last lame version in case not all files have one
                if "encoder_version" in audio_file.info.lame_tag:
                    version = audio_file.info.lame_tag['encoder_version']
                    encoder_info = (version or encoder_info)
            avg_bitrate = avg_bitrate / len(audio_files)

            printMsg("")
            printMsg("Artist   : %s" % audio_files[0].tag.artist)
            printMsg("Album    : %s" % album)
            printMsg("Released : %s" %
                     (audio_files[0].tag.original_release_date or
                      audio_files[0].tag.release_date))
            printMsg("Recorded : %s" % audio_files[0].tag.recording_date)
            genre = audio_files[0].tag.genre
            if genre:
                genre = genre.name
            else:
                genre = ""
            printMsg("Genre    : %s" % genre)

            printMsg("")
            printMsg("Source  : ")
            printMsg("Encoder : %s" % encoder_info)
            printMsg("Codec   : mp3")
            printMsg("Bitrate : ~%s K/s @ %s Hz, %s" %
                     (avg_bitrate, audio_files[0].info.sample_freq,
                      audio_files[0].info.mode))
            printMsg("Tag     : ID3 %s" %
                     versionToString(audio_files[0].tag.version))

            printMsg("")
            printMsg("Ripped By: ")

            printMsg("")
            printMsg("Track Listing")
            printMsg("-------------")
            count = 0
            total_time = 0
            total_size = 0
            for audio_file in audio_files:
                tag = audio_file.tag
                count += 1

                title = tag.title
                title_len = len(title)
                padding = " " * ((max_title_len - title_len) + 3)
                time_secs = audio_file.info.time_secs
                total_time += time_secs
                total_size += audio_file.info.size_bytes

                zero_pad = "0" * (len(str(len(audio_files))) - len(str(count)))
                printMsg(" %s%d. %s%s(%s)" %
                         (zero_pad, count, title, padding,
                          formatTime(time_secs)))

            printMsg("")
            printMsg("Total play time : %s" %
                     formatTime(total_time))
            printMsg("Total size      : %s" %
                     formatSize(total_size))

            printMsg("")
            printMsg("=" * 78)
            printMsg(".NFO file created with eyeD3 %s on %s" %
                     (VERSION, time.asctime()))
            printMsg("For more information about eyeD3 go to %s" %
                     "http://eyeD3.nicfit.net/")
            printMsg("=" * 78)


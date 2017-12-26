# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2012  Travis Shirk <travis@pobox.com>
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
from eyed3.plugins import LoaderPlugin
from eyed3.id3.apple import PCST, WFED

class Podcast(LoaderPlugin):
    NAMES = ['itunes-podcast']
    SUMMARY = u"Adds (or removes) the tags necessary for Apple iTunes to "\
               "identify the file as a podcast."

    def __init__(self, arg_parser):
        super(Podcast, self).__init__(arg_parser)
        g = self.arg_group
        g.add_argument("--add", action="store_true",
                       help="Add the podcast frames.")
        g.add_argument("--remove", action="store_true",
                       help="Remove the podcast frames.")

    def _add(self, tag):
        save = False
        if "PCST" not in tag.frame_set:
            tag.frame_set["PCST"] = PCST()
            save = True
        if "WFED" not in tag.frame_set:
            tag.frame_set["WFED"] = WFED(u"http://eyeD3.nicfit.net/")
            save = True

        if save:
            print("\tAdding...")
            tag.save(backup=self.args.backup)
            self._printStatus(tag)

    def _remove(self, tag):
        save = False
        for fid in ["PCST", "WFED"]:
            try:
                del tag.frame_set[fid]
                save = True
            except KeyError:
                continue

        if save:
            print("\tRemoving...")
            tag.save(backup=self.args.backup)
            self._printStatus(tag)

    def _printStatus(self, tag):
        status = ":-("
        if "PCST" in tag.frame_set:
            status = ":-/"
            if "WFED" in tag.frame_set:
                status = ":-)"
        print("\tiTunes podcast? %s" % status)

    def handleFile(self, f):
        super(Podcast, self).handleFile(f)

        if self.audio_file and self.audio_file.tag:
            print(f)
            tag = self.audio_file.tag
            self._printStatus(tag)
            if self.args.remove:
                self._remove(self.audio_file.tag)
            elif self.args.add:
                self._add(self.audio_file.tag)


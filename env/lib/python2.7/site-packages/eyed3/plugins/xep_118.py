# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2009  Travis Shirk <travis@pobox.com>
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
import os

from eyed3.utils.console import printMsg, printError
from eyed3.plugins import LoaderPlugin

class Xep118Plugin(LoaderPlugin):
    NAMES = ["xep-118"]
    SUMMARY = u"Outputs all tags in XEP-118 XML format. "\
               "(see: http://xmpp.org/extensions/xep-0118.html)"

    def handleFile(self, f):
        super(Xep118Plugin, self).handleFile(f)

        if self.audio_file and self.audio_file.tag:
            xml = self.getXML(self.audio_file)
            printMsg(xml)

    def getXML(self, audio_file):
        tag = audio_file.tag

        xml =  u"<tune xmlns='http://jabber.org/protocol/tune'>\n"
        if tag.artist:
            xml += "  <artist>%s</artist>\n" % tag.artist
        if tag.title:
            xml += "  <title>%s</title>\n" % tag.title
        if tag.album:
            xml += "  <source>%s</source>\n" % tag.album
        xml += ("  <track>file://%s</track>\n" %
                unicode(os.path.abspath(audio_file.path)))
        if audio_file.info:
            xml += "  <length>%s</length>\n" % \
                   unicode(audio_file.info.time_secs)
        xml += "</tune>\n"

        return xml


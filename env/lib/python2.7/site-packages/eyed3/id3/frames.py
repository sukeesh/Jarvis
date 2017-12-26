# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2012-2015  Travis Shirk <travis@pobox.com>
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
import re
from collections import namedtuple

from .. import core
from ..utils import requireUnicode
from ..utils.binfuncs import *
from ..compat import StringIO, unicode, BytesType
from .. import Error
from . import ID3_V2, ID3_V2_3, ID3_V2_4
from . import (LATIN1_ENCODING, UTF_8_ENCODING, UTF_16BE_ENCODING,
               UTF_16_ENCODING, DEFAULT_LANG)
from .headers import FrameHeader


from ..utils.log import getLogger
log = getLogger(__name__)


class FrameException(Error):
    pass


TITLE_FID          = "TIT2"
SUBTITLE_FID       = "TIT3"
ARTIST_FID         = "TPE1"
ALBUM_ARTIST_FID   = "TPE2"
ALBUM_FID          = "TALB"
TRACKNUM_FID       = "TRCK"
GENRE_FID          = "TCON"
COMMENT_FID        = "COMM"
USERTEXT_FID       = "TXXX"
OBJECT_FID         = "GEOB"
UNIQUE_FILE_ID_FID = "UFID"
LYRICS_FID         = "USLT"
DISCNUM_FID        = "TPOS"
IMAGE_FID          = "APIC"
USERURL_FID        = "WXXX"
PLAYCOUNT_FID      = "PCNT"
BPM_FID            = "TBPM"
PUBLISHER_FID      = "TPUB"
CDID_FID           = "MCDI"
PRIVATE_FID        = "PRIV"
TOS_FID            = "USER"
POPULARITY_FID     = "POPM"

URL_COMMERCIAL_FID = "WCOM"
URL_COPYRIGHT_FID  = "WCOP"
URL_AUDIOFILE_FID  = "WOAF"
URL_ARTIST_FID     = "WOAR"
URL_AUDIOSRC_FID   = "WOAS"
URL_INET_RADIO_FID = "WORS"
URL_PAYMENT_FID    = "WPAY"
URL_PUBLISHER_FID  = "WPUB"
URL_FIDS           = [URL_COMMERCIAL_FID, URL_COPYRIGHT_FID,
                      URL_AUDIOFILE_FID, URL_ARTIST_FID, URL_AUDIOSRC_FID,
                      URL_INET_RADIO_FID, URL_PAYMENT_FID,
                      URL_PUBLISHER_FID]

TOC_FID            = "CTOC"
CHAPTER_FID        = "CHAP"

DEPRECATED_DATE_FIDS = ["TDAT", "TYER", "TIME", "TORY", "TRDA",
                        # Nonstandard v2.3 only
                        "XDOR",
                       ]
DATE_FIDS = ["TDEN", "TDOR", "TDRC", "TDRL", "TDTG"]


class Frame(object):
    def __init__(self, id):
        self.id = id
        self.header = None

        self.decompressed_size = 0
        self.group_id = None
        self.encrypt_method = None
        self.data = None
        self.data_len = 0
        self.encoding = None

    def parse(self, data, frame_header):
        self.id = frame_header.id
        self.header = frame_header
        self.data = self._disassembleFrame(data)

    def render(self):
        return self._assembleFrame(self.data)

    def __lt__(self, other):
        return self.id < other.id

    @staticmethod
    def decompress(data):
        import zlib
        log.debug("before decompression: %d bytes" % len(data))
        data = zlib.decompress(data, 15)
        log.debug("after decompression: %d bytes" % len(data))
        return data

    @staticmethod
    def compress(data):
        import zlib
        log.debug("before compression: %d bytes" % len(data))
        data = zlib.compress(data)
        log.debug("after compression: %d bytes" % len(data))
        return data

    @staticmethod
    def decrypt(data):
        raise NotImplementedError("Frame decryption not yet supported")

    @staticmethod
    def encrypt(data):
        raise NotImplementedError("Frame encryption not yet supported")

    def _disassembleFrame(self, data):
        assert(self.header)
        header = self.header
        # Format flags in the frame header may add extra data to the
        # beginning of this data.
        if header.minor_version <= 3:
            # 2.3:  compression(4), encryption(1), group(1)
            if header.compressed:
                self.decompressed_size = bin2dec(bytes2bin(data[:4]))
                data = data[4:]
                log.debug("Decompressed Size: %d" % self.decompressed_size)
            if header.encrypted:
                self.encrypt_method = bin2dec(bytes2bin(data[0]))
                data = data[1:]
                log.debug("Encryption Method: %d" % self.encrypt_method)
            if header.grouped:
                self.group_id = bin2dec(bytes2bin(data[0]))
                data = data[1:]
                log.debug("Group ID: %d" % self.group_id)
        else:
            # 2.4:  group(1), encrypted(1), data_length_indicator (4,7)
            if header.grouped:
                self.group_id = bin2dec(bytes2bin(data[0]))
                log.debug("Group ID: %d" % self.group_id)
                data = data[1:]
            if header.encrypted:
                self.encrypt_method = bin2dec(bytes2bin(data[0]))
                data = data[1:]
                log.debug("Encryption Method: %d" % self.encrypt_method)
            if header.data_length_indicator:
                self.data_len = bin2dec(bytes2bin(data[:4], 7))
                data = data[4:]
                log.debug("Data Length: %d" % self.data_len)
                if header.compressed:
                    self.decompressed_size = self.data_len
                    log.debug("Decompressed Size: %d" % self.decompressed_size)

        if header.minor_version == 4 and header.unsync:
            data = deunsyncData(data)
        if header.encrypted:
            data = self.decrypt(data)
        if header.compressed:
            data = self.decompress(data)

        return data

    def _assembleFrame(self, data):
        assert(self.header)
        header = self.header

        # eyeD3 never writes unsync'd frames
        header.unsync = False

        format_data = b""
        if header.minor_version == 3:
            if header.compressed:
                format_data += bin2bytes(dec2bin(len(data), 32))
            if header.encrypted:
                format_data += bin2bytes(dec2bin(self.encrypt_method, 8))
            if header.grouped:
                format_data += bin2bytes(dec2bin(self.group_id, 8))
        else:
            if header.grouped:
                format_data += bin2bytes(dec2bin(self.group_id, 8))
            if header.encrypted:
                format_data += bin2bytes(dec2bin(self.encrypt_method, 8))
            if header.compressed or header.data_length_indicator:
                header.data_length_indicator = 1
                format_data += bin2bytes(dec2bin(len(data), 32))

        if header.compressed:
            data = self.compress(data)

        if header.encrypted:
            data = self.encrypt(data)

        self.data = format_data + data
        return header.render(len(self.data)) + self.data

    ##
    # Process a 3 byte language code (ISO 639-2).
    # This code must match the [A-Z][A-Z][A-Z]
    # (although case is ignored) and be ascii to be considered valid. When
    # deemed invalid warnings are logged and the value is changed to
    # \c DEFAULT_LANG.
    #
    # \param lang The code.
    # \returns The orignal code if valid, \c DEFAULT_LANG if not.
    @staticmethod
    def _processLang(lang):
        try:
            # Test ascii encoding, it MUST be
            lang = lang.encode("ascii")
        except (UnicodeEncodeError, UnicodeDecodeError):
            log.warning("Fixing invalid lyrics language code: %s" % lang)
            lang = DEFAULT_LANG

        # Test it at least looks like a valid code
        if (lang and not re.compile(b"[A-Z][A-Z][A-Z]",
                                    re.IGNORECASE).match(lang)):
            log.warning("Fixing invalid lyrics language code: %s" % lang)
            lang = DEFAULT_LANG

        return lang

    @property
    def text_delim(self):
        assert(self.encoding is not None)
        return b"\x00\x00" if self.encoding in (UTF_16_ENCODING,
                                                UTF_16BE_ENCODING) else b"\x00"

    def _initEncoding(self):
        assert(self.header.version and len(self.header.version) == 3)
        if self.encoding is not None:
            # Make sure the encoding is valid for this version
            if self.header.version[:2] < (2, 4):
                if self.header.version[0] == 1:
                    self.encoding = LATIN1_ENCODING
                else:
                    if self.encoding > UTF_16_ENCODING:
                        # v2.3 cannot do utf16 BE or utf8
                        self.encoding = UTF_16_ENCODING
        else:
            if self.header.version[:2] < (2, 4):
                if self.header.version[0] == 2:
                    self.encoding = UTF_16_ENCODING
                else:
                    self.encoding = LATIN1_ENCODING
            else:
                self.encoding = UTF_8_ENCODING

        assert(LATIN1_ENCODING <= self.encoding <= UTF_8_ENCODING)


class TextFrame(Frame):
    '''Text frames.
    Data string format: encoding (one byte) + text
    '''
    @requireUnicode("text")
    def __init__(self, id, text=None):
        super(TextFrame, self).__init__(id)
        assert(self.id[0] == 'T' or self.id in ["XSOA", "XSOP", "XSOT", "XDOR",
                                                "WFED"])
        self.text = text or u""

    @property
    def text(self):
        return self._text

    @text.setter
    @requireUnicode(1)
    def text(self, txt):
        self._text = txt

    def parse(self, data, frame_header):
        super(TextFrame, self).parse(data, frame_header)

        self.encoding = self.data[0]
        self.text = decodeUnicode(self.data[1:], self.encoding)
        log.debug("TextFrame text: %s" % self.text)

    def render(self):
        self._initEncoding()
        self.data = (self.encoding +
                     self.text.encode(id3EncodingToString(self.encoding)))
        assert(type(self.data) == BytesType)
        return super(TextFrame, self).render()


class UserTextFrame(TextFrame):
    @requireUnicode("description", "text")
    def __init__(self, id=USERTEXT_FID, description=u"", text=u""):
        super(UserTextFrame, self).__init__(id, text=text)
        self.description = description

    @property
    def description(self):
        return self._description

    @description.setter
    @requireUnicode(1)
    def description(self, txt):
        self._description = txt

    def parse(self, data, frame_header):
        '''Data string format:
        encoding (one byte) + description + "\x00" + text '''
        # Calling Frame, not TextFrame implementation here since TextFrame
        # does not know about description
        Frame.parse(self, data, frame_header)

        self.encoding = encoding = self.data[0]
        (d, t) = splitUnicode(self.data[1:], encoding)
        self.description = decodeUnicode(d, encoding)
        log.debug("UserTextFrame description: %s" % self.description)
        self.text = decodeUnicode(t, encoding)
        log.debug("UserTextFrame text: %s" % self.text)

    def render(self):
        self._initEncoding()
        data = (self.encoding +
                self.description.encode(id3EncodingToString(self.encoding)) +
                self.text_delim +
                self.text.encode(id3EncodingToString(self.encoding)))
        self.data = data
        # Calling Frame, not the base
        return Frame.render(self)


class DateFrame(TextFrame):
    ## \a date Either an ISO 8601 date string or a eyed3.core.Date object.
    def __init__(self, id, date=""):
        assert(id in DATE_FIDS or id in DEPRECATED_DATE_FIDS)
        super(DateFrame, self).__init__(id, text=unicode(date))
        self.date = self.text
        self.encoding = LATIN1_ENCODING

    def parse(self, data, frame_header):
        super(DateFrame, self).parse(data, frame_header)
        try:
            if self.text:
                _ = core.Date.parse(self.text.encode("latin1"))
        except ValueError:
            # Date is invalid, log it and reset.
            core.parseError(FrameException(u"Invalid date: " + self.text))
            self.text = u''

    @property
    def date(self):
        return core.Date.parse(self.text.encode("latin1")) if self.text \
                                                           else None

    ## \a date Either an ISO 8601 date string or a eyed3.core.Date object.
    @date.setter
    def date(self, date):
        if not date:
            self.text = u""
            return

        try:
            if type(date) is str:
                date = core.Date.parse(date)
            elif type(date) is unicode:
                date = core.Date.parse(date.encode("latin1"))
            elif not isinstance(date, core.Date):
                raise TypeError("str, unicode, and eyed3.core.Date type "
                                "expected")
        except ValueError:
            log.warning("Invalid date text: %s" % date)
            self.text = u""
            return

        self.text = unicode(str(date))

    def _initEncoding(self):
        # Dates are always latin1 since they are always represented in ISO 8601
        self.encoding = LATIN1_ENCODING


class UrlFrame(Frame):
    def __init__(self, id, url=""):
        assert(id in URL_FIDS or id == USERURL_FID)
        super(UrlFrame, self).__init__(id)
        self.encoding = LATIN1_ENCODING
        self.url = url

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        if isinstance(url, unicode):
            url = url.encode("latin1")
        self._url = url

    def parse(self, data, frame_header):
        super(UrlFrame, self).parse(data, frame_header)
        # The URL is ascii, ensure
        try:
            self.url = unicode(self.data, "ascii").encode("ascii")
        except UnicodeDecodeError:
            log.warning("Non ascii url, clearing.")
            self.url = ""

    def render(self):
        self.data = self.url
        return super(UrlFrame, self).render()


class UserUrlFrame(UrlFrame):
    '''
    Data string format:
    encoding (one byte) + description + "\x00" + url (ascii)
    '''
    @requireUnicode("description")
    def __init__(self, id=USERURL_FID, description=u"", url=""):
        UrlFrame.__init__(self, id, url=url)
        assert(self.id == USERURL_FID)

        self.description = description

    @property
    def description(self):
        return self._description

    @description.setter
    @requireUnicode(1)
    def description(self, desc):
        self._description = desc

    def parse(self, data, frame_header):
        # Calling Frame and NOT UrlFrame to get the basic disassemble behavior
        # UrlFrame would be confused by the encoding, desc, etc.
        super(UserUrlFrame, self).parse(data, frame_header)
        self.encoding = encoding = self.data[0]

        (d, u) = splitUnicode(self.data[1:], encoding)
        self.description = decodeUnicode(d, encoding)
        log.debug("UserUrlFrame description: %s" % self.description)
        # The URL is ascii, ensure
        try:
            self.url = unicode(u, "ascii").encode("ascii")
        except UnicodeDecodeError:
            log.warning("Non ascii url, clearing.")
            self.url = ""
        log.debug("UserUrlFrame text: %s" % self.url)

    def render(self):
        self._initEncoding()
        data = (self.encoding +
                self.description.encode(id3EncodingToString(self.encoding)) +
                self.text_delim + self.url)
        self.data = data
        # Calling Frame, not the base.
        return Frame.render(self)


##
# Data string format:
# <Header for 'Attached picture', ID: "APIC">
#  Text encoding      $xx
#  MIME type          <text string> $00
#  Picture type       $xx
#  Description        <text string according to encoding> $00 (00)
#  Picture data       <binary data>
class ImageFrame(Frame):
    OTHER               = 0x00
    ICON                = 0x01 # 32x32 png only.
    OTHER_ICON          = 0x02
    FRONT_COVER         = 0x03
    BACK_COVER          = 0x04
    LEAFLET             = 0x05
    MEDIA               = 0x06 # label side of cd, picture disc vinyl, etc.
    LEAD_ARTIST         = 0x07
    ARTIST              = 0x08
    CONDUCTOR           = 0x09
    BAND                = 0x0A
    COMPOSER            = 0x0B
    LYRICIST            = 0x0C
    RECORDING_LOCATION  = 0x0D
    DURING_RECORDING    = 0x0E
    DURING_PERFORMANCE  = 0x0F
    VIDEO               = 0x10
    BRIGHT_COLORED_FISH = 0x11 # There's always room for porno.
    ILLUSTRATION        = 0x12
    BAND_LOGO           = 0x13
    PUBLISHER_LOGO      = 0x14
    MIN_TYPE            = OTHER
    MAX_TYPE            = PUBLISHER_LOGO

    URL_MIME_TYPE       = b"-->"

    @requireUnicode("description")
    def __init__(self, id=IMAGE_FID, description=u"",
                 image_data=None, image_url=None,
                 picture_type=None, mime_type=None):
        assert(id == IMAGE_FID)
        super(ImageFrame, self).__init__(id)
        self.description = description
        self.image_data = image_data
        self.image_url = image_url

        self.picture_type = picture_type
        self.mime_type = mime_type

    @property
    def description(self):
        return self._description

    @description.setter
    @requireUnicode(1)
    def description(self, d):
        self._description = d

    @property
    def mime_type(self):
        return self._mime_type

    @mime_type.setter
    def mime_type(self, m):
        m = m or b''
        self._mime_type = m if isinstance(m, BytesType) else m.encode('ascii')

    @property
    def picture_type(self):
        return self._pic_type

    @picture_type.setter
    def picture_type(self, t):
        if t is not None and (t < ImageFrame.MIN_TYPE or
                              t > ImageFrame.MAX_TYPE):
            raise ValueError("Invalid picture_type: %d" % t)
        self._pic_type = t

    def parse(self, data, frame_header):
        super(ImageFrame, self).parse(data, frame_header)

        input = StringIO(self.data)
        log.debug("APIC frame data size: %d" % len(self.data))
        self.encoding = encoding = input.read(1)

        # Mime type
        self.mime_type = b""
        if frame_header.minor_version != 2:
            ch = input.read(1)
            while ch and ch != b"\x00":
                self.mime_type += ch
                ch = input.read(1)
        else:
            # v2.2 (OBSOLETE) special case
            self.mime_type = input.read(3)
        log.debug("APIC mime type: %s" % self.mime_type)
        if not self.mime_type:
            core.parseError(FrameException("APIC frame does not contain a mime "
                                           "type"))
        if (self.mime_type != self.URL_MIME_TYPE and
                self.mime_type.find(b"/") == -1):
            self.mime_type = b"image/" + self.mime_type

        pt = ord(input.read(1))
        log.debug("Initial APIC picture type: %d" % pt)
        if pt < self.MIN_TYPE or pt > self.MAX_TYPE:
            core.parseError(FrameException("Invalid APIC picture type: %d" %
                                           pt))
            # Rather than force this to UNKNOWN, let's assume that they put a
            # character literal instead of it's byte value.
            try:
                pt = int(chr(pt))
            except:
                pt = self.OTHER
            if pt < self.MIN_TYPE or pt > self.MAX_TYPE:
                self.picture_type = self.OTHER
        self.picture_type = pt
        log.debug("APIC picture type: %d" % self.picture_type)

        self.desciption = u""

        # Remaining data is a NULL separated description and image data
        buffer = input.read()
        input.close()

        (desc, img) = splitUnicode(buffer, encoding)
        log.debug("description len: %d" % len(desc))
        log.debug("image len: %d" % len(img))
        self.description = decodeUnicode(desc, encoding)
        log.debug("APIC description: %s" % self.description)

        if self.mime_type.find(self.URL_MIME_TYPE) != -1:
            self.image_data = None
            self.image_url = img
            log.debug("APIC image URL: %s" % len(self.image_url))
        else:
            self.image_data = img
            self.image_url = None
            log.debug("APIC image data: %d bytes" % len(self.image_data))
        if not self.image_data and not self.image_url:
            core.parseError(FrameException("APIC frame does not contain image "
                                           "data/url"))

    def render(self):
        # some code has problems with image descriptions encoded <> latin1
        # namely mp3diags: work around the problem by forcing latin1 encoding for
        # empty descriptions, which is by far the most common case anyway
        if self.description:
            self._initEncoding()
        else:
            self.encoding = LATIN1_ENCODING

        if not self.image_data and self.image_url:
            self.mime_type = self.URL_MIME_TYPE

        data = (self.encoding + self.mime_type + b"\x00" +
                bin2bytes(dec2bin(self.picture_type, 8)) +
                self.description.encode(id3EncodingToString(self.encoding)) +
                self.text_delim)

        if self.image_data:
            data += self.image_data
        elif self.image_url:
            data += self.image_url.encode("ascii")

        self.data = data
        return super(ImageFrame, self).render()

    @staticmethod
    def picTypeToString(t):
        if t == ImageFrame.OTHER:
            return "OTHER"
        elif t == ImageFrame.ICON:
            return "ICON"
        elif t == ImageFrame.OTHER_ICON:
            return "OTHER_ICON"
        elif t == ImageFrame.FRONT_COVER:
            return "FRONT_COVER"
        elif t == ImageFrame.BACK_COVER:
            return "BACK_COVER"
        elif t == ImageFrame.LEAFLET:
            return "LEAFLET"
        elif t == ImageFrame.MEDIA:
            return "MEDIA"
        elif t == ImageFrame.LEAD_ARTIST:
            return "LEAD_ARTIST"
        elif t == ImageFrame.ARTIST:
            return "ARTIST"
        elif t == ImageFrame.CONDUCTOR:
            return "CONDUCTOR"
        elif t == ImageFrame.BAND:
            return "BAND"
        elif t == ImageFrame.COMPOSER:
            return "COMPOSER"
        elif t == ImageFrame.LYRICIST:
            return "LYRICIST"
        elif t == ImageFrame.RECORDING_LOCATION:
            return "RECORDING_LOCATION"
        elif t == ImageFrame.DURING_RECORDING:
            return "DURING_RECORDING"
        elif t == ImageFrame.DURING_PERFORMANCE:
            return "DURING_PERFORMANCE"
        elif t == ImageFrame.VIDEO:
            return "VIDEO"
        elif t == ImageFrame.BRIGHT_COLORED_FISH:
            return "BRIGHT_COLORED_FISH"
        elif t == ImageFrame.ILLUSTRATION:
            return "ILLUSTRATION"
        elif t == ImageFrame.BAND_LOGO:
            return "BAND_LOGO"
        elif t == ImageFrame.PUBLISHER_LOGO:
            return "PUBLISHER_LOGO"
        else:
            raise ValueError("Invalid APIC picture type: %d" % t)

    @staticmethod
    def stringToPicType(s):
        if s == "OTHER":
            return ImageFrame.OTHER
        elif s == "ICON":
            return ImageFrame.ICON
        elif s == "OTHER_ICON":
            return ImageFrame.OTHER_ICON
        elif s == "FRONT_COVER":
            return ImageFrame.FRONT_COVER
        elif s == "BACK_COVER":
            return ImageFrame.BACK_COVER
        elif s == "LEAFLET":
            return ImageFrame.LEAFLET
        elif s == "MEDIA":
            return ImageFrame.MEDIA
        elif s == "LEAD_ARTIST":
            return ImageFrame.LEAD_ARTIST
        elif s == "ARTIST":
            return ImageFrame.ARTIST
        elif s == "CONDUCTOR":
            return ImageFrame.CONDUCTOR
        elif s == "BAND":
            return ImageFrame.BAND
        elif s == "COMPOSER":
            return ImageFrame.COMPOSER
        elif s == "LYRICIST":
            return ImageFrame.LYRICIST
        elif s == "RECORDING_LOCATION":
            return ImageFrame.RECORDING_LOCATION
        elif s == "DURING_RECORDING":
            return ImageFrame.DURING_RECORDING
        elif s == "DURING_PERFORMANCE":
            return ImageFrame.DURING_PERFORMANCE
        elif s == "VIDEO":
            return ImageFrame.VIDEO
        elif s == "BRIGHT_COLORED_FISH":
            return ImageFrame.BRIGHT_COLORED_FISH
        elif s == "ILLUSTRATION":
            return ImageFrame.ILLUSTRATION
        elif s == "BAND_LOGO":
            return ImageFrame.BAND_LOGO
        elif s == "PUBLISHER_LOGO":
            return ImageFrame.PUBLISHER_LOGO
        else:
            raise ValueError("Invalid APIC picture type: %s" % s)

    def makeFileName(self, name=None):
        name = ImageFrame.picTypeToString(self.picture_type) if not name \
                                                             else name
        ext = self.mime_type.split("/")[1]
        if ext == "jpeg":
            ext = "jpg"
        name = '.'.join([name, ext])
        return name


class ObjectFrame(Frame):

    @requireUnicode("description", "filename")
    def __init__(self, id=OBJECT_FID, description=u"", filename=u"",
                 object_data=None, mime_type=None):
        super(ObjectFrame, self).__init__(OBJECT_FID)
        self.description = description
        self.filename = filename
        self.mime_type = mime_type
        self.object_data = object_data

    @property
    def description(self):
        return self._description

    @description.setter
    @requireUnicode(1)
    def description(self, txt):
        self._description = txt

    @property
    def filename(self):
        return self._filename

    @filename.setter
    @requireUnicode(1)
    def filename(self, txt):
        self._filename = txt

    def parse(self, data, frame_header):
        '''Parse the frame from ``data`` bytes using details from
        ``frame_header``.

        Data string format:
        <Header for 'General encapsulated object', ID: "GEOB">
        Text encoding          $xx
        MIME type              <text string> $00
        Filename               <text string according to encoding> $00 (00)
        Content description    <text string according to encoding> $00 (00)
        Encapsulated object    <binary data>
        '''
        super(ObjectFrame, self).parse(data, frame_header)

        input = StringIO(self.data)
        log.debug("GEOB frame data size: " + str(len(self.data)))
        self.encoding = encoding = input.read(1)

        # Mime type
        self.mime_type = ""
        if self.header.minor_version != 2:
            ch = input.read(1)
            while ch != b"\x00":
                self.mime_type += ch
                ch = input.read(1)
        else:
            # v2.2 (OBSOLETE) special case
            self.mime_type = input.read(3)
        log.debug("GEOB mime type: %s" % self.mime_type)
        if not self.mime_type:
            core.parseError(FrameException("GEOB frame does not contain a "
                                           "mime type"))
        if self.mime_type.find("/") == -1:
            core.parseError(FrameException("GEOB frame does not contain a "
                                           "valid mime type"))

        self.filename = u""
        self.description = u""

        # Remaining data is a NULL separated filename, description and object
        # data
        buffer = input.read()
        input.close()

        (filename, buffer) = splitUnicode(buffer, encoding)
        (desc, obj) = splitUnicode(buffer, encoding)
        self.filename = decodeUnicode(filename, encoding)
        log.debug("GEOB filename: " + self.filename)
        self.description = decodeUnicode(desc, encoding)
        log.debug("GEOB description: " + self.description)

        self.object_data = obj
        log.debug("GEOB data: %d bytes " % len(self.object_data))
        if not self.object_data:
            core.parseError(FrameException("GEOB frame does not contain any "
                                           "data"))

    def render(self):
        self._initEncoding()
        data = (self.encoding + self.mime_type + b"\x00" +
                self.filename.encode(id3EncodingToString(self.encoding)) +
                self.text_delim +
                self.description.encode(id3EncodingToString(self.encoding)) +
                self.text_delim +
                self.object_data)
        self.data = data
        return super(ObjectFrame, self).render()


class PrivateFrame(Frame):
    '''PRIV'''

    def __init__(self, id=PRIVATE_FID, owner_id=b"", owner_data=b""):
        super(PrivateFrame, self).__init__(id)
        assert(id == PRIVATE_FID)
        self.owner_id = owner_id
        self.owner_data = owner_data

    def parse(self, data, frame_header):
        super(PrivateFrame, self).parse(data, frame_header)
        try:
            self.owner_id, self.owner_data = self.data.split('\x00', 1)
        except ValueError:
            # If data doesn't contain required \x00
            # all data is taken to be owner_id
            self.owner_id = self.data


    def render(self):
        self.data = self.owner_id + b"\x00" + self.owner_data
        return super(PrivateFrame, self).render()


class MusicCDIdFrame(Frame):

    def __init__(self, id=CDID_FID, toc=b""):
        super(MusicCDIdFrame, self).__init__(id)
        assert(id == CDID_FID)
        self.toc = toc

    @property
    def toc(self):
        return self.data

    @toc.setter
    def toc(self, toc):
        self.data = toc

    def parse(self, data, frame_header):
        super(MusicCDIdFrame, self).parse(data, frame_header)
        self.toc = self.data


class PlayCountFrame(Frame):
    def __init__(self, id=PLAYCOUNT_FID, count=0):
        super(PlayCountFrame, self).__init__(id)
        assert(self.id == PLAYCOUNT_FID)

        if count is None or count < 0:
            raise ValueError("Invalid count value: %s" % str(count))
        self.count = count

    def parse(self, data, frame_header):
        super(PlayCountFrame, self).parse(data, frame_header)
        # data of less then 4 bytes is handled with with 'sz' arg
        if len(self.data) < 4:
            log.warning("Fixing invalid PCNT frame: less than 32 bits")

        self.count = bytes2dec(self.data)

    def render(self):
        self.data = dec2bytes(self.count, 32)
        return super(PlayCountFrame, self).render()


class PopularityFrame(Frame):
    '''Frame type for 'POPM' frames; popularity.
    Frame format:
    <Header for 'Popularimeter', ID: "POPM">
    Email to user   <text string> $00
    Rating          $xx
    Counter         $xx xx xx xx (xx ...)
    '''
    def __init__(self, id=POPULARITY_FID, email=b"", rating=0, count=0):
        super(PopularityFrame, self).__init__(id)
        assert(self.id == POPULARITY_FID)

        self.email = email or b""
        self.rating = rating
        if count is None or count < 0:
            raise ValueError("Invalid count value: %s" % str(count))
        self.count = count

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, rating):
        if rating < 0 or rating > 255:
            raise ValueError("Popularity rating must be >= 0 and <=255")
        self._rating = rating

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email.encode("ascii")

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, count):
        if count < 0:
            raise ValueError("Popularity count must be > 0")
        self._count = count

    def parse(self, data, frame_header):
        super(PopularityFrame, self).parse(data, frame_header)
        data = self.data

        null_byte = data.find('\x00')
        try:
            self.email = data[:null_byte]
        except UnicodeDecodeError:
            core.parseError(FrameException("Invalid (non-ascii) POPM email "
                                           "address. Setting to 'BOGUS'"))
            self.email = b"BOGUS"
        data = data[null_byte + 1:]

        self.rating = bytes2dec(data[0])

        data = data[1:]
        if len(self.data) < 4:
            core.parseError(FrameException(
                "Invalid POPM play count: less than 32 bits."))
        self.count = bytes2dec(data)

    def render(self):
        data = (self.email or b"") + '\x00'
        data += dec2bytes(self.rating)
        data += dec2bytes(self.count, 32)

        self.data = data
        return super(PopularityFrame, self).render()


class UniqueFileIDFrame(Frame):
    def __init__(self, id=UNIQUE_FILE_ID_FID, owner_id=None, uniq_id=None):
        super(UniqueFileIDFrame, self).__init__(id)
        assert(self.id == UNIQUE_FILE_ID_FID)

        self.owner_id = owner_id
        self.uniq_id = uniq_id

    def parse(self, data, frame_header):
        '''
        Data format
        Owner identifier <text string> $00
        Identifier       up to 64 bytes binary data>
        '''
        super(UniqueFileIDFrame, self).parse(data, frame_header)
        split_data = self.data.split('\x00', 1)
        if len(split_data) == 2:
            (self.owner_id, self.uniq_id) = split_data
        else:
            self.owner_id, self.uniq_id = b"", split_data[0]
        log.debug("UFID owner_id: %s" % self.owner_id)
        log.debug("UFID id: %s" % self.uniq_id)
        if len(self.owner_id) == 0:
            dummy_owner_id = "http://www.id3.org/dummy/ufid.html"
            self.owner_id = dummy_owner_id
            core.parseError(FrameException("Invalid UFID, owner_id is empty. "
                                           "Setting to '%s'" % dummy_owner_id))
        elif 0 <= len(self.uniq_id) > 64:
            core.parseError(FrameException("Invalid UFID, ID is empty or too "
                                           "long: %s" % self.uniq_id))

    def render(self):
        self.data = self.owner_id + b"\x00" + self.uniq_id
        return super(UniqueFileIDFrame, self).render()


class DescriptionLangTextFrame(Frame):

    @requireUnicode(2, 4)
    def __init__(self, id, description, lang, text):
        super(DescriptionLangTextFrame,
              self).__init__(id)
        self.lang = lang
        self.description = description
        self.text = text

    @property
    def description(self):
        return self._description

    @description.setter
    @requireUnicode(1)
    def description(self, description):
        self._description = description

    @property
    def text(self):
        return self._text

    @text.setter
    @requireUnicode(1)
    def text(self, text):
        self._text = text

    def parse(self, data, frame_header):
        super(DescriptionLangTextFrame, self).parse(data, frame_header)

        self.encoding = encoding = self.data[0]
        self.lang = Frame._processLang(self.data[1:4].strip(b"\x00"))
        log.debug("%s lang: %s" % (self.id, self.lang))

        try:
            (d, t) = splitUnicode(self.data[4:], encoding)
            self.description = decodeUnicode(d, encoding)
            log.debug("%s description: %s" % (self.id, self.description))
            self.text = decodeUnicode(t, encoding)
            log.debug("%s text: %s" % (self.id, self.text))
        except ValueError:
            log.warning("Invalid %s frame; no description/text" % self.id)
            self.description = u""
            self.text = u""

    def render(self):
        lang = self.lang.encode("ascii")
        if len(lang) > 3:
            lang = lang[0:3]
        elif len(lang) < 3:
            lang = lang + ('\x00' * (3 - len(lang)))

        self._initEncoding()
        data = (self.encoding + lang +
                self.description.encode(id3EncodingToString(self.encoding)) +
                self.text_delim +
                self.text.encode(id3EncodingToString(self.encoding)))
        self.data = data
        return super(DescriptionLangTextFrame, self).render()


class CommentFrame(DescriptionLangTextFrame):
    def __init__(self, id=COMMENT_FID, description=u"", lang=DEFAULT_LANG,
                 text=u""):
        super(CommentFrame, self).__init__(id, description, lang, text)
        assert(self.id == COMMENT_FID)


class LyricsFrame(DescriptionLangTextFrame):
    def __init__(self, id=LYRICS_FID, description=u"", lang=DEFAULT_LANG,
                 text=u""):
        super(LyricsFrame, self).__init__(id, description, lang, text)
        assert(self.id == LYRICS_FID)


class TermsOfUseFrame(Frame):
    @requireUnicode("text")
    def __init__(self, id="USER", text=u"", lang=DEFAULT_LANG):
        super(TermsOfUseFrame, self).__init__(id)
        self.lang = lang
        self.text = text

    @property
    def text(self):
        return self._text

    @text.setter
    @requireUnicode(1)
    def text(self, text):
        self._text = text

    def parse(self, data, frame_header):
        super(TermsOfUseFrame, self).parse(data, frame_header)

        self.encoding = encoding = self.data[0]
        self.lang = Frame._processLang(self.data[1:4]).strip(b"\x00")
        log.debug("%s lang: %s" % (self.id, self.lang))
        self.text = decodeUnicode(self.data[4:], encoding)
        log.debug("%s text: %s" % (self.id, self.text))

    def render(self):
        lang = self.lang.encode("ascii")
        if len(lang) > 3:
            lang = lang[0:3]
        elif len(lang) < 3:
            lang = lang + ('\x00' * (3 - len(lang)))

        self._initEncoding()
        self.data = (self.encoding + lang +
                     self.text.encode(id3EncodingToString(self.encoding)))
        return super(TermsOfUseFrame, self).render()


class TocFrame(Frame):
    '''Table of content frame. There may be more than one, but only one may
    have the top-level flag set.

    Data format:
    Element ID: <string>\x00
    TOC flags:  %000000ab
    Entry count: %xx
    Child elem IDs: <string>\x00 (... num entry count)
    Description: TIT2 frame (optional)
    '''
    TOP_LEVEL_FLAG_BIT = 6
    ORDERED_FLAG_BIT   = 7

    def __init__(self, id=TOC_FID, element_id=None, toplevel=True, ordered=True,
                 child_ids=None, description=None):
        assert(id == TOC_FID)
        super(TocFrame, self).__init__(id)

        self.element_id = element_id
        self.toplevel = toplevel
        self.ordered = ordered
        self.child_ids = child_ids or []
        self.description = description

    def parse(self, data, frame_header):
        super(TocFrame, self).parse(data, frame_header)

        data = self.data
        log.debug("CTOC frame data size: %d" % len(data))

        null_byte = data.find('\x00')
        self.element_id = data[0:null_byte]
        data = data[null_byte + 1:]

        flag_bits = bytes2bin(data[0])
        self.toplevel = bool(flag_bits[self.TOP_LEVEL_FLAG_BIT])
        self.ordered = bool(flag_bits[self.ORDERED_FLAG_BIT])
        entry_count = bytes2dec(data[1])
        data = data[2:]

        self.child_ids = []
        for i in range(entry_count):
            null_byte = data.find('\x00')
            self.child_ids.append(data[:null_byte])
            data = data[null_byte + 1:]

        # Any data remaining must be a TIT2 frame
        self.description = None
        if data and data[:4] != b"TIT2":
            log.warning("Invalid toc data, TIT2 frame expected")
            return
        elif data:
            data = StringIO(data)
            frame_header = FrameHeader.parse(data, self.header.version)
            data = data.read()
            description_frame = TextFrame(TITLE_FID)
            description_frame.parse(data, frame_header)

            self.description = description_frame.text

    def render(self):
        flags = [0] * 8
        if self.toplevel:
            flags[self.TOP_LEVEL_FLAG_BIT] = 1
        if self.ordered:
            flags[self.ORDERED_FLAG_BIT] = 1

        data = (self.element_id.encode('ascii') + '\x00' +
                bin2bytes(flags) + dec2bytes(len(self.child_ids)))

        for id in self.child_ids:
            data += id + '\x00'

        if self.description is not None:
            desc_frame = TextFrame(TITLE_FID, self.description)
            desc_frame.header = FrameHeader(TITLE_FID, self.header.version)
            data += desc_frame.render()

        self.data = data
        return super(TocFrame, self).render()

StartEndTuple = namedtuple("StartEndTuple", ["start", "end"])
'''A 2-tuple, with names 'start' and 'end'.'''


class ChapterFrame(Frame):
    '''Frame type for chapter/section of the audio file.
    <ID3v2.3 or ID3v2.4 frame header, ID: "CHAP">           (10 bytes)
    Element ID      <text string> $00
    Start time      $xx xx xx xx
    End time        $xx xx xx xx
    Start offset    $xx xx xx xx
    End offset      $xx xx xx xx
    <Optional embedded sub-frames>
    '''

    NO_OFFSET = 4294967295
    '''No offset value, aka "0xff0xff0xff0xff"'''

    def __init__(self, id=CHAPTER_FID, element_id=None, times=None,
                 offsets=None, sub_frames=None):
        assert(id == CHAPTER_FID)
        super(ChapterFrame, self).__init__(id)
        self.element_id = element_id
        self.times = times or StartEndTuple(None, None)
        self.offsets = offsets or StartEndTuple(None, None)
        self.sub_frames = sub_frames or FrameSet()

    def parse(self, data, frame_header):
        from .headers import TagHeader, ExtendedTagHeader

        super(ChapterFrame, self).parse(data, frame_header)

        data = self.data
        log.debug("CTOC frame data size: %d" % len(data))

        null_byte = data.find('\x00')
        self.element_id = data[0:null_byte]
        data = data[null_byte + 1:]

        start = bytes2dec(data[:4])
        data = data[4:]
        end = bytes2dec(data[:4])
        data = data[4:]
        self.times = StartEndTuple(start, end)

        start = bytes2dec(data[:4])
        data = data[4:]
        end = bytes2dec(data[:4])
        data = data[4:]
        self.offsets = StartEndTuple(start if start != self.NO_OFFSET else None,
                                     end if end != self.NO_OFFSET else None)

        if data:
            dummy_tag_header = TagHeader(self.header.version)
            dummy_tag_header.tag_size = len(data)
            padding = self.sub_frames.parse(StringIO(data), dummy_tag_header,
                                            ExtendedTagHeader())
        else:
            self.sub_frames = FrameSet()

    def render(self):
        data = self.element_id.encode('ascii') + '\x00'

        for n in self.times + self.offsets:
            if n is not None:
                data += dec2bytes(n, 32)
            else:
                data += b'\xff\xff\xff\xff'

        for f in self.sub_frames.getAllFrames():
            f.header = FrameHeader(f.id, self.header.version)
            data += f.render()

        self.data = data
        return super(ChapterFrame, self).render()

    @property
    def title(self):
        if TITLE_FID in self.sub_frames:
            return self.sub_frames[TITLE_FID][0].text
        return None

    @title.setter
    def title(self, title):
        self.sub_frames.setTextFrame(TITLE_FID, title)

    @property
    def subtitle(self):
        if SUBTITLE_FID in self.sub_frames:
            return self.sub_frames[SUBTITLE_FID][0].text
        return None

    @subtitle.setter
    def subtitle(self, subtitle):
        self.sub_frames.setTextFrame(SUBTITLE_FID, subtitle)

    @property
    def user_url(self):
        if USERURL_FID in self.sub_frames:
            frame = self.sub_frames[USERURL_FID][0]
            # Not returning frame description, it is always the same since it
            # allows only 1 URL.
            return frame.url
        return None

    @user_url.setter
    def user_url(self, url):
        DESCRIPTION = u"chapter url"

        if url is None:
            del self.sub_frames[USERURL_FID]
        else:
            if USERURL_FID in self.sub_frames:
                for frame in self.sub_frames[USERURL_FID]:
                    if frame.description == DESCRIPTION:
                        frame.url = url
                        return

            self.sub_frames[USERURL_FID] = UserUrlFrame(USERURL_FID,
                                                        DESCRIPTION, url)


class FrameSet(dict):
    def __init__(self):
        dict.__init__(self)

    def parse(self, f, tag_header, extended_header):
        '''Read frames starting from the current read position of the file
        object. Returns the amount of padding which occurs after the tag, but
        before the audio content.  A return valule of 0 does not mean error.'''
        self.clear()

        padding_size = 0
        size_left = tag_header.tag_size - extended_header.size
        start_size = size_left
        consumed_size = 0

        # Handle a tag-level unsync.  Some frames may have their own unsync bit
        # set instead.
        tag_data = f.read(size_left)

        # If the tag is 2.3 and the tag header unsync bit is set then all the
        # frame data is deunsync'd at once, otherwise it will happen on a per
        # frame basis.
        if tag_header.unsync and tag_header.version <= ID3_V2_3:
            log.debug("De-unsynching %d bytes at once (<= 2.3 tag)" %
                      len(tag_data))
            og_size = len(tag_data)
            tag_data = deunsyncData(tag_data)
            size_left = len(tag_data)
            log.debug("De-unsynch'd %d bytes at once (<= 2.3 tag) to %d bytes" %
                      (og_size, size_left))

        # Adding bytes to simulate the tag header(s) in the buffer.  This keeps
        # f.tell() values matching the file offsets for logging.
        prepadding = '\x00' * 10  # Tag header
        prepadding += '\x00' * extended_header.size
        tag_buffer = StringIO(prepadding + tag_data)
        tag_buffer.seek(len(prepadding))

        frame_count = 0
        while size_left > 0:
            log.debug("size_left: " + str(size_left))
            if size_left < (10 + 1): # The size of the smallest frame.
                log.debug("FrameSet: Implied padding (size_left<minFrameSize)")
                padding_size = size_left
                break

            log.debug("+++++++++++++++++++++++++++++++++++++++++++++++++")
            log.debug("FrameSet: Reading Frame #" + str(frame_count + 1))
            frame_header = FrameHeader.parse(tag_buffer, tag_header.version)
            if not frame_header:
                log.debug("No frame found, implied padding of %d bytes" %
                          size_left)
                padding_size = size_left
                break

            # Frame data.
            if frame_header.data_size:
                log.debug("FrameSet: Reading %d (0x%X) bytes of data from byte "
                          "pos %d (0x%X)" % (frame_header.data_size,
                                             frame_header.data_size,
                                             tag_buffer.tell(),
                                             tag_buffer.tell()))
                data = tag_buffer.read(frame_header.data_size)

                log.debug("FrameSet: %d bytes of data read" % len(data))
                consumed_size += (frame_header.size +
                                  frame_header.data_size)
                frame = createFrame(tag_header, frame_header, data)
                self[frame.id] = frame
                frame_count += 1

            # Each frame contains data_size + headerSize bytes.
            size_left -= (frame_header.size +
                          frame_header.data_size)

        return padding_size

    def __getitem__(self, fid):
        if fid in self:
            return dict.__getitem__(self, fid)
        else:
            return None

    def __setitem__(self, fid, frame):
        assert(fid == frame.id)

        if fid in self:
            self[fid].append(frame)
        else:
            dict.__setitem__(self, fid, [frame])

    def getAllFrames(self):
        '''Return all the frames in the set as a list. The list is sorted
        in an arbitrary but consistent order.'''
        frames = []
        for flist in list(self.values()):
            frames += flist
        frames.sort()
        return frames

    @requireUnicode(2)
    def setTextFrame(self, fid, text):
        '''Set a text frame value.
        Text frame IDs must be unique.  If a frame with
        the same Id is already in the list it's value is changed, otherwise
        the frame is added.
        '''
        assert(fid[0] == "T" and (fid in ID3_FRAMES or
                                  fid in NONSTANDARD_ID3_FRAMES))

        if fid in self:
            self[fid][0].text = text
        else:
            if fid in (DATE_FIDS + DEPRECATED_DATE_FIDS):
                self[fid] = DateFrame(fid, date=text)
            else:
                self[fid] = TextFrame(fid, text=text)


def deunsyncData(data):
    output = []
    safe = True
    for val in data:
        if safe:
            output.append(val)
            safe = (val != '\xff')
        else:
            if val != '\x00':
                output.append(val)
            safe = True
    return ''.join(output)


# Create and return the appropriate frame.
def createFrame(tag_header, frame_header, data):
    fid = frame_header.id
    FrameClass = None

    if fid in ID3_FRAMES:
        (desc, ver, FrameClass) = ID3_FRAMES[fid]
    elif fid in NONSTANDARD_ID3_FRAMES:
        log.verbose("Non standard frame '%s' encountered" % fid)
        (desc, ver, FrameClass) = NONSTANDARD_ID3_FRAMES[fid]
    else:
        log.warning("Unknown ID3 frame ID: %s" % fid)
        (desc, ver, FrameClass) = ("Unknown", None, Frame)

    # FrameClass may still be None if the frame is standard but does not
    # yet have a concrete type.
    if not FrameClass:
        log.warning("Frame '%s' is not yet supported, using raw Frame to parse"
                    % fid)
        FrameClass = Frame

    log.debug("createFrame '%s' with class '%s'" % (fid, FrameClass))
    if tag_header.version[:2] == (2, 4) and tag_header.unsync:
        frame_header.unsync = True

    frame = FrameClass(fid)
    frame.parse(data, frame_header)
    return frame


def decodeUnicode(bites, encoding):
    codec = id3EncodingToString(encoding)
    log.debug("Unicode encoding: %s" % codec)
    if (codec.startswith("utf_16") and
            len(bites) % 2 != 0 and bites[-1] == b"\x00"):
        # Catch and fix bad utf16 data, it is everywhere.
        log.warning("Fixing utf16 data with extra zero bytes")
        bites = bites[:-1]
    # XXX: not sure if the strip is necessary since the above fix of the data.
    return unicode(bites, codec).rstrip(b"\x00")


def splitUnicode(data, encoding):
    try:
        if encoding == LATIN1_ENCODING or encoding == UTF_8_ENCODING:
            (d, t) = data.split(b"\x00", 1)
        elif encoding == UTF_16_ENCODING or encoding == UTF_16BE_ENCODING:
            # Two null bytes split, but since each utf16 char is also two
            # bytes we need to ensure we found a proper boundary.
            (d, t) = data.split(b"\x00\x00", 1)
            if (len(d) % 2) != 0:
                (d, t) = data.split(b"\x00\x00\x00", 1)
                d += b"\x00"
    except ValueError as ex:
        log.warning("Invalid 2-tuple ID3 frame data: %s", ex)
        d, t = data, b""
    return (d, t)


def id3EncodingToString(encoding):
    if encoding == LATIN1_ENCODING:
        return "latin_1"
    elif encoding == UTF_8_ENCODING:
        return "utf_8"
    elif encoding == UTF_16_ENCODING:
        return "utf_16"
    elif encoding == UTF_16BE_ENCODING:
        return "utf_16_be"
    else:
        raise ValueError("Encoding unknown: %s" % encoding)


def stringToEncoding(s):
    s = s.replace('-', '_')
    if s in ("latin_1", "latin1"):
        return LATIN1_ENCODING
    elif s in ("utf_8", "utf8"):
        return UTF_8_ENCODING
    elif s in ("utf_16", "utf16"):
        return UTF_16_ENCODING
    elif s in ("utf_16_be", "utf16_be"):
        return UTF_16BE_ENCODING
    else:
        raise ValueError("Encoding unknown: %s" % s)


# { frame-id : (frame-description, valid-id3-version, frame-class) }
ID3_FRAMES = { "AENC": ("Audio encryption",
                        ID3_V2,
                        None),
               "APIC": ("Attached picture",
                        ID3_V2,
                        ImageFrame),
               "ASPI": ("Audio seek point index",
                        ID3_V2_4,
                        None),

               "COMM": ("Comments", ID3_V2, CommentFrame),
               "COMR": ("Commercial frame", ID3_V2, None),

               "CTOC": ("Table of contents", ID3_V2, TocFrame),
               "CHAP": ("Chapter", ID3_V2, ChapterFrame),

               "ENCR": ("Encryption method registration", ID3_V2, None),
               "EQUA": ("Equalisation", ID3_V2_3, None),
               "EQU2": ("Equalisation (2)", ID3_V2_4, None),
               "ETCO": ("Event timing codes", ID3_V2, None),

               "GEOB": ("General encapsulated object", ID3_V2, ObjectFrame),
               "GRID": ("Group identification registration", ID3_V2, None),

               "IPLS": ("Involved people list", ID3_V2_3, None),

               "LINK": ("Linked information", ID3_V2, None),

               "MCDI": ("Music CD identifier", ID3_V2, MusicCDIdFrame),
               "MLLT": ("MPEG location lookup table", ID3_V2, None),

               "OWNE": ("Ownership frame", ID3_V2, None),

               "PRIV": ("Private frame", ID3_V2, PrivateFrame),
               "PCNT": ("Play counter", ID3_V2, PlayCountFrame),
               "POPM": ("Popularimeter", ID3_V2, PopularityFrame),
               "POSS": ("Position synchronisation frame", ID3_V2, None),

               "RBUF": ("Recommended buffer size", ID3_V2, None),
               "RVAD": ("Relative volume adjustment", ID3_V2_3, None),
               "RVA2": ("Relative volume adjustment (2)", ID3_V2_4, None),
               "RVRB": ("Reverb", ID3_V2, None),

               "SEEK": ("Seek frame", ID3_V2_4, None),
               "SIGN": ("Signature frame", ID3_V2_4, None),
               "SYLT": ("Synchronised lyric/text", ID3_V2, None),
               "SYTC": ("Synchronised tempo codes", ID3_V2, None),

               "TALB": ("Album/Movie/Show title", ID3_V2, TextFrame),
               "TBPM": ("BPM (beats per minute)", ID3_V2, TextFrame),
               "TCOM": ("Composer", ID3_V2, TextFrame),
               "TCON": ("Content type", ID3_V2, TextFrame),
               "TCOP": ("Copyright message", ID3_V2, TextFrame),
               "TDAT": ("Date", ID3_V2_3, DateFrame),
               "TDEN": ("Encoding time", ID3_V2_4, DateFrame),
               "TDLY": ("Playlist delay", ID3_V2, TextFrame),
               "TDOR": ("Original release time", ID3_V2_4, DateFrame),
               "TDRC": ("Recording time", ID3_V2_4, DateFrame),
               "TDRL": ("Release time", ID3_V2_4, DateFrame),
               "TDTG": ("Tagging time", ID3_V2_4, DateFrame),
               "TENC": ("Encoded by", ID3_V2, TextFrame),
               "TEXT": ("Lyricist/Text writer", ID3_V2, TextFrame),
               "TFLT": ("File type", ID3_V2, TextFrame),
               "TIME": ("Time", ID3_V2_3, DateFrame),
               "TIPL": ("Involved people list", ID3_V2_4, TextFrame),
               "TIT1": ("Content group description", ID3_V2, TextFrame),
               "TIT2": ("Title/songname/content description", ID3_V2,
                        TextFrame),
               "TIT3": ("Subtitle/Description refinement", ID3_V2, TextFrame),
               "TKEY": ("Initial key", ID3_V2, TextFrame),
               "TLAN": ("Language(s)", ID3_V2, TextFrame),
               "TLEN": ("Length", ID3_V2, TextFrame),
               "TMCL": ("Musician credits list", ID3_V2_4, TextFrame),
               "TMED": ("Media type", ID3_V2, TextFrame),
               "TMOO": ("Mood", ID3_V2_4, TextFrame),
               "TOAL": ("Original album/movie/show title", ID3_V2, TextFrame),
               "TOFN": ("Original filename", ID3_V2, TextFrame),
               "TOLY": ("Original lyricist(s)/text writer(s)", ID3_V2,
                        TextFrame),
               "TOPE": ("Original artist(s)/performer(s)", ID3_V2, TextFrame),
               "TORY": ("Original release year", ID3_V2_3, DateFrame),
               "TOWN": ("File owner/licensee", ID3_V2, TextFrame),
               "TPE1": ("Lead performer(s)/Soloist(s)", ID3_V2, TextFrame),
               "TPE2": ("Band/orchestra/accompaniment", ID3_V2, TextFrame),
               "TPE3": ("Conductor/performer refinement", ID3_V2, TextFrame),
               "TPE4": ("Interpreted, remixed, or otherwise modified by",
                        ID3_V2, TextFrame),
               "TPOS": ("Part of a set", ID3_V2, TextFrame),
               "TPRO": ("Produced notice", ID3_V2_4, TextFrame),
               "TPUB": ("Publisher", ID3_V2, TextFrame),
               "TRCK": ("Track number/Position in set", ID3_V2, TextFrame),
               "TRDA": ("Recording dates", ID3_V2_3, DateFrame),
               "TRSN": ("Internet radio station name", ID3_V2, TextFrame),
               "TRSO": ("Internet radio station owner", ID3_V2, TextFrame),
               "TSOA": ("Album sort order", ID3_V2_4, TextFrame),
               "TSOP": ("Performer sort order", ID3_V2_4, TextFrame),
               "TSOT": ("Title sort order", ID3_V2_4, TextFrame),
               "TSIZ": ("Size", ID3_V2_3, TextFrame),
               "TSRC": ("ISRC (international standard recording code)", ID3_V2,
                        TextFrame),
               "TSSE": ("Software/Hardware and settings used for encoding",
                        ID3_V2, TextFrame),
               "TSST": ("Set subtitle", ID3_V2_4, TextFrame),
               "TYER": ("Year", ID3_V2_3, DateFrame),
               "TXXX": ("User defined text information frame", ID3_V2,
                        UserTextFrame),

               "UFID": ("Unique file identifier", ID3_V2, UniqueFileIDFrame),
               "USER": ("Terms of use", ID3_V2, TermsOfUseFrame),
               "USLT": ("Unsynchronised lyric/text transcription", ID3_V2,
                        LyricsFrame),

               "WCOM": ("Commercial information", ID3_V2, UrlFrame),
               "WCOP": ("Copyright/Legal information", ID3_V2, UrlFrame),
               "WOAF": ("Official audio file webpage", ID3_V2, UrlFrame),
               "WOAR": ("Official artist/performer webpage", ID3_V2, UrlFrame),
               "WOAS": ("Official audio source webpage", ID3_V2, UrlFrame),
               "WORS": ("Official Internet radio station homepage", ID3_V2,
                        UrlFrame),
               "WPAY": ("Payment", ID3_V2, UrlFrame),
               "WPUB": ("Publishers official webpage", ID3_V2, UrlFrame),
               "WXXX": ("User defined URL link frame", ID3_V2, UserUrlFrame),
}


def map2_2FrameId(orig_id):
    if orig_id not in TAGS2_2_TO_TAGS_2_3_AND_4:
        return orig_id
    return TAGS2_2_TO_TAGS_2_3_AND_4[orig_id]

# mapping of 2.2 frames to 2.3/2.4
TAGS2_2_TO_TAGS_2_3_AND_4 = {
    "TT1" : "TIT1", # CONTENTGROUP content group description
    "TT2" : "TIT2", # TITLE title/songname/content description
    "TT3" : "TIT3", # SUBTITLE subtitle/description refinement
    "TP1" : "TPE1", # ARTIST lead performer(s)/soloist(s)
    "TP2" : "TPE2", # BAND band/orchestra/accompaniment
    "TP3" : "TPE3", # CONDUCTOR conductor/performer refinement
    "TP4" : "TPE4", # MIXARTIST interpreted, remixed, modified by
    "TCM" : "TCOM", # COMPOSER composer
    "TXT" : "TEXT", # LYRICIST lyricist/text writer
    "TLA" : "TLAN", # LANGUAGE language(s)
    "TCO" : "TCON", # CONTENTTYPE content type
    "TAL" : "TALB", # ALBUM album/movie/show title
    "TRK" : "TRCK", # TRACKNUM track number/position in set
    "TPA" : "TPOS", # PARTINSET part of set
    "TRC" : "TSRC", # ISRC international standard recording code
    "TDA" : "TDAT", # DATE date
    "TYE" : "TYER", # YEAR year
    "TIM" : "TIME", # TIME time
    "TRD" : "TRDA", # RECORDINGDATES recording dates
    "TOR" : "TORY", # ORIGYEAR original release year
    "TBP" : "TBPM", # BPM beats per minute
    "TMT" : "TMED", # MEDIATYPE media type
    "TFT" : "TFLT", # FILETYPE file type
    "TCR" : "TCOP", # COPYRIGHT copyright message
    "TPB" : "TPUB", # PUBLISHER publisher
    "TEN" : "TENC", # ENCODEDBY encoded by
    "TSS" : "TSSE", # ENCODERSETTINGS software/hardware + settings for encoding
    "TLE" : "TLEN", # SONGLEN length (ms)
    "TSI" : "TSIZ", # SIZE size (bytes)
    "TDY" : "TDLY", # PLAYLISTDELAY playlist delay
    "TKE" : "TKEY", # INITIALKEY initial key
    "TOT" : "TOAL", # ORIGALBUM original album/movie/show title
    "TOF" : "TOFN", # ORIGFILENAME original filename
    "TOA" : "TOPE", # ORIGARTIST original artist(s)/performer(s)
    "TOL" : "TOLY", # ORIGLYRICIST original lyricist(s)/text writer(s)
    "TXX" : "TXXX", # USERTEXT user defined text information frame
    "WAF" : "WOAF", # WWWAUDIOFILE official audio file webpage
    "WAR" : "WOAR", # WWWARTIST official artist/performer webpage
    "WAS" : "WOAS", # WWWAUDIOSOURCE official audion source webpage
    "WCM" : "WCOM", # WWWCOMMERCIALINFO commercial information
    "WCP" : "WCOP", # WWWCOPYRIGHT copyright/legal information
    "WPB" : "WPUB", # WWWPUBLISHER publishers official webpage
    "WXX" : "WXXX", # WWWUSER user defined URL link frame
    "IPL" : "IPLS", # INVOLVEDPEOPLE involved people list
    "ULT" : "USLT", # UNSYNCEDLYRICS unsynchronised lyrics/text transcription
    "COM" : "COMM", # COMMENT comments
    "UFI" : "UFID", # UNIQUEFILEID unique file identifier
    "MCI" : "MCDI", # CDID music CD identifier
    "ETC" : "ETCO", # EVENTTIMING event timing codes
    "MLL" : "MLLT", # MPEGLOOKUP MPEG location lookup table
    "STC" : "SYTC", # SYNCEDTEMPO synchronised tempo codes
    "SLT" : "SYLT", # SYNCEDLYRICS synchronised lyrics/text
    "RVA" : "RVAD", # VOLUMEADJ relative volume adjustment
    "EQU" : "EQUA", # EQUALIZATION equalization
    "REV" : "RVRB", # REVERB reverb
    "PIC" : "APIC", # PICTURE attached picture
    "GEO" : "GEOB", # GENERALOBJECT general encapsulated object
    "CNT" : "PCNT", # PLAYCOUNTER play counter
    "POP" : "POPM", # POPULARIMETER popularimeter
    "BUF" : "RBUF", # BUFFERSIZE recommended buffer size
    "CRA" : "AENC", # AUDIOCRYPTO audio encryption
    "LNK" : "LINK", # LINKEDINFO linked information
    # Extension workarounds i.e., ignore them
    "TCP" : "TCMP", # iTunes "extension" for compilation marking
    "TST" : "TSOT", # iTunes "extension" for title sort
    "TSP" : "TSOP", # iTunes "extension" for artist sort
    "TSA" : "TSOA", # iTunes "extension" for album sort
    "TS2" : "TSO2", # iTunes "extension" for album artist sort
    "TSC" : "TSOC", # iTunes "extension" for composer sort
    "TDR" : "TDRL", # iTunes "extension" for release date
    "TDS" : "TDES", # iTunes "extension" for podcast description
    "TID" : "TGID", # iTunes "extension" for podcast identifier
    "WFD" : "WFED", # iTunes "extension" for podcast feed URL
    "CM1" : "CM1 ", # Seems to be some script kiddie tagging the tag.
                    # For example, [rH] join #rH on efnet [rH]
    "PCS" : "PCST", # iTunes extension for podcast marking.
}

from . import apple
NONSTANDARD_ID3_FRAMES = {
    "NCON": ("Undefined MusicMatch extension", ID3_V2, Frame),
    "TCMP": ("iTunes complilation flag extension", ID3_V2, TextFrame),
    "XSOA": ("Album sort-order string extension for v2.3",
             ID3_V2_3, TextFrame),
    "XSOP": ("Performer sort-order string extension for v2.3",
             ID3_V2_3, TextFrame),
    "XSOT": ("Title sort-order string extension for v2.3",
             ID3_V2_3, TextFrame),
    "XDOR": ("MusicBrainz release date (full) extension for v2.3",
             ID3_V2_3, DateFrame),

    "TSO2": ("Album artist sort-order used in iTunes and Picard",
             ID3_V2, TextFrame),
    "TSOC": ("Composer sort-order used in iTunes and Picard",
             ID3_V2, TextFrame),

    "PCST": ("iTunes extension; marks the file as a podcast",
             ID3_V2, apple.PCST),
    "TKWD": ("iTunes extension; podcast keywords?",
             ID3_V2, apple.TKWD),
    "TDES": ("iTunes extension; podcast description?",
             ID3_V2, apple.TDES),
    "TGID": ("iTunes extension; podcast ?????",
             ID3_V2, apple.TGID),
    "WFED": ("iTunes extension; podcast feed URL?",
             ID3_V2, apple.WFED),
    "TCAT": ("iTunes extension; podcast category.",
             ID3_V2, TextFrame),
}


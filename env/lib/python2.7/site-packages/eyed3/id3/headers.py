# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2002-2015  Travis Shirk <travis@pobox.com>
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
import logging
import math, binascii
from ..utils.binfuncs import *
from .. import core

from . import ID3_DEFAULT_VERSION, isValidVersion, normalizeVersion

from ..utils.log import getLogger
log = getLogger(__name__)

NULL_FRAME_FLAGS = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


class TagHeader(object):
    SIZE = 10

    def __init__(self, version=ID3_DEFAULT_VERSION):
        self.clear()
        self.version = version

    def clear(self):
        self.tag_size = 0
        # Flag bits
        self.unsync = False
        self.extended = False
        self.experimental = False
        # v2.4 addition
        self.footer = False

    @property
    def version(self):
        return tuple([v for v in self._version])

    @version.setter
    def version(self, v):
        v = normalizeVersion(v)
        if not isValidVersion(v, fully_qualified=True):
            raise ValueError("Invalid version: %s" % str(v))
        self._version = v

    @property
    def major_version(self):
        return self._version[0]

    @property
    def minor_version(self):
        return self._version[1]

    @property
    def rev_version(self):
        return self._version[2]

    def parse(self, f):
        '''Parse an ID3 v2 header starting at the current position of ``f``.
        If a header is parsed ``True`` is returned, otherwise ``False``. If
        a header is found but malformed an ``eyed3.id3.tag.TagException`` is
        thrown.
        '''
        from .tag import TagException

        self.clear()

        # 3 bytes: v2 header is "ID3".
        if f.read(3) != "ID3":
            return False
        log.debug("Located ID3 v2 tag")

        # 2 bytes: the minor and revision versions.
        version = f.read(2)
        if len(version) != 2:
            return False
        major = 2
        minor = ord(version[0])
        rev = ord(version[1])
        log.debug("TagHeader [major]: %d " % major)
        log.debug("TagHeader [minor]: %d " % minor)
        log.debug("TagHeader [rev]: %d " % rev)
        if not (major == 2 and (minor >= 2 and minor <= 4)):
            raise TagException("ID3 v%d.%d is not supported" % (major, minor))
        self.version = (major, minor, rev)

        # 1 byte (first 4 bits): flags
        data = f.read(1)
        if not data:
            return False
        (self.unsync,
         self.extended,
         self.experimental,
         self.footer) = (bool(b) for b in bytes2bin(data)[0:4])
        log.debug("TagHeader [flags]: unsync(%d) extended(%d) "
                  "experimental(%d) footer(%d)" % (self.unsync, self.extended,
                                                   self.experimental,
                                                   self.footer))

        # 4 bytes: The size of the extended header (if any), frames, and padding
        # afer unsynchronization. This is a sync safe integer, so only the
        # bottom 7 bits of each byte are used.
        tag_size_bytes = f.read(4)
        if len(tag_size_bytes) != 4:
            return False
        log.debug("TagHeader [size string]: 0x%02x%02x%02x%02x" %
                  (ord(tag_size_bytes[0]), ord(tag_size_bytes[1]),
                   ord(tag_size_bytes[2]), ord(tag_size_bytes[3])))
        self.tag_size = bin2dec(bytes2bin(tag_size_bytes, 7))
        log.debug("TagHeader [size]: %d (0x%x)" % (self.tag_size,
                                                   self.tag_size))

        return True

    def render(self, tag_len=None):
        if tag_len is not None:
            self.tag_size = tag_len

        if self.unsync:
            raise NotImplementedError("eyeD3 does not write (only reads) "
                                      "unsync'd data")

        data = b"ID3"
        data += chr(self.minor_version) + chr(self.rev_version)
        data += bin2bytes([int(self.unsync),
                           int(self.extended),
                           int(self.experimental),
                           int(self.footer),
                           0, 0, 0, 0])
        log.debug("Setting tag size to %d" % self.tag_size)
        data += bin2bytes(bin2synchsafe(dec2bin(self.tag_size, 32)))
        log.debug("TagHeader rendered %d bytes" % len(data))
        return data


class ExtendedTagHeader(object):
    RESTRICT_TAG_SZ_LARGE = 0x00
    RESTRICT_TAG_SZ_MED   = 0x01
    RESTRICT_TAG_SZ_SMALL = 0x02
    RESTRICT_TAG_SZ_TINY  = 0x03

    RESTRICT_TEXT_ENC_NONE = 0x00
    RESTRICT_TEXT_ENC_UTF8 = 0x01

    RESTRICT_TEXT_LEN_NONE = 0x00
    RESTRICT_TEXT_LEN_1024 = 0x01
    RESTRICT_TEXT_LEN_128  = 0x02
    RESTRICT_TEXT_LEN_30   = 0x03

    RESTRICT_IMG_ENC_NONE    = 0x00
    RESTRICT_IMG_ENC_PNG_JPG = 0x01

    RESTRICT_IMG_SZ_NONE     = 0x00
    RESTRICT_IMG_SZ_256      = 0x01
    RESTRICT_IMG_SZ_64       = 0x02
    RESTRICT_IMG_SZ_64_EXACT = 0x03

    def __init__(self):
        self.size = 0
        self._flags = 0
        self.crc = None
        self._restrictions = 0

    @property
    def update_bit(self):
        return bool(self._flags & 0x40)
    @update_bit.setter
    def update_bit(self, v):
        if v:
            self._flags |= 0x40
        else:
            self._flags &= ~0x40

    @property
    def crc_bit(self):
        return bool(self._flags & 0x20)
    @crc_bit.setter
    def crc_bit(self, v):
        if v:
            self._flags |= 0x20
        else:
            self._flags &= ~0x20

    @property
    def crc(self):
        return self._crc
    @crc.setter
    def crc(self, v):
        self.crc_bit = 1 if v else 0
        self._crc = v

    @property
    def restrictions_bit(self):
        return bool(self._flags & 0x10)
    @restrictions_bit.setter
    def restrictions_bit(self, v):
        if v:
            self._flags |= 0x10
        else:
            self._flags &= ~0x10

    @property
    def tag_size_restriction(self):
        return self._restrictions >> 6
    @tag_size_restriction.setter
    def tag_size_restriction(self, v):
        assert(v >= 0 and v <= 3)
        self.restrictions_bit = 1
        self._restrictions = (v << 6) | (self._restrictions & 0x3f)

    @property
    def tag_size_restriction_description(self):
        val = self.tag_size_restriction
        if val == ExtendedTagHeader.RESTRICT_TAG_SZ_LARGE:
            return "No more than 128 frames and 1 MB total tag size"
        elif val == ExtendedTagHeader.RESTRICT_TAG_SZ_MED:
            return "No more than 64 frames and 128 KB total tag size"
        elif val == ExtendedTagHeader.RESTRICT_TAG_SZ_SMALL:
            return "No more than 32 frames and 40 KB total tag size"
        elif val == ExtendedTagHeader.RESTRICT_TAG_SZ_TINY:
            return "No more than 32 frames and 4 KB total tag size"

    @property
    def text_enc_restriction(self):
        return (self._restrictions & 0x20) >> 5
    @text_enc_restriction.setter
    def text_enc_restriction(self, v):
        assert(v == 0 or v == 1)
        self.restrictions_bit = 1
        self._restrictions ^= 0x20

    @property
    def text_enc_restriction_description(self):
        if self.text_enc_restriction:
            return "Strings are only encoded with ISO-8859-1 or UTF-8"
        else:
            return "None"

    @property
    def text_length_restriction(self):
        return (self._restrictions >> 3) & 0x03
    @text_length_restriction.setter
    def text_length_restriction(self, v):
        assert(v >= 0 and v <= 3)
        self.restrictions_bit = 1
        self._restrictions = (v << 3) | (self._restrictions & 0xe7)

    @property
    def text_length_restriction_description(self):
        val = self.text_length_restriction
        if val == ExtendedTagHeader.RESTRICT_TEXT_LEN_NONE:
            return "None"
        elif val == ExtendedTagHeader.RESTRICT_TEXT_LEN_1024:
            return "No string is longer than 1024 characters."
        elif val == ExtendedTagHeader.RESTRICT_TEXT_LEN_128:
            return "No string is longer than 128 characters."
        elif val == ExtendedTagHeader.RESTRICT_TEXT_LEN_30:
            return "No string is longer than 30 characters."

    @property
    def image_enc_restriction(self):
        return (self._restrictions & 0x04) >> 2
    @image_enc_restriction.setter
    def image_enc_restriction(self, v):
        assert(v == 0 or v == 1)
        self.restrictions_bit = 1
        self._restrictions ^= 0x04

    @property
    def image_enc_restriction_description(self):
        if self.image_enc_restriction:
            return "Images are encoded only with PNG [PNG] or JPEG [JFIF]."
        else:
            return "None"

    @property
    def image_size_restriction(self):
        return self._restrictions & 0x03
    @image_size_restriction.setter
    def image_size_restriction(self, v):
        assert(v >= 0 and v <= 3)
        self.restrictions_bit = 1
        self._restrictions = v | (self._restrictions & 0xfc)

    @property
    def image_size_restriction_description(self):
        val = self.image_size_restriction
        if val == ExtendedTagHeader.RESTRICT_IMG_SZ_NONE:
            return "None"
        elif val == ExtendedTagHeader.RESTRICT_IMG_SZ_256:
            return "All images are 256x256 pixels or smaller."
        elif val == ExtendedTagHeader.RESTRICT_IMG_SZ_64:
            return "All images are 64x64 pixels or smaller."
        elif val == ExtendedTagHeader.RESTRICT_IMG_SZ_64_EXACT:
            return "All images are exactly 64x64 pixels, unless required "\
                   "otherwise."

    def _syncsafeCRC(self):
        bites = b""
        bites += chr((self.crc >> 28) & 0x7f)
        bites += chr((self.crc >> 21) & 0x7f)
        bites += chr((self.crc >> 14) & 0x7f)
        bites += chr((self.crc >>  7) & 0x7f)
        bites += chr((self.crc >>  0) & 0x7f)
        return bites

    def render(self, version, frame_data, padding=0):
        assert(version[0] == 2)

        data = b""
        if version[1] == 4:
            # Version 2.4
            size = 6
            # Extended flags.
            if self.update_bit:
                data += b"\x00"
            if self.crc_bit:
                data += b"\x05"
                # XXX: Using the absolute value of the CRC. The spec is unclear
                # about the type of this data.
                self.crc = int(math.fabs(binascii.crc32(frame_data +
                                                        (b"\x00" * padding))))
                crc_data = self._syncsafeCRC()
                if len(crc_data) < 5:
                    # pad if necessary
                    crc_data = (b"\x00" * (5 - len(crc_data))) + crc_data
                assert(len(crc_data) == 5)
                data += crc_data
            if self.restrictions_bit:
                data += b"\x01"
                data += chr(self._restrictions)
            log.debug("Rendered extended header data (%d bytes)" % len(data))

            # Extended header size.
            size = bin2bytes(bin2synchsafe(dec2bin(len(data) + 6, 32)))
            assert(len(size) == 4)

            data = size + b"\x01" + bin2bytes(dec2bin(self._flags)) + data
            log.debug("Rendered extended header of size %d" % len(data))
        else:
            # Version 2.3
            size = 6  # Note, the 4 size bytes are not included in the size
            # Extended flags.
            f = [0] * 16
            crc = None
            if self.crc_bit:
                f[0] = 1
                # XXX: Using the absolute value of the CRC.  The spec is unclear
                # about the type of this value.
                self.crc = int(math.fabs(binascii.crc32(frame_data +
                                                        (b"\x00" * padding))))
                crc = bin2bytes(dec2bin(self.crc))
                assert(len(crc) == 4)
                size += 4
            flags = bin2bytes(f)
            assert(len(flags) == 2)
            # Extended header size.
            size = bin2bytes(dec2bin(size, 32))
            assert(len(size) == 4)
            # Padding size
            padding_size = bin2bytes(dec2bin(padding, 32))

            data = size + flags + padding_size
            if crc:
                data += crc

        return data

    # Only call this when you *know* there is an extened header.
    def parse(self, fp, version):
        '''Parse an ID3 v2 extended header starting at the current position
        of ``fp`` and per the format defined by ``version``. This method
        should only be called when the presence of an extended header is known
        since it moves the file position. If a header is found but malformed
        an ``eyed3.id3.tag.TagException`` is thrown. The return value is
        ``None``.
        '''
        from .tag import TagException
        assert(version[0] == 2)

        log.debug("Parsing extended header @ 0x%x" % fp.tell())
        # First 4 bytes is the size of the extended header.
        data = fp.read(4)
        if version[1] == 4:
            # sync-safe
            sz = bin2dec(bytes2bin(data, 7))
            self.size = sz
            log.debug("Extended header size (includes the 4 size bytes): %d" %
                      sz)
            data = fp.read(sz - 4)

            # Number of flag bytes
            if ord(data[0]) != 1 or (ord(data[1]) & 0x8f):
                # As of 2.4 the first byte is 1 and the second can only have
                # bits 6, 5, and 4 set.
                raise TagException("Invalid Extended Header")

            self._flags = ord(data[1])
            log.debug("Extended header flags: %x" % self._flags)

            offset = 2
            if self.update_bit:
                log.debug("Extended header has update bit set")
                assert(ord(data[offset]) == 0)
                offset += 1
            if self.crc_bit:
                log.debug("Extended header has CRC bit set")
                assert(ord(data[offset]) == 5)
                offset += 1
                crc_data = data[offset:offset + 5]
                # This is sync-safe.
                self.crc = bin2dec(bytes2bin(crc_data, 7))
                log.debug("Extended header CRC: %d" % self.crc)
                offset += 5
            if self.restrictions_bit:
                log.debug("Extended header has restrictions bit set")
                assert(ord(data[offset]) == 1)
                offset += 1
                self._restrictions = ord(data[offset])
                offset += 1
        else:
            # v2.3 is totally different... *sigh*
            sz = bin2dec(bytes2bin(data))
            self.size = sz
            log.debug("Extended header size (not including 4 size bytes): %d" %
                      sz)
            tmpFlags = fp.read(2)
            # Read the padding size, but it'll be computed during the parse.
            ps = fp.read(4)
            log.debug("Extended header says there is %d bytes of padding" %
                      bin2dec(bytes2bin(ps)))
            # Make this look like a v2.4 mask.
            self._flags = ord(tmpFlags[0]) >> 2
            if self.crc_bit:
                log.debug("Extended header has CRC bit set")
                crc_data = fp.read(4)
                self.crc = bin2dec(bytes2bin(crc_data))
                log.debug("Extended header CRC: %d" % self.crc)


class FrameHeader(object):

    # 2.4 not only added flag bits, but also reordered the previously defined
    # flags. So these are mapped once the ID3 version is known. Access through
    # 'self', always
    TAG_ALTER   = None
    FILE_ALTER  = None
    READ_ONLY   = None
    COMPRESSED  = None
    ENCRYPTED   = None
    GROUPED     = None
    UNSYNC      = None
    DATA_LEN    = None

    # Constructor.
    def __init__(self, fid, version):
        self._version = version
        self._setBitMask()
        # _setBitMask will throw if the version is no good

        # Correctly set size of header (v2.2 is smaller)
        self.size = 10 if self.minor_version != 2 else 6

        # The frame header itself...
        self.id = fid           # First 4 bytes, frame ID
        self._flags = [0] * 16  # 16 bits, represented here as a list
        self.data_size = 0      # 4 bytes, size of frame data

    def copyFlags(self, rhs):
        self.tag_alter = rhs._flags[rhs.TAG_ALTER]
        self.file_alter = rhs._flags[rhs.FILE_ALTER]
        self.read_only = rhs._flags[rhs.READ_ONLY]
        self.compressed = rhs._flags[rhs.COMPRESSED]
        self.encrypted = rhs._flags[rhs.ENCRYPTED]
        self.grouped = rhs._flags[rhs.GROUPED]
        self.unsync = rhs._flags[rhs.UNSYNC]
        self.data_length_indicator = rhs._flags[rhs.DATA_LEN]

    @property
    def major_version(self):
        return self._version[0]
    @property
    def minor_version(self):
        return self._version[1]
    @property
    def version(self):
        return self._version

    @property
    def tag_alter(self):
        return self._flags[self.TAG_ALTER]
    @tag_alter.setter
    def tag_alter(self, b):
        self._flags[self.TAG_ALTER] = int(bool(b))

    @property
    def file_alter(self):
        return self._flags[self.FILE_ALTER]
    @file_alter.setter
    def file_alter(self, b):
        self._flags[self.FILE_ALTER] = int(bool(b))

    @property
    def read_only(self):
        return self._flags[self.READ_ONLY]
    @read_only.setter
    def read_only(self, b):
        self._flags[self.READ_ONLY] = int(bool(b))

    @property
    def compressed(self):
        return self._flags[self.COMPRESSED]
    @compressed.setter
    def compressed(self, b):
        self._flags[self.COMPRESSED] = int(bool(b))

    @property
    def encrypted(self):
        return self._flags[self.ENCRYPTED]
    @encrypted.setter
    def encrypted(self, b):
        self._flags[self.ENCRYPTED] = int(bool(b))

    @property
    def grouped(self):
        return self._flags[self.GROUPED]
    @grouped.setter
    def grouped(self, b):
        self._flags[self.GROUPED] = int(bool(b))

    @property
    def unsync(self):
        return self._flags[self.UNSYNC]
    @unsync.setter
    def unsync(self, b):
        self._flags[self.UNSYNC] = int(bool(b))

    @property
    def data_length_indicator(self):
        return self._flags[self.DATA_LEN]
    @data_length_indicator.setter
    def data_length_indicator(self, b):
        self._flags[self.DATA_LEN] = int(bool(b))

    def _setBitMask(self):
        major = self.major_version
        minor = self.minor_version

        # 1.x tags are converted to 2.4 frames internally.  These frames are
        # created with frame flags \x00.

        if (major == 2 and minor in (3, 2)):
            # v2.2 does not contain flags, but set anyway, as long as the
            # values remain 0 all is good
            self.TAG_ALTER  = 0
            self.FILE_ALTER = 1
            self.READ_ONLY  = 2
            self.COMPRESSED = 8
            self.ENCRYPTED  = 9
            self.GROUPED    = 10
            # This is not in 2.3 frame header flags, map to unused
            self.UNSYNC      = 14
            # This is not in 2.3 frame header flags, map to unused
            self.DATA_LEN    = 4
        elif ((major == 2 and minor == 4) or (major == 1 and minor in (0, 1))):
            self.TAG_ALTER  = 1
            self.FILE_ALTER = 2
            self.READ_ONLY  = 3
            self.COMPRESSED = 12
            self.ENCRYPTED  = 13
            self.GROUPED    = 9
            self.UNSYNC     = 14
            self.DATA_LEN   = 15
        else:
            raise ValueError("ID3 v" + str(major) + "." + str(minor) +\
                             " is not supported.")

    def render(self, data_size):
        from ..compat import BytesType
        if type(self.id) is BytesType:
            data = self.id
        else:
            data = self.id.encode("ascii")

        self.data_size = data_size

        if self.minor_version == 3:
            data += bin2bytes(dec2bin(data_size, 32))
        else:
            data += bin2bytes(bin2synchsafe(dec2bin(data_size, 32)))

        if self.unsync:
            raise NotImplementedError("eyeD3 does not write (only reads) "
                                      "unsync'd data")
        data += bin2bytes(self._flags)

        return data

    @staticmethod
    def _parse2_2(f, version):
        from .frames import map2_2FrameId
        from .frames import FrameException
        frame_id_22 = f.read(3)
        frame_id = map2_2FrameId(frame_id_22)
        if FrameHeader._isValidFrameId(frame_id):
            log.debug("FrameHeader [id]: %s (0x%x%x%x)" % (frame_id_22,
                                                           ord(frame_id_22[0]),
                                                           ord(frame_id_22[1]),
                                                           ord(frame_id_22[2])))
            frame_header = FrameHeader(frame_id, version)
            # data_size corresponds to the size of the data segment after
            # encryption, compression, and unsynchronization.
            sz = f.read(3)
            frame_header.data_size = bin2dec(bytes2bin(sz, 8))
            log.debug("FrameHeader [data size]: %d (0x%X)" %
                      (frame_header.data_size, frame_header.data_size))
            return frame_header
        elif frame_id == '\x00\x00\x00':
            log.debug("FrameHeader: Null frame id found at byte %d" % f.tell())
        else:
            core.parseError(FrameException("FrameHeader: Illegal Frame ID: %s" %
                                           frame_id))

        return None

    @staticmethod
    def parse(f, version):
        from .frames import FrameException
        log.debug("FrameHeader [start byte]: %d (0x%X)" % (f.tell(),
                                                           f.tell()))
        major_version, minor_version = version[:2]
        if minor_version == 2:
            return FrameHeader._parse2_2(f, version)

        frame_id = f.read(4)
        if FrameHeader._isValidFrameId(frame_id):
            log.debug("FrameHeader [id]: %s (0x%x%x%x%x)" % (frame_id,
                                                             ord(frame_id[0]),
                                                             ord(frame_id[1]),
                                                             ord(frame_id[2]),
                                                             ord(frame_id[3])))
            frame_header = FrameHeader(frame_id, version)
            # data_size corresponds to the size of the data segment after
            # encryption, compression, and unsynchronization.
            sz = f.read(4)
            # In ID3 v2.4 this value became a synch-safe integer, meaning only
            # the low 7 bits are used per byte.
            if minor_version == 3:
                frame_header.data_size = bin2dec(bytes2bin(sz, 8))
            else:
                frame_header.data_size = bin2dec(bytes2bin(sz, 7))
            log.debug("FrameHeader [data size]: %d (0x%X)" %
                      (frame_header.data_size, frame_header.data_size))

            # Frame flags.
            flags = f.read(2)
            frame_header._flags = bytes2bin(flags)
            if log.getEffectiveLevel() <= logging.DEBUG:
                log.debug("FrameHeader [flags]: ta(%d) fa(%d) ro(%d) co(%d) "
                          "en(%d) gr(%d) un(%d) dl(%d)" %
                          (frame_header.tag_alter,
                           frame_header.file_alter, frame_header.read_only,
                           frame_header.compressed, frame_header.encrypted,
                           frame_header.grouped, frame_header.unsync,
                           frame_header.data_length_indicator))
            if (frame_header.minor_version >= 4 and frame_header.compressed and
                   not frame_header.data_length_indicator):
                core.parseError(FrameException("Invalid frame; compressed with "
                                               "no data length indicator"))

            return frame_header
        elif frame_id == '\x00\x00\x00\x00':
            log.debug("FrameHeader: Null frame id found at byte %d" % f.tell())
        else:
            core.parseError(FrameException("FrameHeader: Illegal Frame ID: %s" %
                                           frame_id))

        return None

    @staticmethod
    def _isValidFrameId(id):
        import re
        return re.compile("^[A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9]$").match(id)


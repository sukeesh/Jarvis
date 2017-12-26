# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2007-2012  Travis Shirk <travis@pobox.com>
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
import types
import string
import shutil
import tempfile

from ..utils import requireUnicode, chunkCopy, datePicker
from .. import core
from ..core import TXXX_ALBUM_TYPE, TXXX_ARTIST_ORIGIN, ALBUM_TYPE_IDS
from .. import Error
from . import (ID3_ANY_VERSION, ID3_V1, ID3_V1_0, ID3_V1_1,
               ID3_V2, ID3_V2_2, ID3_V2_3, ID3_V2_4, versionToString)
from . import DEFAULT_LANG
from . import Genre
from . import frames
from .headers import TagHeader, ExtendedTagHeader
from ..compat import StringTypes, BytesType, unicode, UnicodeType

from ..utils.log import getLogger
log = getLogger(__name__)


class TagException(Error):
    pass


ID3_V1_COMMENT_DESC = u"ID3v1.x Comment"
DEFAULT_PADDING = 1024


class Tag(core.Tag):
    def __init__(self):
        core.Tag.__init__(self)
        self.clear()

    def clear(self):
        ## ID3 tag header
        self.header = TagHeader()
        ## Optional extended header in v2 tags.
        self.extended_header = ExtendedTagHeader()
        ## Contains the tag's frames. ID3v1 fields are read and converted
        #  the the corresponding v2 frame.
        self.frame_set = frames.FrameSet()
        self._comments = CommentsAccessor(self.frame_set)
        self._images = ImagesAccessor(self.frame_set)
        self._lyrics = LyricsAccessor(self.frame_set)
        self._objects = ObjectsAccessor(self.frame_set)
        self._privates = PrivatesAccessor(self.frame_set)
        self._user_texts = UserTextsAccessor(self.frame_set)
        self._unique_file_ids = UniqueFileIdAccessor(self.frame_set)
        self._user_urls = UserUrlsAccessor(self.frame_set)
        self._chapters = ChaptersAccessor(self.frame_set)
        self._tocs = TocAccessor(self.frame_set)
        self._popularities = PopularitiesAccessor(self.frame_set)
        self.file_info = None

    def parse(self, fileobj, version=ID3_ANY_VERSION):
        assert(fileobj)
        self.clear()
        version = version or ID3_ANY_VERSION

        close_file = False
        try:
            filename = fileobj.name
        except AttributeError:
            if type(fileobj) in StringTypes:
                filename = fileobj
                fileobj = open(filename, "rb")
                close_file = True
            else:
                raise ValueError("Invalid type: %s" % str(type(fileobj)))

        self.file_info = FileInfo(filename)

        try:
            tag_found = False
            padding = 0
            # The & is for supporting the "meta" versions, any, etc.
            if version[0] & 2:
                tag_found, padding = self._loadV2Tag(fileobj)

            if not tag_found and version[0] & 1:
                tag_found, padding = self._loadV1Tag(fileobj)
                if tag_found:
                    self.extended_header = None

            if tag_found and self.isV2():
                self.file_info.tag_size = (TagHeader.SIZE +
                                           self.header.tag_size)
            if tag_found:
                self.file_info.tag_padding_size = padding

        finally:
            if close_file:
                fileobj.close()

        return tag_found

    ## returns (tag_found, padding_len)
    def _loadV2Tag(self, fp):
        padding = 0
        # Look for a tag and if found load it.
        if not self.header.parse(fp):
            return (False, 0)

        # Read the extended header if present.
        if self.header.extended:
            self.extended_header.parse(fp, self.header.version)

        # Header is definitely there so at least one frame *must* follow.
        padding = self.frame_set.parse(fp, self.header,
                                       self.extended_header)

        log.debug("Tag contains %d bytes of padding." % padding)
        return (True, padding)

    def _loadV1Tag(self, fp):
        v1_enc = "latin1"

        # Seek to the end of the file where all v1x tags are written.
        # v1.x tags are 128 bytes min and max
        fp.seek(0, 2)
        if fp.tell() < 128:
            return (False, 0)
        fp.seek(-128, 2)
        tag_data = fp.read(128)

        if tag_data[0:3] != "TAG":
            return (False, 0)

        log.debug("Located ID3 v1 tag")
        # v1.0 is implied until a v1.1 feature is recognized.
        self.version = ID3_V1_0

        STRIP_CHARS = string.whitespace + "\x00"
        title = tag_data[3:33].strip(STRIP_CHARS)
        log.debug("Tite: %s" % title)
        if title:
            self.title = unicode(title, v1_enc)

        artist = tag_data[33:63].strip(STRIP_CHARS)
        log.debug("Artist: %s" % artist)
        if artist:
            self.artist = unicode(artist, v1_enc)

        album = tag_data[63:93].strip(STRIP_CHARS)
        log.debug("Album: %s" % album)
        if album:
            self.album = unicode(album, v1_enc)

        year = tag_data[93:97].strip(STRIP_CHARS)
        log.debug("Year: %s" % year)
        try:
            if year and int(year):
                # Values here typically mean the year of release
                self.release_date = int(year)
        except ValueError:
            # Bogus year strings.
            log.warn("ID3v1.x tag contains invalid year: %s" % year)
            pass

        # Can't use STRIP_CHARS here, since the final byte is numeric
        comment = tag_data[97:127].rstrip("\x00")
        # Track numbers stuffed in the comment field is what makes v1.1
        if comment:
            if (len(comment) >= 2 and
                    comment[-2] == "\x00" and comment[-1] != "\x00"):
                log.debug("Track Num found, setting version to v1.1")
                self.version = ID3_V1_1

                track = ord(comment[-1])
                self.track_num = (track, None)
                log.debug("Track: " + str(track))
                comment = comment[:-2].strip(STRIP_CHARS)

            # There may only have been a track #
            if comment:
                log.debug("Comment: %s" % comment)
                self.comments.set(unicode(comment, v1_enc), ID3_V1_COMMENT_DESC)

        genre = ord(tag_data[127:128])
        log.debug("Genre ID: %d" % genre)
        try:
            self.genre = genre
        except ValueError as ex:
            log.warning(ex)
            self.genre = None

        return (True, 0)

    @property
    def version(self):
        return self.header.version

    @version.setter
    def version(self, v):
        self.header.version = v

    def isV1(self):
        '''Test ID3 major version for v1.x'''
        return self.header.major_version == 1

    def isV2(self):
        '''Test ID3 major version for v2.x'''
        return self.header.major_version == 2

    @requireUnicode(2)
    def setTextFrame(self, fid, txt):
        if not fid.startswith("T") or fid.startswith("TX"):
            raise ValueError("Invalid frame-id for text frame: " +
                             unicode(fid, "ascii"))

        if not txt and self.frame_set[fid]:
            del self.frame_set[fid]
        elif txt:
            self.frame_set.setTextFrame(fid, txt)

    def getTextFrame(self, fid):
        if not fid.startswith("T") or fid.startswith("TX"):
            raise ValueError("Invalid frame-id for text frame: " +
                             unicode(fid, "ascii"))
        f = self.frame_set[fid]
        return f[0].text if f else None

    @requireUnicode(1)
    def _setArtist(self, val):
        self.setTextFrame(frames.ARTIST_FID, val)

    def _getArtist(self):
        return self.getTextFrame(frames.ARTIST_FID)

    @requireUnicode(1)
    def _setAlbumArtist(self, val):
        self.setTextFrame(frames.ALBUM_ARTIST_FID, val)

    def _getAlbumArtist(self):
        return self.getTextFrame(frames.ALBUM_ARTIST_FID)

    @requireUnicode(1)
    def _setAlbum(self, val):
        self.setTextFrame(frames.ALBUM_FID, val)

    def _getAlbum(self):
        return self.getTextFrame(frames.ALBUM_FID)

    @requireUnicode(1)
    def _setTitle(self, val):
        self.setTextFrame(frames.TITLE_FID, val)

    def _getTitle(self):
        return self.getTextFrame(frames.TITLE_FID)

    def _setTrackNum(self, val):
        self._setNum(frames.TRACKNUM_FID, val)

    def _getTrackNum(self):
        return self._splitNum(frames.TRACKNUM_FID)

    def _splitNum(self, fid):
        f = self.frame_set[fid]
        first, second = None, None
        if f and f[0].text:
            n = f[0].text.split('/')
            try:
                first = int(n[0])
                second = int(n[1]) if len(n) == 2 else None
            except ValueError as ex:
                log.warning(str(ex))
        return (first, second)

    def _setNum(self, fid, val):
        if type(val) is tuple:
            tn, tt = val
        elif type(val) is int:
            tn, tt = val, None
        elif val is None:
            tn, tt = None, None

        n = (tn, tt)

        if n[0] is None and n[1] is None:
            if self.frame_set[fid]:
                del self.frame_set[fid]
            return

        total_str = ""
        if n[1] is not None:
            if n[1] >= 0 and n[1] <= 9:
                total_str = "0" + str(n[1])
            else:
                total_str = str(n[1])

        t = n[0] if n[0] else 0
        track_str = str(t)

        # Pad with zeros according to how large the total count is.
        if len(track_str) == 1:
            track_str = "0" + track_str
        if len(track_str) < len(total_str):
            track_str = ("0" * (len(total_str) - len(track_str))) + track_str

        final_str = ""
        if track_str and total_str:
            final_str = "%s/%s" % (track_str, total_str)
        elif track_str and not total_str:
            final_str = track_str

        self.frame_set.setTextFrame(fid, unicode(final_str))

    @property
    def comments(self):
        return self._comments

    def _getBpm(self):
        bpm = None
        if frames.BPM_FID in self.frame_set:
            bpm_str = self.frame_set[frames.BPM_FID][0].text or u"0"
            try:
                # Round floats since the spec says this is an integer
                bpm = int(round(float(bpm_str)))
            except ValueError as ex:
                log.warning(ex)
        return bpm

    def _setBpm(self, bpm):
        assert(bpm >= 0)
        self.setTextFrame(frames.BPM_FID, unicode(str(bpm)))

    bpm = property(_getBpm, _setBpm)

    @property
    def play_count(self):
        if frames.PLAYCOUNT_FID in self.frame_set:
            pc = self.frame_set[frames.PLAYCOUNT_FID][0]
            return pc.count
        else:
            return None

    @play_count.setter
    def play_count(self, count):
        if count is None:
            del self.frame_set[frames.PLAYCOUNT_FID]
            return

        if count < 0:
            raise ValueError("Invalid play count value: %d" % count)

        if self.frame_set[frames.PLAYCOUNT_FID]:
            pc = self.frame_set[frames.PLAYCOUNT_FID][0]
            pc.count = count
        else:
            self.frame_set[frames.PLAYCOUNT_FID] = \
                frames.PlayCountFrame(count=count)

    def _getPublisher(self):
        if frames.PUBLISHER_FID in self.frame_set:
            pub = self.frame_set[frames.PUBLISHER_FID]
            return pub[0].text
        else:
            return None

    @requireUnicode(1)
    def _setPublisher(self, p):
        self.setTextFrame(frames.PUBLISHER_FID, p)

    publisher = property(_getPublisher, _setPublisher)

    @property
    def cd_id(self):
        if frames.CDID_FID in self.frame_set:
            return self.frame_set[frames.CDID_FID][0].toc
        else:
            return None

    @cd_id.setter
    def cd_id(self, toc):
        if len(toc) > 804:
            raise ValueError("CD identifier table of contents can be no "
                             "greater than 804 bytes")

        if self.frame_set[frames.CDID_FID]:
            cdid = self.frame_set[frames.CDID_FID][0]
            cdid.toc = BytesType(toc)
        else:
            self.frame_set[frames.CDID_FID] = \
                frames.MusicCDIdFrame(toc=toc)

    @property
    def images(self):
        return self._images

    def _getEncodingDate(self):
        return self._getDate("TDEN")

    def _setEncodingDate(self, date):
        self._setDate("TDEN", date)
    encoding_date = property(_getEncodingDate, _setEncodingDate)

    @property
    def best_release_date(self):
        '''This method tries its best to return a date of some sort, amongst
        alll the possible date frames. The order of preference for a release
        date is 1) date of original release 2) date of this versions release
        3) the recording date. Or None is returned.'''
        import warnings
        warnings.warn("Use Tag.getBestDate() instead", DeprecationWarning,
                      stacklevel=2)
        return (self.original_release_date or
                self.release_date or
                self.recording_date)

    def getBestDate(self, prefer_recording_date=False):
        '''This method returns a date of some sort, amongst all the possible
        date frames. The order of preference is:

        1) date of original release
        2) date of this versions release
        3) the recording date.

        Unless ``prefer_recording_date`` is ``True`` in which case the order is
        3, 1, 2.

        ``None`` will be returned if no dates are available.'''
        return datePicker(self, prefer_recording_date)

    def _getReleaseDate(self):
        return self._getDate("TDRL") if self.version == ID3_V2_4 \
                                     else self._getV23OrignalReleaseDate()

    def _setReleaseDate(self, date):
        self._setDate("TDRL" if self.version == ID3_V2_4 else "TORY", date)

    release_date = property(_getReleaseDate, _setReleaseDate)
    '''The date the audio was released. This is NOT the original date the
    work was released, instead it is more like the pressing or version of the
    release. Original release date is usually what is intended but many programs
    use this frame and/or don't distinguish between the two.'''

    def _getOrigReleaseDate(self):
        return self._getDate("TDOR") or self._getV23OrignalReleaseDate()

    def _setOrigReleaseDate(self, date):
        self._setDate("TDOR", date)

    original_release_date = property(_getOrigReleaseDate, _setOrigReleaseDate)
    '''The date the work was originally released.'''

    def _getRecordingDate(self):
        return self._getDate("TDRC") or self._getV23RecordingDate()

    def _setRecordingDate(self, date):
        if date is None:
            for fid in ("TDRC", "TYER", "TDAT", "TIME"):
                self._setDate(fid, None)
        elif self.version == ID3_V2_4:
            self._setDate("TDRC", date)
        else:
            self._setDate("TYER", unicode(date.year))
            if None not in (date.month, date.day):
                date_str = u"%s%s" % (str(date.day).rjust(2, "0"),
                                      str(date.month).rjust(2, "0"))
                self._setDate("TDAT", date_str)
            if None not in (date.hour, date.minute):
                date_str = u"%s%s" % (str(date.hour).rjust(2, "0"),
                                      str(date.minute).rjust(2, "0"))
                self._setDate("TIME", date_str)

    recording_date = property(_getRecordingDate, _setRecordingDate)
    '''The date of the recording. Many applications use this for release date
    regardless of the fact that this value is rarely known, and release dates
    are more correct.'''

    def _getV23RecordingDate(self):
        # v2.3 TYER (yyyy), TDAT (DDMM), TIME (HHmm)
        date = None
        try:
            date_str = ""
            if "TYER" in self.frame_set:
                date_str = self.frame_set["TYER"][0].text.encode("latin1")
                date = core.Date.parse(date_str)
            if "TDAT" in self.frame_set:
                text = self.frame_set["TDAT"][0].text.encode("latin1")
                date_str += "-%s-%s" % (text[2:], text[:2])
                date = core.Date.parse(date_str)
            if "TIME" in self.frame_set:
                text = self.frame_set["TIME"][0].text.encode("latin1")
                date_str += "T%s:%s" % (text[:2], text[2:])
                date = core.Date.parse(date_str)
        except ValueError as ex:
            log.warning("Invalid v2.3 TYER, TDAT, or TIME frame: %s" % ex)

        return date

    def _getV23OrignalReleaseDate(self):
        date, date_str = None, None
        try:
            for fid in ("XDOR", "TORY"):
                # Prefering XDOR over TORY since it can contain full date.
                if fid in self.frame_set:
                    date_str = self.frame_set[fid][0].text.encode("latin1")
                    break
            if date_str:
                date = core.Date.parse(date_str)
        except ValueError as ex:
            log.warning("Invalid v2.3 TORY/XDOR frame: %s" % ex)

        return date

    def _getTaggingDate(self):
        return self._getDate("TDTG")

    def _setTaggingDate(self, date):
        self._setDate("TDTG", date)
    tagging_date = property(_getTaggingDate, _setTaggingDate)

    def _setDate(self, fid, date):
        assert(fid in frames.DATE_FIDS or
               fid in frames.DEPRECATED_DATE_FIDS)

        if date is None:
            try:
                del self.frame_set[fid]
            except KeyError:
                pass
            return

        # Special casing the conversion to DATE objects cuz TDAT and TIME won't
        if fid not in ("TDAT", "TIME"):
            # Convert to ISO format which is what FrameSet wants.
            date_type = type(date)
            if date_type is int:
                # The integer year
                date = core.Date(date)
            elif date_type in StringTypes:
                date = core.Date.parse(date)
            elif not isinstance(date, core.Date):
                raise TypeError("Invalid type: %s" % str(type(date)))

        date_text = unicode(str(date))
        if fid in self.frame_set:
            self.frame_set[fid][0].date = date
        else:
            self.frame_set[fid] = frames.DateFrame(fid, date_text)

    def _getDate(self, fid):
        if fid in ("TORY", "XDOR"):
            return self._getV23OrignalReleaseDate()

        if fid in self.frame_set:
            if fid in ("TYER", "TDAT", "TIME"):
                if fid == "TYER":
                    # Contain years only, date conversion can happen
                    return core.Date(int(self.frame_set[fid][0].text))
                else:
                    return self.frame_set[fid][0].text
            else:
                return self.frame_set[fid][0].date
        else:
            return None

    @property
    def lyrics(self):
        return self._lyrics

    @property
    def disc_num(self):
        return self._splitNum(frames.DISCNUM_FID)

    @disc_num.setter
    def disc_num(self, val):
        self._setNum(frames.DISCNUM_FID, val)

    @property
    def objects(self):
        return self._objects

    @property
    def privates(self):
        return self._privates

    @property
    def popularities(self):
        return self._popularities

    def _getGenre(self):
        f = self.frame_set[frames.GENRE_FID]
        if f and f[0].text:
            return Genre.parse(f[0].text)
        else:
            return None

    def _setGenre(self, g):
        '''
        Set the genre. Four types are accepted for the ``g`` argument.
        A Genre object, an acceptable (see Genre.parse) genre string,
        or an integer genre ID all will set the value. A value of None will
        remove the genre.'''
        if g is None:
            if self.frame_set[frames.GENRE_FID]:
                del self.frame_set[frames.GENRE_FID]
            return

        if isinstance(g, unicode):
            g = Genre.parse(g)
        elif isinstance(g, int):
            g = Genre(id=g)
        elif not isinstance(g, Genre):
            raise TypeError("Invalid genre data type: %s" % str(type(g)))
        self.frame_set.setTextFrame(frames.GENRE_FID, unicode(g))
    genre = property(_getGenre, _setGenre)

    @property
    def user_text_frames(self):
        return self._user_texts

    def _setUrlFrame(self, fid, url):
        if fid not in frames.URL_FIDS:
            raise ValueError("Invalid URL frame-id")

        if self.frame_set[fid]:
            if not url:
                del self.frame_set[fid]
            else:
                self.frame_set[fid][0].url = url
        else:
            self.frame_set[fid] = frames.UrlFrame(fid, url)

    def _getUrlFrame(self, fid):
        if fid not in frames.URL_FIDS:
            raise ValueError("Invalid URL frame-id")
        f = self.frame_set[fid]
        return f[0].url if f else None

    @property
    def commercial_url(self):
        return self._getUrlFrame(frames.URL_COMMERCIAL_FID)

    @commercial_url.setter
    def commercial_url(self, url):
        self._setUrlFrame(frames.URL_COMMERCIAL_FID, url)

    @property
    def copyright_url(self):
        return self._getUrlFrame(frames.URL_COPYRIGHT_FID)

    @copyright_url.setter
    def copyright_url(self, url):
        self._setUrlFrame(frames.URL_COPYRIGHT_FID, url)

    @property
    def audio_file_url(self):
        return self._getUrlFrame(frames.URL_AUDIOFILE_FID)

    @audio_file_url.setter
    def audio_file_url(self, url):
        self._setUrlFrame(frames.URL_AUDIOFILE_FID, url)

    @property
    def audio_source_url(self):
        return self._getUrlFrame(frames.URL_AUDIOSRC_FID)

    @audio_source_url.setter
    def audio_source_url(self, url):
        self._setUrlFrame(frames.URL_AUDIOSRC_FID, url)

    @property
    def artist_url(self):
        return self._getUrlFrame(frames.URL_ARTIST_FID)

    @artist_url.setter
    def artist_url(self, url):
        self._setUrlFrame(frames.URL_ARTIST_FID, url)

    @property
    def internet_radio_url(self):
        return self._getUrlFrame(frames.URL_INET_RADIO_FID)

    @internet_radio_url.setter
    def internet_radio_url(self, url):
        self._setUrlFrame(frames.URL_INET_RADIO_FID, url)

    @property
    def payment_url(self):
        return self._getUrlFrame(frames.URL_PAYMENT_FID)

    @payment_url.setter
    def payment_url(self, url):
        self._setUrlFrame(frames.URL_PAYMENT_FID, url)

    @property
    def publisher_url(self):
        return self._getUrlFrame(frames.URL_PUBLISHER_FID)

    @publisher_url.setter
    def publisher_url(self, url):
        self._setUrlFrame(frames.URL_PUBLISHER_FID, url)

    @property
    def user_url_frames(self):
        return self._user_urls

    @property
    def unique_file_ids(self):
        return self._unique_file_ids

    @property
    def terms_of_use(self):
        if self.frame_set[frames.TOS_FID]:
            return self.frame_set[frames.TOS_FID][0].text

    @terms_of_use.setter
    @requireUnicode(1)
    def terms_of_use(self, tos):
        if self.frame_set[frames.TOS_FID]:
            self.frame_set[frames.TOS_FID][0].text = tos
        else:
            self.frame_set[frames.TOS_FID] = frames.TermsOfUseFrame(text=tos)

    def _raiseIfReadonly(self):
        if self.read_only:
            raise RuntimeError("Tag is set read only.")

    def save(self, filename=None, version=None, encoding=None, backup=False,
             preserve_file_time=False, max_padding=None):
        '''Save the tag. If ``filename`` is not give the value from the
        ``file_info`` member is used, or a ``TagException`` is raised. The
        ``version`` argument can be used to select an ID3 version other than
        the version read. ``Select text encoding with ``encoding`` or use
        the existing (or default) encoding. If ``backup`` is True the orignal
        file is preserved; likewise if ``preserve_file_time`` is True the
        file´s modification/access times are not updated.
        '''
        self._raiseIfReadonly()

        if not (filename or self.file_info):
            raise TagException("No file")
        elif filename:
            self.file_info = FileInfo(filename)

        version = version if version else self.version
        if version == ID3_V2_2:
            raise NotImplementedError("Unable to write ID3 v2.2")
        self.version = version

        if backup and os.path.isfile(self.file_info.name):
            backup_name = "%s.%s" % (self.file_info.name, "orig")
            i = 1
            while os.path.isfile(backup_name):
                backup_name = "%s.%s.%d" % (self.file_info.name, "orig", i)
                i += 1
            shutil.copyfile(self.file_info.name, backup_name)

        if version[0] == 1:
            self._saveV1Tag(version)
        elif version[0] == 2:
            self._saveV2Tag(version, encoding, max_padding)
        else:
            assert(not "Version bug: %s" % str(version))

        if preserve_file_time and None not in (self.file_info.atime,
                                               self.file_info.mtime):
            self.file_info.touch((self.file_info.atime, self.file_info.mtime))
        else:
            self.file_info.initStatTimes()

    def _saveV1Tag(self, version):
        self._raiseIfReadonly()

        assert(version[0] == 1)

        def pack(s, n):
            assert(type(s) is str)
            return s.ljust(n, '\x00')[:n]

        def encode(s):
            return s.encode("latin_1", "replace")

        # Build tag buffer.
        tag = b"TAG"
        tag += pack(encode(self.title) if self.title else b"", 30)
        tag += pack(encode(self.artist) if self.artist else b"", 30)
        tag += pack(encode(self.album) if self.album else b"", 30)

        release_date = self.getBestDate()
        year = str(release_date.year) if release_date else b""
        tag += pack(encode(year), 4)

        cmt = ""
        for c in self.comments:
            if c.description == ID3_V1_COMMENT_DESC:
                cmt = c.text
                # We prefer this one over ""
                break
            elif c.description == "":
                cmt = c.text
                # Keep searching in case we find the description eyeD3 uses.
        cmt = pack(encode(cmt), 30)

        if version != ID3_V1_0:
            track = self.track_num[0]
            if track is not None:
                cmt = cmt[0:28] + "\x00" + chr(int(track) & 0xff)
        tag += cmt

        if not self.genre or self.genre.id is None:
            genre = 12  # Other
        else:
            genre = self.genre.id
        tag += chr(genre & 0xff)

        assert(len(tag) == 128)

        mode = "rb+" if os.path.isfile(self.file_info.name) else "w+b"
        with open(self.file_info.name, mode) as tag_file:
            # Write the tag over top an original or append it.
            try:
                tag_file.seek(-128, 2)
                if tag_file.read(3) == "TAG":
                    tag_file.seek(-128, 2)
                else:
                    tag_file.seek(0, 2)
            except IOError:
                # File is smaller than 128 bytes.
                tag_file.seek(0, 2)

            tag_file.write(tag)
            tag_file.flush()

    def _render(self, version, curr_tag_size, max_padding_size):
        std_frames = []
        non_std_frames = []
        for f in self.frame_set.getAllFrames():
            try:
                _, fversion, _ = frames.ID3_FRAMES[f.id]
                if fversion in (version, ID3_V2):
                    std_frames.append(f)
                else:
                    non_std_frames.append(f)
            except KeyError:
                # Not a standard frame (ID3_FRAMES)
                try:
                    _, fversion, _ = frames.NONSTANDARD_ID3_FRAMES[f.id]
                    # but is it one we can handle.
                    if fversion in (version, ID3_V2):
                        std_frames.append(f)
                    else:
                        non_std_frames.append(f)
                except KeyError:
                    # Don't know anything about this pass it on for the error
                    # check there.
                    non_std_frames.append(f)

        if non_std_frames:
            # actually, they're not converted yet
            non_std_frames = self._convertFrames(std_frames, non_std_frames,
                                                 version)

        # Render all frames first so the data size is known for the tag header.
        frame_data = b""
        for f in std_frames + non_std_frames:
            frame_header = frames.FrameHeader(f.id, version)
            if f.header:
                frame_header.copyFlags(f.header)
            f.header = frame_header

            log.debug("Rendering frame: %s" % frame_header.id)
            raw_frame = f.render()
            log.debug("Rendered %d bytes" % len(raw_frame))
            frame_data += raw_frame

        log.debug("Rendered %d total frame bytes" % len(frame_data))

        # eyeD3 never writes unsync'd data
        self.header.unsync = False

        pending_size = TagHeader.SIZE + len(frame_data)
        if self.header.extended:
            # Using dummy data and padding, the actual size of this header
            # will be the same regardless, it's more about the flag bits
            tmp_ext_header_data = self.extended_header.render(version,
                                                              b"\x00", 0)
            pending_size += len(tmp_ext_header_data)

        padding_size = 0
        if pending_size > curr_tag_size:
            # current tag (minus padding) larger than the current (plus padding)
            padding_size = DEFAULT_PADDING
            rewrite_required = True
        else:
            padding_size = curr_tag_size - pending_size
            if max_padding_size is not None and padding_size > max_padding_size:
                padding_size = min(DEFAULT_PADDING, max_padding_size)
                rewrite_required = True
            else:
                rewrite_required = False

        assert(padding_size >= 0)
        log.debug("Using %d bytes of padding" % padding_size)

        # Extended header
        ext_header_data = b""
        if self.header.extended:
            log.debug("Rendering extended header")
            ext_header_data += self.extended_header.render(self.header.version,
                                                           frame_data,
                                                           padding_size)

        # Render the tag header.
        total_size = pending_size + padding_size
        log.debug("Rendering %s tag header with size %d" %
                  (versionToString(version),
                   total_size - TagHeader.SIZE))
        header_data = self.header.render(total_size - TagHeader.SIZE)

        # Assemble the entire tag.
        tag_data = b"%(tag_header)s%(ext_header)s%(frames)s" % \
                   {"tag_header": header_data,
                    "ext_header": ext_header_data,
                    "frames": frame_data,
                    }
        assert(len(tag_data) == (total_size - padding_size))
        return (rewrite_required, tag_data, "\x00" * padding_size)

    def _saveV2Tag(self, version, encoding, max_padding):
        self._raiseIfReadonly()

        assert(version[0] == 2 and version[1] != 2)

        log.debug("Rendering tag version: %s" % versionToString(version))

        file_exists = os.path.exists(self.file_info.name)

        if encoding:
            # Any invalid encoding is going to get coersed to a valid value
            # when the frame is rendered.
            for f in self.frame_set.getAllFrames():
                f.encoding = frames.stringToEncoding(encoding)

        curr_tag_size = 0

        if file_exists:
            # We may be converting from 1.x to 2.x so we need to find any
            # current v2.x tag otherwise we're gonna hork the file.
            # This also resets all offsets, state, etc. and makes me feel safe.
            tmp_tag = Tag()
            if tmp_tag.parse(self.file_info.name, ID3_V2):
                log.debug("Found current v2.x tag:")
                curr_tag_size = tmp_tag.file_info.tag_size
                log.debug("Current tag size: %d" % curr_tag_size)

            rewrite_required, tag_data, padding = self._render(version,
                                                               curr_tag_size,
                                                               max_padding)
            log.debug("Writing %d bytes of tag data and %d bytes of "
                      "padding" % (len(tag_data), len(padding)))
            if rewrite_required:
                # Open tmp file
                with tempfile.NamedTemporaryFile("wb", delete=False) \
                        as tmp_file:
                    tmp_file.write(tag_data + padding)

                    # Copy audio data in chunks
                    with open(self.file_info.name, "rb") as tag_file:
                        if curr_tag_size != 0:
                            seek_point = curr_tag_size
                        else:
                            seek_point = 0
                        log.debug("Seeking to beginning of audio data, "
                                  "byte %d (%x)" % (seek_point, seek_point))
                        tag_file.seek(seek_point)
                        chunkCopy(tag_file, tmp_file)

                    tmp_file.flush()

                # Move tmp to orig.
                shutil.copyfile(tmp_file.name, self.file_info.name)
                os.unlink(tmp_file.name)

            else:
                with open(self.file_info.name, "r+b") as tag_file:
                    tag_file.write(tag_data + padding)

        else:
            _, tag_data, padding = self._render(version, 0, None)
            with open(self.file_info.name, "wb") as tag_file:
                tag_file.write(tag_data + padding)

        log.debug("Tag write complete. Updating FileInfo state.")
        self.file_info.tag_size = len(tag_data) + len(padding)

    def _convertFrames(self, std_frames, convert_list, version):
        '''Maps frame imcompatibilies between ID3 v2.3 and v2.4.
        The items in ``std_frames`` need no conversion, but the list/frames
        may be edited if necessary (e.g. a converted frame replaces a frame
        in the list).  The items in ``convert_list`` are the frames to convert
        and return. The ``version`` is the target ID3 version.'''
        from . import versionToString
        from .frames import (DATE_FIDS, DEPRECATED_DATE_FIDS,
                             DateFrame, TextFrame)
        converted_frames = []
        flist = list(convert_list)

        # Date frame conversions.
        date_frames = {}
        for f in flist:
            if version == ID3_V2_4:
                if f.id in DEPRECATED_DATE_FIDS:
                    date_frames[f.id] = f
            else:
                if f.id in DATE_FIDS:
                    date_frames[f.id] = f

        if date_frames:
            if version == ID3_V2_4:
                if "TORY" in date_frames or "XDOR" in date_frames:
                    # XDOR -> TDOR (full date)
                    # TORY -> TDOR (year only)
                    date = self._getV23OrignalReleaseDate()
                    if date:
                        converted_frames.append(DateFrame("TDOR", date))
                    for fid in ("TORY", "XDOR"):
                        if fid in flist:
                            flist.remove(date_frames[fid])
                            del date_frames[fid]

                # TYER, TDAT, TIME -> TDRC
                if ("TYER" in date_frames or "TDAT" in date_frames or
                        "TIME" in date_frames):
                    date = self._getV23RecordingDate()
                    if date:
                        converted_frames.append(DateFrame("TDRC", date))
                    for fid in ["TYER", "TDAT", "TIME"]:
                        if fid in date_frames:
                            flist.remove(date_frames[fid])
                            del date_frames[fid]

            elif version == ID3_V2_3:
                if "TDOR" in date_frames:
                    date = date_frames["TDOR"].date
                    if date:
                        converted_frames.append(DateFrame("TORY",
                                                          unicode(date.year)))
                    flist.remove(date_frames["TDOR"])
                    del date_frames["TDOR"]

                if "TDRC" in date_frames:
                    date = date_frames["TDRC"].date

                    if date:
                        converted_frames.append(DateFrame("TYER",
                                                          unicode(date.year)))
                        if None not in (date.month, date.day):
                            date_str = u"%s%s" %\
                                    (str(date.day).rjust(2, "0"),
                                     str(date.month).rjust(2, "0"))
                            converted_frames.append(TextFrame("TDAT", date_str))
                        if None not in (date.hour, date.minute):
                            date_str = u"%s%s" %\
                                    (str(date.hour).rjust(2, "0"),
                                     str(date.minute).rjust(2, "0"))
                            converted_frames.append(TextFrame("TIME", date_str))

                    flist.remove(date_frames["TDRC"])
                    del date_frames["TDRC"]

                if "TDRL" in date_frames:
                    # TDRL -> XDOR
                    date = date_frames["TDRL"].date
                    if date:
                        converted_frames.append(DateFrame("XDOR", str(date)))
                    flist.remove(date_frames["TDRL"])
                    del date_frames["TDRL"]

            # All other date frames have no conversion
            for fid in date_frames:
                log.warning("%s frame being dropped due to conversion to %s" %
                            (fid, versionToString(version)))
                flist.remove(date_frames[fid])

        # Convert sort order frames 2.3 (XSO*) <-> 2.4 (TSO*)
        prefix = "X" if version == ID3_V2_4 else "T"
        fids = ["%s%s" % (prefix, suffix) for suffix in ["SOA", "SOP", "SOT"]]
        soframes = [f for f in flist if f.id in fids]

        for frame in soframes:
            frame.id = ("X" if prefix == "T" else "T") + frame.id[1:]
            flist.remove(frame)
            converted_frames.append(frame)

        # TSIZ (v2.3) are completely deprecated, remove them
        if version == ID3_V2_4:
            flist = [f for f in flist if f.id != "TSIZ"]

        # TSST (v2.4) --> TIT3 (2.3)
        if version == ID3_V2_3 and "TSST" in [f.id for f in flist]:
            tsst_frame = [f for f in flist if f.id == "TSST"][0]
            flist.remove(tsst_frame)
            tsst_frame = frames.UserTextFrame(
                    description=u"Subtitle (converted)", text=tsst_frame.text)
            converted_frames.append(tsst_frame)

        # Raise an error for frames that could not be converted.
        if len(flist) != 0:
            unconverted = ", ".join([f.id for f in flist])
            raise TagException("Unable to covert the following frames to "
                               "version %s: %s" % (versionToString(version),
                                                   unconverted))

        # Some frames in converted_frames may replace/edit frames in std_frames.
        for cframe in converted_frames:
            for sframe in std_frames:
                if cframe.id == sframe.id:
                    std_frames.remove(sframe)

        return converted_frames

    @staticmethod
    def remove(filename, version=ID3_ANY_VERSION, preserve_file_time=False):
        retval = False

        if version[0] & ID3_V1[0]:
            # ID3 v1.x
            tag = Tag()
            with open(filename, "r+b") as tag_file:
                found = tag.parse(tag_file, ID3_V1)
                if found:
                    tag_file.seek(-128, 2)
                    log.debug("Removing ID3 v1.x Tag")
                    tag_file.truncate()
                    retval |= True

        if version[0] & ID3_V2[0]:
            tag = Tag()
            with open(filename, "rb") as tag_file:
                found = tag.parse(tag_file, ID3_V2)
                if found:
                    log.debug("Removing ID3 %s tag" %
                              versionToString(tag.version))
                    tag_file.seek(tag.file_info.tag_size)

                    # Open tmp file
                    with tempfile.NamedTemporaryFile("wb", delete=False) \
                            as tmp_file:
                        chunkCopy(tag_file, tmp_file)

                    # Move tmp to orig
                    shutil.copyfile(tmp_file.name, filename)
                    os.unlink(tmp_file.name)

                    retval |= True

        if preserve_file_time and retval and None not in (tag.file_info.atime,
                                                          tag.file_info.mtime):
            tag.file_info.touch((tag.file_info.atime, tag.file_info.mtime))

        return retval

    @property
    def chapters(self):
        return self._chapters

    @property
    def table_of_contents(self):
        return self._tocs

    @property
    def album_type(self):
        if TXXX_ALBUM_TYPE in self.user_text_frames:
            return self.user_text_frames.get(TXXX_ALBUM_TYPE).text
        else:
            return None

    @album_type.setter
    def album_type(self, t):
        if not t:
            self.user_text_frames.remove(TXXX_ALBUM_TYPE)
        elif t in ALBUM_TYPE_IDS:
            self.user_text_frames.set(t, TXXX_ALBUM_TYPE)
        else:
            raise ValueError("Invalid album_type: %s" % t)

    @property
    def artist_origin(self):
        '''Returns a 3-tuple: (city, state, country) Any may be ``None``.'''
        if TXXX_ARTIST_ORIGIN in self.user_text_frames:
            origin = self.user_text_frames.get(TXXX_ARTIST_ORIGIN).text
            vals = origin.split('\t')
        else:
            vals = [None] * 3

        vals.extend([None] * (3 - len(vals)))
        vals = [None if not v else v for v in vals]
        assert(len(vals) == 3)
        return vals

    @artist_origin.setter
    def artist_origin(self, city, state, country):
        vals = (city, state, country)
        vals = [None if not v else v for v in vals]
        if vals == (None, None, None):
            self.user_text_frames.remove(TXXX_ARTIST_ORIGIN)
        else:
            assert(len(vals) == 3)
            self.user_text_frames.set('\t'.join(vals), TXXX_ARTIST_ORIGIN)

    def frameiter(self, fids=None):
        '''A iterator for tag frames. If ``fids`` is passed it must be a list
        of frame IDs to filter and return.'''
        fids = fids or []
        fids = [(b(f, ascii_encode)
            if isinstance(f, UnicodeType) else f) for f in fids]
        for f in self.frame_set.getAllFrames():
            if not fids or f.id in fids:
                yield f


class FileInfo:
    '''
    This class is for storing information about a parsed file. It containts info
    such as the filename, original tag size, and amount of padding; all of which
    can make rewriting faster.
    '''
    def __init__(self, file_name):
        from .. import LOCAL_FS_ENCODING

        if type(file_name) is unicode:
            self.name = file_name
        else:
            try:
                self.name = unicode(file_name, LOCAL_FS_ENCODING)
            except UnicodeDecodeError:
                # Work around the local encoding not matching that of a mounted
                # filesystem
                log.warning(u"Mismatched file system encoding for file '%s'" %
                            repr(file_name))
                self.name = file_name

        self.tag_size = 0  # This includes the padding byte count.
        self.tag_padding_size = 0

        self.initStatTimes()

    def initStatTimes(self):
        try:
            s = os.stat(self.name)
        except OSError:
            self.atime, self.mtime = None, None
        else:
            self.atime, self.mtime = s.st_atime, s.st_mtime

    def touch(self, times):
        '''times is a 2-tuple of (atime, mtime).'''
        os.utime(self.name, times)
        self.initStatTimes()


class AccessorBase(object):
    def __init__(self, fid, fs, match_func=None):
        self._fid = fid
        self._fs = fs
        self._match_func = match_func

    def __iter__(self):
        for f in self._fs[self._fid] or []:
            yield f

    def __len__(self):
        return len(self._fs[self._fid] or [])

    def __getitem__(self, i):
        frames = self._fs[self._fid]
        if not frames:
            raise IndexError("list index out of range")
        return frames[i]

    def get(self, *args, **kwargs):
        for frame in self._fs[self._fid] or []:
            if self._match_func(frame, *args, **kwargs):
                return frame
        return None

    def remove(self, *args, **kwargs):
        '''Returns the removed item or ``None`` if not found.'''
        fid_frames = self._fs[self._fid] or []
        for frame in fid_frames:
            if self._match_func(frame, *args, **kwargs):
                fid_frames.remove(frame)
                return frame
        return None


class DltAccessor(AccessorBase):
    def __init__(self, FrameClass, fid, fs):
        def match_func(frame, description, lang=DEFAULT_LANG):
            return frame.description == description and frame.lang == lang

        super(DltAccessor, self).__init__(fid, fs, match_func)
        self.FrameClass = FrameClass

    @requireUnicode(1, 2)
    def set(self, text, description=u"", lang=DEFAULT_LANG):
        lang = lang or DEFAULT_LANG
        for f in self._fs[self._fid] or []:
            if f.description == description and f.lang == lang:
                # Exists, update text
                f.text = text
                return f

        new_frame = self.FrameClass(description=description, lang=lang,
                                    text=text)
        self._fs[self._fid] = new_frame
        return new_frame

    @requireUnicode(1)
    def remove(self, description, lang=DEFAULT_LANG):
        return super(DltAccessor, self).remove(description,
                                               lang=lang or DEFAULT_LANG)

    @requireUnicode(1)
    def get(self, description, lang=DEFAULT_LANG):
        return super(DltAccessor, self).get(description,
                                            lang=lang or DEFAULT_LANG)


class CommentsAccessor(DltAccessor):
    def __init__(self, fs):
        super(CommentsAccessor, self).__init__(frames.CommentFrame,
                                               frames.COMMENT_FID, fs)


class LyricsAccessor(DltAccessor):
    def __init__(self, fs):
        super(LyricsAccessor, self).__init__(frames.LyricsFrame,
                                             frames.LYRICS_FID, fs)


class ImagesAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, description):
            return frame.description == description
        super(ImagesAccessor, self).__init__(frames.IMAGE_FID, fs, match_func)

    @requireUnicode("description")
    def set(self, type_, img_data, mime_type, description=u"", img_url=None):
        '''Add an image of ``type_`` (a type constant from ImageFrame).
        The ``img_data`` is either bytes or ``None``. In the latter case
        ``img_url`` MUST be the URL to the image. In this case ``mime_type``
        is ignored and "-->" is used to signal this as a link and not data
        (per the ID3 spec).'''
        if not img_data and not img_url:
            raise ValueError("img_url MUST not be none when no image data")

        mime_type = mime_type if img_data else frames.ImageFrame.URL_MIME_TYPE

        images = self._fs[frames.IMAGE_FID] or []
        for img in images:
            if img.description == description:
                # update
                if not img_data:
                    img.image_url = img_url
                    img.image_data = None
                    img.mime_type = frames.ImageFrame.URL_MIME_TYPE
                else:
                    img.image_url = None
                    img.image_data = img_data
                    img.mime_type = mime_type
                img.picture_type = type_
                return img

        img_frame = frames.ImageFrame(description=description,
                                      image_data=img_data,
                                      image_url=img_url,
                                      mime_type=mime_type,
                                      picture_type=type_)
        self._fs[frames.IMAGE_FID] = img_frame
        return img_frame

    @requireUnicode(1)
    def remove(self, description):
        return super(ImagesAccessor, self).remove(description)

    @requireUnicode(1)
    def get(self, description):
        return super(ImagesAccessor, self).get(description)


class ObjectsAccessor(AccessorBase):
    def __init__(self, fs):

        def match_func(frame, description):
            return frame.description == description
        super(ObjectsAccessor, self).__init__(frames.OBJECT_FID, fs, match_func)

    @requireUnicode("description", "filename")
    def set(self, data, mime_type, description=u"", filename=u""):
        objects = self._fs[frames.OBJECT_FID] or []
        for obj in objects:
            if obj.description == description:
                # update
                obj.object_data = data
                obj.mime_type = mime_type
                obj.filename = filename
                return obj

        obj_frame = frames.ObjectFrame(description=description,
                                       filename=filename,
                                       object_data=data,
                                       mime_type=mime_type)
        self._fs[frames.OBJECT_FID] = obj_frame
        return obj_frame

    @requireUnicode(1)
    def remove(self, description):
        return super(ObjectsAccessor, self).remove(description)

    @requireUnicode(1)
    def get(self, description):
        return super(ObjectsAccessor, self).get(description)


class PrivatesAccessor(AccessorBase):
    def __init__(self, fs):

        def match_func(frame, owner_id):
            return frame.owner_id == owner_id
        super(PrivatesAccessor, self).__init__(frames.PRIVATE_FID, fs,
                                               match_func)

    def set(self, data, owner_id):
        priv_frames = self._fs[frames.PRIVATE_FID] or []
        for f in priv_frames:
            if f.owner_id == owner_id:
                # update
                f.owner_data = data
                return f

        priv_frame = frames.PrivateFrame(owner_id=owner_id,
                                         owner_data=data)
        self._fs[frames.PRIVATE_FID] = priv_frame
        return priv_frame

    def remove(self, owner_id):
        return super(PrivatesAccessor, self).remove(owner_id)

    def get(self, owner_id):
        return super(PrivatesAccessor, self).get(owner_id)


class UserTextsAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, description):
            return frame.description == description
        super(UserTextsAccessor, self).__init__(frames.USERTEXT_FID, fs,
                                                match_func)

    @requireUnicode(1, "description")
    def set(self, text, description=u""):
        flist = self._fs[frames.USERTEXT_FID] or []
        for utf in flist:
            if utf.description == description:
                # update
                utf.text = text
                return utf

        utf = frames.UserTextFrame(description=description,
                                   text=text)
        self._fs[frames.USERTEXT_FID] = utf
        return utf

    @requireUnicode(1)
    def remove(self, description):
        return super(UserTextsAccessor, self).remove(description)

    @requireUnicode(1)
    def get(self, description):
        return super(UserTextsAccessor, self).get(description)

    @requireUnicode(1)
    def __contains__(self, description):
        return bool(self.get(description))


class UniqueFileIdAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, owner_id):
            return frame.owner_id == owner_id
        super(UniqueFileIdAccessor, self).__init__(frames.UNIQUE_FILE_ID_FID,
                                                   fs, match_func)

    def set(self, data, owner_id):
        data = str(data)
        if len(data) > 64:
            raise TagException("UFID data must be 64 bytes or less")

        flist = self._fs[frames.UNIQUE_FILE_ID_FID] or []
        for f in flist:
            if f.owner_id == owner_id:
                # update
                f.uniq_id = data
                return f

        uniq_id_frame = frames.UniqueFileIDFrame(owner_id=owner_id,
                                                 uniq_id=data)
        self._fs[frames.UNIQUE_FILE_ID_FID] = uniq_id_frame
        return uniq_id_frame

    def remove(self, owner_id):
        return super(UniqueFileIdAccessor, self).remove(owner_id)

    def get(self, owner_id):
        return super(UniqueFileIdAccessor, self).get(owner_id)


class UserUrlsAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, description):
            return frame.description == description
        super(UserUrlsAccessor, self).__init__(frames.USERURL_FID, fs,
                                               match_func)

    @requireUnicode("description")
    def set(self, url, description=u""):
        flist = self._fs[frames.USERURL_FID] or []
        for uuf in flist:
            if uuf.description == description:
                # update
                uuf.url = url
                return uuf

        uuf = frames.UserUrlFrame(description=description, url=url)
        self._fs[frames.USERURL_FID] = uuf
        return uuf

    @requireUnicode(1)
    def remove(self, description):
        return super(UserUrlsAccessor, self).remove(description)

    @requireUnicode(1)
    def get(self, description):
        return super(UserUrlsAccessor, self).get(description)


class PopularitiesAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, email):
            return frame.email == email
        super(PopularitiesAccessor, self).__init__(frames.POPULARITY_FID, fs,
                                                   match_func)

    def set(self, email, rating, play_count):
        flist = self._fs[frames.POPULARITY_FID] or []
        for popm in flist:
            if popm.email == email:
                # update
                popm.rating = rating
                popm.count = play_count
                return popm

        popm = frames.PopularityFrame(email=email, rating=rating,
                                      count=play_count)
        self._fs[frames.POPULARITY_FID] = popm
        return popm

    def remove(self, email):
        return super(PopularitiesAccessor, self).remove(email)

    def get(self, email):
        return super(PopularitiesAccessor, self).get(email)


class ChaptersAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, element_id):
            return frame.element_id == element_id
        super(ChaptersAccessor, self).__init__(frames.CHAPTER_FID, fs,
                                               match_func)

    def set(self, element_id, times, offsets=(None, None), sub_frames=None):
        flist = self._fs[frames.CHAPTER_FID] or []
        for chap in flist:
            if chap.element_id == element_id:
                # update
                chap.times, chap.offsets = times, offsets
                if sub_frames:
                    chap.sub_frames = sub_frames
                return chap

        chap = frames.ChapterFrame(element_id=element_id,
                                   times=times, offsets=offsets,
                                   sub_frames=sub_frames)
        self._fs[frames.CHAPTER_FID] = chap
        return chap

    def remove(self, element_id):
        return super(ChaptersAccessor, self).remove(element_id)

    def get(self, element_id):
        return super(ChaptersAccessor, self).get(element_id)

    def __getitem__(self, elem_id):
        '''Overiding the index based __getitem__ for one indexed with chapter
        element IDs. These are stored in the tag's table of contents frames.'''
        for chapter in (self._fs[frames.CHAPTER_FID] or []):
            if chapter.element_id == elem_id:
                return chapter
        raise IndexError("chapter '%s' not found" % elem_id)


class TocAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, element_id):
            return frame.element_id == element_id
        super(TocAccessor, self).__init__(frames.TOC_FID, fs, match_func)

    def __iter__(self):
        tocs = list(self._fs[self._fid] or [])
        for toc_frame in tocs:
            # Find and put top level at the front of the list
            if toc_frame.toplevel:
                tocs.remove(toc_frame)
                tocs.insert(0, toc_frame)
                break

        for toc in tocs:
            yield toc

    @requireUnicode("description")
    def set(self, element_id, toplevel=False, ordered=True, child_ids=None,
            description=u""):
        flist = self._fs[frames.TOC_FID] or []

        # Enforce one top-level
        if toplevel:
            for toc in flist:
                if toc.toplevel:
                    raise ValueError("There may only be one top-level "
                                     "table of contents. Toc '%s' is current "
                                     "top-level." % toc.element_id)
        for toc in flist:
            if toc.element_id == element_id:
                # update
                toc.toplevel = toplevel
                toc.ordered = ordered
                toc.child_ids = child_ids
                toc.description = description
                return toc

        toc = frames.TocFrame(element_id=element_id, toplevel=toplevel,
                              ordered=ordered, child_ids=child_ids,
                              description=description)
        self._fs[frames.TOC_FID] = toc
        return toc

    def remove(self, element_id):
        return super(TocAccessor, self).remove(element_id)

    def get(self, element_id):
        return super(TocAccessor, self).get(element_id)

    def __getitem__(self, elem_id):
        '''Overiding the index based __getitem__ for one indexed with table
        of contents element IDs.'''
        for toc in (self._fs[frames.TOC_FID] or []):
            if toc.element_id == elem_id:
                return toc
        raise IndexError("toc '%s' not found" % elem_id)


class TagTemplate(string.Template):
    idpattern = r'[_a-z][_a-z0-9:]*'

    def __init__(self, pattern, path_friendly=True, dotted_dates=False):
        super(TagTemplate, self).__init__(pattern)
        self._path_friendly = path_friendly
        self._dotted_dates = dotted_dates

    def substitute(self, tag, zeropad=True):
        mapping = self._makeMapping(tag, zeropad)

        # Helper function for .sub()
        def convert(mo):
            named = mo.group('named')
            if named is not None:
                try:
                    if type(mapping[named]) is tuple:
                        func, args = mapping[named][0], mapping[named][1:]
                        return u'%s' % func(tag, named, *args)
                    # We use this idiom instead of str() because the latter
                    # will fail if val is a Unicode containing non-ASCII
                    return u'%s' % (mapping[named],)
                except KeyError:
                    return self.delimiter + named
            braced = mo.group('braced')
            if braced is not None:
                try:
                    if type(mapping[braced]) is tuple:
                        func, args = mapping[braced][0], mapping[braced][1:]
                        return u'%s' % func(tag, braced, *args)
                    return u'%s' % (mapping[braced],)
                except KeyError:
                    return self.delimiter + '{' + braced + '}'
            if mo.group('escaped') is not None:
                return self.delimiter
            if mo.group('invalid') is not None:
                return self.delimiter
            raise ValueError('Unrecognized named group in pattern',
                             self.pattern)

        name = self.pattern.sub(convert, self.template)
        return name.replace('/', '-') if self._path_friendly else name

    safe_substitute = substitute

    def _dates(self, tag, param):
        if param.startswith("release_"):
            date = tag.release_date
        elif param.startswith("recording_"):
            date = tag.recording_date
        elif param.startswith("original_release_"):
            date = tag.original_release_date
        else:
            date = tag.getBestDate(
                    prefer_recording_date=":prefer_recording" in param)

        if date and param.endswith(":year"):
            dstr = unicode(date.year)
        elif date:
            dstr = unicode(date)
        else:
            dstr = u""

        if self._dotted_dates:
            dstr = dstr.replace('-', '.')

        return dstr

    def _nums(self, num_tuple, param, zeropad):
        nn, nt = ((unicode(n) if n else None) for n in num_tuple)
        if zeropad:
            if nt:
                nt = nt.rjust(2, "0")
            nn = nn.rjust(len(nt) if nt else 2, "0")

        if param.endswith(":num"):
            return nn
        elif param.endswith(":total"):
            return nt
        else:
            raise ValueError("Unknown template param: %s" % param)

    def _track(self, tag, param, zeropad):
        return self._nums(tag.track_num, param, zeropad)

    def _disc(self, tag, param, zeropad):
        return self._nums(tag.disc_num, param, zeropad)

    def _file(self, tag, param):
        assert(param.startswith("file"))

        if param.endswith(":ext"):
            return os.path.splitext(tag.file_info.name)[1][1:]
        else:
            return tag.file_info.name

    def _makeMapping(self, tag, zeropad):
        return {"artist": tag.artist if tag else None,
                "album_artist": tag.album_artist if tag else None,
                "album": tag.album if tag else None,
                "title": tag.title if tag else None,
                "track:num": (self._track, zeropad) if tag else None,
                "track:total": (self._track, zeropad) if tag else None,
                "release_date": (self._dates,) if tag else None,
                "release_date:year": (self._dates,) if tag else None,
                "recording_date": (self._dates,) if tag else None,
                "recording_date:year": (self._dates,) if tag else None,
                "original_release_date": (self._dates,) if tag else None,
                "original_release_date:year": (self._dates,) if tag else None,
                "best_date": (self._dates,) if tag else None,
                "best_date:year": (self._dates,) if tag else None,
                "best_date:prefer_recording": (self._dates,) if tag else None,
                "best_date:prefer_release": (self._dates,) if tag else None,
                "best_date:prefer_recording:year": (self._dates,) if tag
                                                                  else None,
                "best_date:prefer_release:year": (self._dates,) if tag
                                                                   else None,
                "file": (self._file,) if tag else None,
                "file:ext": (self._file,) if tag else None,
                "disc:num": (self._disc, zeropad) if tag else None,
                "disc:total": (self._disc, zeropad) if tag else None,
               }

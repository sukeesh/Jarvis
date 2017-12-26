#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''Goslate: Free Google Translate API
'''
from __future__ import print_function
from __future__ import unicode_literals

import sys
import os
import json
import itertools
import functools
import time
import socket
import random
import re

try:
    # python 3
    from urllib.request import build_opener, Request, HTTPHandler, HTTPSHandler
    from urllib.parse import quote_plus, urlencode, unquote_plus, urljoin
    izip = zip

except ImportError:
    # python 2
    from urllib2 import build_opener, Request, HTTPHandler, HTTPSHandler
    from urllib import urlencode, unquote_plus, quote_plus
    from urlparse import urljoin
    from itertools import izip

try:
    import concurrent.futures
    _g_executor = concurrent.futures.ThreadPoolExecutor(max_workers=120)
except ImportError:
    _g_executor = None
    

__author__ = 'ZHUO Qiang'
__email__ = 'zhuo.qiang@gmail.com'
__copyright__ = "2013, http://zhuoqiang.me"
__license__ = "MIT"
__date__ = '2013-05-11'
__version_info__ = (1, 5, 1)
__version__ = '.'.join(str(i) for i in __version_info__)
__home__ = 'https://bitbucket.org/zhuoqiang/goslate'
__download__ = 'https://pypi.python.org/pypi/goslate'


try:
    unicode
except NameError:
    unicode = str
    
def _is_sequence(arg):
    return (not isinstance(arg, unicode)) and (
        not isinstance(arg, bytes)) and (
        hasattr(arg, "__getitem__") or hasattr(arg, "__iter__"))
    
def _is_bytes(arg):
    return isinstance(arg, bytes)


def _unwrapper_single_element(elements):
    if len(elements) == 1:
        return elements[0]
    return elements
        
    
class Error(Exception):
    '''Error type
    '''
    pass


_empty_comma = re.compile(r',(?=,)')

WRITING_NATIVE = ('trans',)
'''native target language writing system'''

WRITING_ROMAN = ('translit',)
'''romanlized writing system. only valid for some langauges, otherwise it outputs empty string'''

WRITING_NATIVE_AND_ROMAN = WRITING_NATIVE + WRITING_ROMAN
'''both native and roman writing. The output will be a tuple'''

class Goslate(object):
    '''All goslate API lives in this class

    You have to first create an instance of Goslate to use this API

    :param writing: The translation writing system. Currently 3 values are valid
    
                 - :const:`WRITING_NATIVE` for native writing system
                 - :const:`WRITING_ROMAN` for roman writing system
                 - :const:`WRITING_NATIVE_AND_ROMAN` for both native and roman writing system. output will be a tuple in this case
    
    :param opener: The url opener to be used for HTTP/HTTPS query.
                   If not provide, a default opener will be used.
                   For proxy support you should provide an ``opener`` with ``ProxyHandler``
    :type opener: `urllib2.OpenerDirector <http://docs.python.org/2/library/urllib2.html#urllib2.OpenerDirector>`_
        
    :param retry_times: how many times to retry when connection reset error occured. Default to 4
    :type retry_times: int
        
    :type max_workers: int

    :param timeout: HTTP request timeout in seconds
    :type timeout: int/float
    
    :param debug: Turn on/off the debug output
    :type debug: bool

    :param service_urls: google translate url list. URLs will be used randomly for better concurrent performance. For example ``['http://translate.google.com', 'http://translate.google.de']``
    :type service_urls: single string or a sequence of strings
    
    :param executor: the multi thread executor for handling batch input, default to a global ``futures.ThreadPoolExecutor`` instance with 120 max thead workers if ``futures`` is avalible. Set to None to disable multi thread support
    :type executor: ``futures.ThreadPoolExecutor``
    
    .. note:: multi thread worker relys on `futures <https://pypi.python.org/pypi/futures>`_, if it is not avalible, ``goslate`` will work under single thread mode
    
    :Example:

        >>> import goslate
        >>> 
        >>> # Create a Goslate instance first
        >>> gs = goslate.Goslate()
        >>> 
        >>> # You could get all supported language list through get_languages
        >>> languages = gs.get_languages()
        >>> print(languages['en'])
        English
        >>> 
        >>> # Tranlate English into German
        >>> print(gs.translate('Hello', 'de'))
        Hallo
        >>> # Detect the language of the text
        >>> print(gs.detect('some English words'))
        en
        >>> # Get goslate object dedicated for romanlized translation (romanlization)
        >>> gs_roman = goslate.Goslate(WRITING_ROMAN)
        >>> print(gs_roman.translate('hello', 'zh'))
        Nín hǎo
    '''

    
    _MAX_LENGTH_PER_QUERY = 1800

    def __init__(self, writing=WRITING_NATIVE, opener=None, retry_times=4, executor=_g_executor,
                 timeout=4, service_urls=('http://translate.google.com',), debug=False):
        self._DEBUG = debug
        self._MIN_TASKS_FOR_CONCURRENT = 2
        self._opener = opener
        self._languages = None
        self._TIMEOUT = timeout
        if not self._opener:
            debuglevel = self._DEBUG and 1 or 0
            self._opener = build_opener(
                HTTPHandler(debuglevel=debuglevel),
                HTTPSHandler(debuglevel=debuglevel))
        
        self._RETRY_TIMES = retry_times
        self._executor = executor
        self._writing = writing
        if _is_sequence(service_urls):
            self._service_urls = service_urls
        else:
            self._service_urls = (service_urls,)

    def _open_url(self, url):
        if len(url) > self._MAX_LENGTH_PER_QUERY+100:
            raise Error('input too large')

        # Google forbits urllib2 User-Agent: Python-urllib/2.7
        request = Request(url, headers={'User-Agent':'Mozilla/4.0'})

        exception = None
        # retry when get (<class 'socket.error'>, error(54, 'Connection reset by peer')
        for i in range(self._RETRY_TIMES):
            try:
                response = self._opener.open(request, timeout=self._TIMEOUT)
                response_content = response.read().decode('utf-8')
                if self._DEBUG:
                    print('GET Response body:{}'.format(response_content))
                return response_content
            except socket.error as e:
                if self._DEBUG:
                    import threading
                    print(threading.currentThread(), e)
                if 'Connection reset by peer' not in str(e):
                    raise e
                exception = e
                time.sleep(0.0001)
        raise exception
    

    def _execute(self, tasks):
        first_tasks = [next(tasks, None) for i in range(self._MIN_TASKS_FOR_CONCURRENT)]
        tasks = (task for task in itertools.chain(first_tasks, tasks) if task)

        if not first_tasks[-1] or not self._executor:
            for each in tasks:
                yield each()
        else:
            exception = None
            for each in [self._executor.submit(t) for t in tasks]:
                if exception:
                    each.cancel()
                else:
                    exception = each.exception()
                    if not exception:
                        yield each.result()

            if exception:
                raise exception


    def _basic_translate(self, text, target_language, source_language):
        # assert _is_bytes(text)
        
        if not target_language:
            raise Error('invalid target language')

        if not text.strip():
            return tuple(u'' for i in range(len(self._writing))) , unicode(target_language)

        # Browser request for 'hello world' is:
        # http://translate.google.com/translate_a/t?client=t&hl=en&sl=en&tl=zh-CN&ie=UTF-8&oe=UTF-8&multires=1&prev=conf&psl=en&ptl=en&otf=1&it=sel.2016&ssel=0&tsel=0&prev=enter&oc=3&ssel=0&tsel=0&sc=1&text=hello%20world
        
        # 2015-04: google had changed service, it is now:
        # https://translate.google.com/translate_a/single?client=z&sl=en&tl=zh-CN&ie=UTF-8&oe=UTF-8&dt=t&dt=rm&q=hello%20world
        # dt=t: translate
        # dt=rm: romanlized writing, like Chinese Pinyin

        # TODO: we could randomly choose one of the google domain URLs for concurrent support
        GOOGLE_TRASLATE_URL = urljoin(random.choice(self._service_urls), '/translate_a/single')
        GOOGLE_TRASLATE_PARAMETERS = {
            'client': 'a',
            'sl': source_language,
            'tl': target_language,
            'ie': 'UTF-8',
            'oe': 'UTF-8',
            'dt': 't',
            'q': text,
            }

        url = '?'.join((GOOGLE_TRASLATE_URL, urlencode(GOOGLE_TRASLATE_PARAMETERS)))
        if 'translit' in self._writing:
            url += '&dt=rm'
        
        response_content = self._open_url(url)
        raw_data = json.loads(_empty_comma.subn('', response_content)[0].replace(u'\xA0', u' ').replace('[,', '[1,'))
        data = {'src': raw_data[-1][0][0]}
        
        if raw_data[0][-1][0] == 1: # roman writing
            data['translit'] = raw_data[0][-1][1]
            data['trans'] = u''.join(i[0] for i in raw_data[0][:-1])
        else:
            data['translit'] = u''
            data['trans'] = u''.join(i[0] for i in raw_data[0])
            
        translation = tuple(data[part] for part in self._writing)
        
        detected_source_language = data['src']
        return translation, detected_source_language


    def get_languages(self):
        '''Discover supported languages

        It returns iso639-1 language codes for
        `supported languages <https://developers.google.com/translate/v2/using_rest#language-params>`_
        for translation. Some language codes also include a country code, like zh-CN or zh-TW.

        .. note:: It only queries Google once for the first time and use cached result afterwards

        :returns: a dict of all supported language code and language name mapping ``{'language-code', 'Language name'}``

        :Example:

        >>> languages = Goslate().get_languages()
        >>> assert 'zh' in languages
        >>> print(languages['zh'])
        Chinese

        '''
        if self._languages:
            return self._languages

        GOOGLE_TRASLATOR_URL = 'http://translate.google.com/translate_a/l'
        GOOGLE_TRASLATOR_PARAMETERS = {
            'client': 't',
            }

        url = '?'.join((GOOGLE_TRASLATOR_URL, urlencode(GOOGLE_TRASLATOR_PARAMETERS)))
        response_content = self._open_url(url)
        data = json.loads(response_content)

        languages = data['sl']
        languages.update(data['tl'])
        if 'auto' in languages:
            del languages['auto']
        if 'zh' not in languages:
            languages['zh'] = 'Chinese'
        self._languages = languages
        return self._languages


    _SEPERATORS = [quote_plus(i.encode('utf-8')) for i in
                   u'.!?,;。，？！:："“”’‘#$%&()（）*×+/<=>@＃￥[\]…［］^`{|}｛｝～~\n\r\t ']

    def _translate_single_text(self, text, target_language, source_lauguage):
        assert _is_bytes(text)
        def split_text(text):
            start = 0
            text = quote_plus(text)
            length = len(text)
            while (length - start) > self._MAX_LENGTH_PER_QUERY:
                for seperator in self._SEPERATORS:
                    index = text.rfind(seperator, start, start+self._MAX_LENGTH_PER_QUERY)
                    if index != -1:
                        break
                else:
                    raise Error('input too large')
                end = index + len(seperator)
                yield unquote_plus(text[start:end])
                start = end

            yield unquote_plus(text[start:])

        def make_task(text):
            return lambda: self._basic_translate(text, target_language, source_lauguage)[0]

        results = list(self._execute(make_task(i) for i in split_text(text)))
        return tuple(''.join(i[n] for i in results) for n in range(len(self._writing)))


    def translate(self, text, target_language, source_language='auto'):
        '''Translate text from source language to target language

        .. note::
        
         - Input all source strings at once. Goslate will batch and fetch concurrently for maximize speed.
         - `futures <https://pypi.python.org/pypi/futures>`_ is required for best performance.
         - It returns generator on batch input in order to better fit pipeline architecture

        :param text: The source text(s) to be translated. Batch translation is supported via sequence input
        :type text: UTF-8 str; unicode; string sequence (list, tuple, iterator, generator)

        :param target_language: The language to translate the source text into.
         The value should be one of the language codes listed in :func:`get_languages`
        :type target_language: str; unicode

        :param source_language: The language of the source text.
                                The value should be one of the language codes listed in :func:`get_languages`.
                                If a language is not specified,
                                the system will attempt to identify the source language automatically.
        :type source_language: str; unicode
        
        :returns: the translated text(s)
        
          - unicode: on single string input
          - generator of unicode: on batch input of string sequence
          - tuple: if WRITING_NATIVE_AND_ROMAN is specified, it will return tuple/generator for tuple (u"native", u"roman format")

        :raises:
         - :class:`Error` ('invalid target language') if target language is not set
         - :class:`Error` ('input too large') if input a single large word without any punctuation or space in between


        :Example:
        
         >>> gs = Goslate()
         >>> print(gs.translate('Hello World', 'de'))
         Hallo Welt
         >>> 
         >>> for i in gs.translate(['good', u'morning'], 'de'):
         ...     print(i)
         ...
         gut
         Morgen

        To output romanlized translation

        :Example:
        
         >>> gs_roman = Goslate(WRITING_ROMAN)
         >>> print(gs_roman.translate('Hello', 'zh'))
         Nín hǎo
        
        '''


        if not target_language:
            raise Error('invalid target language')

        if not source_language:
            source_language = 'auto'
        
        if target_language.lower() == 'zh':
            target_language = 'zh-CN'
            
        if source_language.lower() == 'zh':
            source_language = 'zh-CN'
            
        if not _is_sequence(text):
            if isinstance(text, unicode):
                text = text.encode('utf-8')
            return _unwrapper_single_element(self._translate_single_text(text, target_language, source_language))

        JOINT = u'\u26ff'
        UTF8_JOINT = (u'\n%s\n' % JOINT).encode('utf-8')

        def join_texts(texts):
            def convert_to_utf8(texts):
                for i in texts:
                    if isinstance(i, unicode):
                        i = i.encode('utf-8')
                    yield i.strip()
                
            texts = convert_to_utf8(texts)
            text = next(texts)
            for i in texts:
                new_text = UTF8_JOINT.join((text, i))
                if len(quote_plus(new_text)) < self._MAX_LENGTH_PER_QUERY:
                    text = new_text
                else:
                    yield text
                    text = i
            yield text


        def make_task(text):
            def task():
                r = self._translate_single_text(text, target_language, source_language)
                r = tuple([i.strip('\n') for i in n.split(JOINT)] for n in r)
                return izip(*r)
                # return r[0]
            return task
                
        return (_unwrapper_single_element(i) for i in
                itertools.chain.from_iterable(self._execute(make_task(i) for i in join_texts(text))))


    def _detect_language(self, text):
        if _is_bytes(text):
            text = text.decode('utf-8')
        return self._basic_translate(text[:50].encode('utf-8'), 'en', 'auto')[1]


    def detect(self, text):
        '''Detect language of the input text

        .. note::
        
         - Input all source strings at once. Goslate will detect concurrently for maximize speed.
         - `futures <https://pypi.python.org/pypi/futures>`_ is required for best performance.
         - It returns generator on batch input in order to better fit pipeline architecture.

        :param text: The source text(s) whose language you want to identify.
                     Batch detection is supported via sequence input
        :type text: UTF-8 str; unicode; sequence of string
        :returns: the language code(s)
        
          - unicode: on single string input
          - generator of unicode: on batch input of string sequence

        :raises: :class:`Error` if parameter type or value is not valid

        Example::
        
         >>> gs = Goslate()
         >>> print(gs.detect('hello world'))
         en
         >>> for i in gs.detect([u'hello', 'Hallo']):
         ...     print(i)
         ...
         en
         de

        '''
        if _is_sequence(text):
            return self._execute(functools.partial(self._detect_language, i) for i in text)
        return self._detect_language(text)


    def lookup_dictionary(
            self, text, target_language, source_language='auto',
            examples=False, 
            etymology=False,
            pronunciation=False,
            related_words=False,
            synonyms=False,
            antonyms=False,
            output_language=None):
        '''Lookup detail meaning for single word/phrase

        .. note::
        
         - Do not input sequence of texts

        :param text: The source word/phrase(s) you want to lookup.
        :type text: UTF-8 str
        
        :param target_language: The language to translate the source text into.
         The value should be one of the language codes listed in :func:`get_languages`
        :type target_language: str; unicode

        :param source_language: The language of the source text.
                                The value should be one of the language codes listed in :func:`get_languages`.
                                If a language is not specified,
                                the system will attempt to identify the source language automatically.
        :type source_language: str; unicode
        
        :param examples: include example sentences or not
        :param pronunciation: include pronunciation in roman writing or not
        :param related_words: include related words or not
        :param output_language: the dictionary's own language, default to English.
        
        :returns: a complex list structure contains multiple translation meanings for this word/phrase and detail explaination.
        '''

        if not target_language:
            raise Error('invalid target language')

        if not text.strip():
            return tuple(u'' for i in range(len(self._writing))) , unicode(target_language)

        # Browser request for 'hello world' is:
        # http://translate.google.com/translate_a/t?client=t&hl=en&sl=en&tl=zh-CN&ie=UTF-8&oe=UTF-8&multires=1&prev=conf&psl=en&ptl=en&otf=1&it=sel.2016&ssel=0&tsel=0&prev=enter&oc=3&ssel=0&tsel=0&sc=1&text=hello%20world
        
        # TODO: we could randomly choose one of the google domain URLs for concurrent support
        GOOGLE_TRASLATE_URL = urljoin(random.choice(self._service_urls), '/translate_a/single')
        parameters = [
            ('client', 'a'),
            ('sl', source_language),
            ('tl', target_language),
            ('ie', 'UTF-8'),
            ('oe', 'UTF-8'),
            ('dt', 't'),
            ('q', text),
            
            ('dt', 'bd'), # dictionry
        ]
            
        if output_language:
            parameters.append(('hl', output_language))
        if examples:
            parameters.append(('dt', 'ex'))
        if related_words:
            parameters.append(('dt', 'rw'))
        if pronunciation:
            parameters.append(('dt', 'rm'))
        if synonyms:
            parameters.append(('dt', 'ss'))
        if antonyms:
            parameters.append(('dt', 'at'))
            
        # ('dt', 'ld'), # possibility ?
        # ('dt', 'md'), # long definiation
        # ('dt', 'qca'), # possiblility?
        # 'otf': '1', # ?
        # ('ssel': '1'), # ?
        # ('tsel', '1'), # ?
        # 'kc': '6', # ?
        # 'tk': 522243|913459, #?

        # if source_pronunciation:
        #     parameters.append(('srcrom', '1'))
        
        url = '?'.join((GOOGLE_TRASLATE_URL, urlencode(parameters)))
        # print(url)

        response_content = self._open_url(url)
        raw_data = json.loads(_empty_comma.subn('', response_content)[0].replace(u'\xA0', u' ').replace('[,', '[1,'))
        return raw_data
    
    
def _main(argv):
    import optparse

    usage = "usage: %prog [options] <file1 file2 ...>\n<stdin> will be used as input source if no file specified."
    
    parser = optparse.OptionParser(usage=usage, version="%%prog %s @ Copyright %s" % (__version__, __copyright__))
    parser.add_option('-t', '--target-language', metavar='zh-CN',
                      help='specify target language to translate the source text into')
    parser.add_option('-s', '--source-language', default='auto', metavar='en',
                      help='specify source language, if not provide it will identify the source language automatically')
    parser.add_option('-i', '--input-encoding', default=sys.getfilesystemencoding(), metavar='utf-8',
                      help='specify input encoding, default to current console system encoding')
    parser.add_option('-o', '--output-encoding', default=sys.getfilesystemencoding(), metavar='utf-8',
                      help='specify output encoding, default to current console system encoding')
    parser.add_option('-r', '--roman', action="store_true",
                      help='change translation writing to roman (e.g.: output pinyin instead of Chinese charactors for Chinese. It only valid for some of the target languages)')

    
    options, args = parser.parse_args(argv[1:])
    
    if not options.target_language:
        print('Error: missing target language!')
        parser.print_help()
        return
    
    writing = WRITING_NATIVE
    if options.roman:
        writing = WRITING_ROMAN
    
    gs = Goslate(writing=writing)
    import fileinput
    # inputs = fileinput.input(args, mode='rU', openhook=fileinput.hook_encoded(options.input_encoding))
    inputs = fileinput.input(args, mode='rb')
    inputs = (i.decode(options.input_encoding) for i in inputs)
    outputs = gs.translate(inputs, options.target_language, options.source_language)
    for i in outputs:
        sys.stdout.write((i+u'\n').encode(options.output_encoding))
        sys.stdout.flush()
    
    
if __name__ == '__main__':
    try:
        _main(sys.argv)
    except:
        error = sys.exc_info()[1]
        if len(str(error)) > 2:
            print(error)

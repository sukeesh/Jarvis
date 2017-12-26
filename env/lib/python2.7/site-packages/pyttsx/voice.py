'''
Voice metadata definition.

Copyright (c) 2009, 2013 Peter Parente

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
'''
class Voice(object):
    def __init__(self, id, name=None, languages=[], gender=None, age=None):
        self.id = id
        self.name = name
        self.languages = languages
        self.gender = gender
        self.age = age

    def __str__(self):
        return '''<Voice id=%(id)s
          name=%(name)s
          languages=%(languages)s
          gender=%(gender)s
          age=%(age)s>''' % self.__dict__
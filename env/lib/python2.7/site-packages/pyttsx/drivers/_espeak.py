'''espeak.py a thin ctypes wrapper for the espeak dll

Gary Bishop
July 2007
Modified October 2007 for the version 2 interface to espeak and more pythonic interfaces

Free for any use.
'''

import ctypes
from ctypes import cdll, c_int, c_char_p, c_wchar_p, POINTER, c_short, c_uint, c_long, c_void_p
from ctypes import CFUNCTYPE, byref, Structure, Union, c_wchar, c_ubyte, c_ulong
import time

def cfunc(name, dll, result, *args):
    '''build and apply a ctypes prototype complete with parameter flags'''
    atypes = []
    aflags = []
    for arg in args:
        atypes.append(arg[1])
        aflags.append((arg[2], arg[0]) + arg[3:])
    return CFUNCTYPE(result, *atypes)((name, dll), tuple(aflags))

dll = cdll.LoadLibrary('libespeak.so.1')

# constants and such from speak_lib.h

EVENT_LIST_TERMINATED = 0
EVENT_WORD = 1
EVENT_SENTENCE = 2
EVENT_MARK = 3
EVENT_PLAY = 4
EVENT_END = 5
EVENT_MSG_TERMINATED = 6

class numberORname(Union):
    _fields_ = [
        ('number', c_int),
        ('name', c_char_p)
        ]
    
class EVENT(Structure):
    _fields_ = [
        ('type', c_int),
        ('unique_identifier', c_uint),
        ('text_position', c_int),
        ('length', c_int),
        ('audio_position', c_int),
        ('sample', c_int),
        ('user_data', c_void_p),
        ('id', numberORname)
        ]
    
AUDIO_OUTPUT_PLAYBACK = 0
AUDIO_OUTPUT_RETRIEVAL = 1
AUDIO_OUTPUT_SYNCHRONOUS = 2
AUDIO_OUTPUT_SYNCH_PLAYBACK = 3

EE_OK = 0
EE_INTERNAL_ERROR = -1
EE_BUFFER_FULL = 1
EE_NOT_FOUND = 2

Initialize = cfunc('espeak_Initialize', dll, c_int,
                   ('output', c_int, 1, AUDIO_OUTPUT_PLAYBACK),
                   ('bufflength', c_int, 1, 100),
                   ('path', c_char_p, 1, None),
                   ('option', c_int, 1, 0))
Initialize.__doc__ = '''Must be called before any synthesis functions are called.
  output: the audio data can either be played by eSpeak or passed back by the SynthCallback function. 
  buflength:  The length in mS of sound buffers passed to the SynthCallback function.
  path: The directory which contains the espeak-data directory, or NULL for the default location.
  options: bit 0: 1=allow espeakEVENT_PHONEME events.

  Returns: sample rate in Hz, or -1 (EE_INTERNAL_ERROR).'''

t_espeak_callback = CFUNCTYPE(c_int, POINTER(c_short), c_int, POINTER(EVENT))

cSetSynthCallback = cfunc('espeak_SetSynthCallback', dll, None,
                        ('SynthCallback', t_espeak_callback, 1))
SynthCallback = None
def SetSynthCallback(cb):
    global SynthCallback
    SynthCallback = t_espeak_callback(cb)
    cSetSynthCallback(SynthCallback)

SetSynthCallback.__doc__ = '''Must be called before any synthesis functions are called.
   This specifies a function in the calling program which is called when a buffer of
   speech sound data has been produced. 


   The callback function is of the form:

int SynthCallback(short *wav, int numsamples, espeak_EVENT *events);

   wav:  is the speech sound data which has been produced.
      NULL indicates that the synthesis has been completed.

   numsamples: is the number of entries in wav.  This number may vary, may be less than
      the value implied by the buflength parameter given in espeak_Initialize, and may
      sometimes be zero (which does NOT indicate end of synthesis).

   events: an array of espeak_EVENT items which indicate word and sentence events, and
      also the occurance if <mark> and <audio> elements within the text.


   Callback returns: 0=continue synthesis,  1=abort synthesis.'''

t_UriCallback = CFUNCTYPE(c_int, c_int, c_char_p, c_char_p)

cSetUriCallback = cfunc('espeak_SetUriCallback', dll, None,
                       ('UriCallback', t_UriCallback, 1))
UriCallback = None
def SetUriCallback(cb):
    global UriCallback
    UriCallback = t_UriCallback(UriCallback)
    cSetUriCallback(UriCallback)

SetUriCallback.__doc__ = '''This function must be called before synthesis functions are used, in order to deal with
   <audio> tags.  It specifies a callback function which is called when an <audio> element is
   encountered and allows the calling program to indicate whether the sound file which
   is specified in the <audio> element is available and is to be played.

   The callback function is of the form:

int UriCallback(int type, const char *uri, const char *base);

   type:  type of callback event.  Currently only 1= <audio> element

   uri:   the "src" attribute from the <audio> element

   base:  the "xml:base" attribute (if any) from the <speak> element

   Return: 1=don't play the sound, but speak the text alternative.
           0=place a PLAY event in the event list at the point where the <audio> element
             occurs.  The calling program can then play the sound at that point.'''


# a few manifest constants
CHARS_AUTO =  0
CHARS_UTF8 =  1
CHARS_8BIT =  2
CHARS_WCHAR = 3

SSML          = 0x10
PHONEMES      = 0x100
ENDPAUSE      = 0x1000
KEEP_NAMEDATA = 0x2000

POS_CHARACTER = 1
POS_WORD      = 2
POS_SENTENCE  = 3

def Synth(text, position=0, position_type=POS_CHARACTER, end_position=0, flags=0):
    flags |= CHARS_WCHAR
    text = unicode(text)
    return cSynth(text, len(text)*10, position, position_type, end_position, flags, None, None)

cSynth = cfunc('espeak_Synth', dll, c_int,
              ('text', c_wchar_p, 1),
              ('size', c_long, 1),
              ('position', c_uint, 1, 0),
              ('position_type', c_int, 1, POS_CHARACTER),
              ('end_position', c_uint, 1, 0),
              ('flags', c_uint, 1, CHARS_AUTO),
              ('unique_identifier', POINTER(c_uint), 1, None),
              ('user_data', c_void_p, 1, None))
Synth.__doc__ = '''Synthesize speech for the specified text.  The speech sound data is passed to the calling
   program in buffers by means of the callback function specified by espeak_SetSynthCallback(). The command is asynchronous: it is internally buffered and returns as soon as possible. If espeak_Initialize was previously called with AUDIO_OUTPUT_PLAYBACK as argument, the sound data are played by eSpeak.

   text: The text to be spoken, terminated by a zero character. It may be either 8-bit characters,
      wide characters (wchar_t), or UTF8 encoding.  Which of these is determined by the "flags"
      parameter.

   size: Equal to (or greatrer than) the size of the text data, in bytes.  This is used in order
      to allocate internal storage space for the text.  This value is not used for
      AUDIO_OUTPUT_SYNCHRONOUS mode.

   position:  The position in the text where speaking starts. Zero indicates speak from the
      start of the text.

   position_type:  Determines whether "position" is a number of characters, words, or sentences.
      Values: 

   end_position:  If set, this gives a character position at which speaking will stop.  A value
      of zero indicates no end position.

   flags:  These may be OR'd together:
      Type of character codes, one of:
         espeak.CHARS_UTF8     UTF8 encoding
         espeak.CHARS_8BIT     The 8 bit ISO-8859 character set for the particular language.
         espeak.CHARS_AUTO     8 bit or UTF8  (this is the default)
         espeak.CHARS_WCHAR    Wide characters (wchar_t)

      espeak.SSML   Elements within < > are treated as SSML elements, or if not recognised are ignored.

      espeak.PHONEMES  Text within [[ ]] is treated as phonemes codes (in espeak's Hirschenbaum encoding).

      espeak.ENDPAUSE  If set then a sentence pause is added at the end of the text.  If not set then
         this pause is suppressed.

   unique_identifier: message identifier; helpful for identifying later 
     data supplied to the callback.

   user_data: pointer which will be passed to the callback function.

   Return: EE_OK: operation achieved 
           EE_BUFFER_FULL: the command can not be buffered; 
             you may try after a while to call the function again.
	   EE_INTERNAL_ERROR.'''

def Synth_Mark(text, index_mark, end_position=0, flags=CHARS_AUTO):
    cSynth_Mark(text, len(text)+1, index_mark, end_position, flags)

cSynth_Mark = cfunc('espeak_Synth_Mark', dll, c_int,
                   ('text', c_char_p, 1),
                   ('size', c_ulong, 1),
                   ('index_mark', c_char_p, 1),
                   ('end_position', c_uint, 1, 0),
                   ('flags', c_uint, 1, CHARS_AUTO),
                   ('unique_identifier', POINTER(c_uint), 1, None),
                   ('user_data', c_void_p, 1, None))
Synth_Mark.__doc__ = '''Synthesize speech for the specified text.  Similar to espeak_Synth() but the start position is
   specified by the name of a <mark> element in the text.

   index_mark:  The "name" attribute of a <mark> element within the text which specified the
      point at which synthesis starts.  UTF8 string.

   For the other parameters, see espeak_Synth()

   Return: EE_OK: operation achieved 
           EE_BUFFER_FULL: the command can not be buffered; 
             you may try after a while to call the function again.
	   EE_INTERNAL_ERROR.'''

Key = cfunc('espeak_Key', dll, c_int,
            ('key_name', c_char_p, 1))
Key.__doc__ = '''Speak the name of a keyboard key.
   Currently this just speaks the "key_name" as given 

   Return: EE_OK: operation achieved 
           EE_BUFFER_FULL: the command can not be buffered; 
             you may try after a while to call the function again.
	   EE_INTERNAL_ERROR.'''

Char = cfunc('espeak_Char', dll, c_int,
             ('character', c_wchar, 1))
Char.__doc__ = '''Speak the name of the given character 

   Return: EE_OK: operation achieved 
           EE_BUFFER_FULL: the command can not be buffered; 
             you may try after a while to call the function again.
	   EE_INTERNAL_ERROR.'''

# Speech Parameters
SILENCE=0  #internal use
RATE=1
VOLUME=2
PITCH=3
RANGE=4
PUNCTUATION=5
CAPITALS=6
EMPHASIS=7   # internal use
LINELENGTH=8 # internal use

PUNCT_NONE=0
PUNCT_ALL=1
PUNCT_SOME=2

SetParameter = cfunc('espeak_SetParameter', dll, c_int,
                     ('parameter', c_int, 1),
                     ('value', c_int, 1),
                     ('relative', c_int, 1, 0))
SetParameter.__doc__ = '''Sets the value of the specified parameter.
   relative=0   Sets the absolute value of the parameter.
   relative=1   Sets a relative value of the parameter.

   parameter:
      espeak.RATE:    speaking speed in word per minute.

      espeak.VOLUME:  volume in range 0-100    0=silence

      espeak.PITCH:   base pitch, range 0-100.  50=normal

      espeak.RANGE:   pitch range, range 0-100. 0-monotone, 50=normal

      espeak.PUNCTUATION:  which punctuation characters to announce:
         value in espeak_PUNCT_TYPE (none, all, some), 
	 see espeak_GetParameter() to specify which characters are announced.

      espeak.CAPITALS: announce capital letters by:
         0=none,
         1=sound icon,
         2=spelling,
         3 or higher, by raising pitch.  This values gives the amount in Hz by which the pitch
            of a word raised to indicate it has a capital letter.

   Return: EE_OK: operation achieved 
           EE_BUFFER_FULL: the command can not be buffered; 
             you may try after a while to call the function again.
	   EE_INTERNAL_ERROR.'''

GetParameter = cfunc('espeak_GetParameter', dll, c_int,
                     ('parameter', c_int, 1))
GetParameter.__doc__ = '''current=0  Returns the default value of the specified parameter.
   current=1  Returns the current value of the specified parameter, as set by SetParameter()'''

SetPunctuationList = cfunc('espeak_SetPunctuationList', dll, c_int,
                           ('punctlist', c_wchar, 1))
SetPunctuationList.__doc__ = '''Specified a list of punctuation characters whose names are to be spoken when the value of the Punctuation parameter is set to "some".

   punctlist:  A list of character codes, terminated by a zero character.

   Return: EE_OK: operation achieved 
           EE_BUFFER_FULL: the command can not be buffered; 
             you may try after a while to call the function again.
	   EE_INTERNAL_ERROR.'''
                           
SetPhonemeTrace = cfunc('espeak_SetPhonemeTrace', dll, None,
                        ('value', c_int, 1),
                        ('stream', c_void_p, 1))
SetPhonemeTrace.__doc__ = '''Controls the output of phoneme symbols for the text
   value=0  No phoneme output (default)
   value=1  Output the translated phoneme symbols for the text
   value=2  as (1), but also output a trace of how the translation was done (matching rules and list entries)

   stream   output stream for the phoneme symbols (and trace).  If stream=NULL then it uses stdout.'''

CompileDictionary = cfunc('espeak_CompileDictionary', dll, None,
                          ('path', c_char_p, 1),
                          ('log', c_void_p, 1))
CompileDictionary.__doc__ = '''Compile pronunciation dictionary for a language which corresponds to the currently
   selected voice.  The required voice should be selected before calling this function.

   path:  The directory which contains the language's '_rules' and '_list' files.
          'path' should end with a path separator character ('/').
   log:   Stream for error reports and statistics information. If log=NULL then stderr will be used.'''

class VOICE(Structure):
    _fields_ = [
        ('name', c_char_p),
        ('languages', c_char_p),
        ('identifier', c_char_p),
        ('gender', c_ubyte),
        ('age', c_ubyte),
        ('variant', c_ubyte),
        ('xx1', c_ubyte),
        ('score', c_int),
        ('spare', c_void_p),
        ]
    def __repr__(self):
        '''Print the fields'''
        res = []
        for field in self._fields_:
            res.append('%s=%s' % (field[0], repr(getattr(self, field[0]))))
        return self.__class__.__name__ + '(' + ','.join(res) + ')'
        

cListVoices = cfunc('espeak_ListVoices', dll, POINTER(POINTER(VOICE)),
                    ('voice_spec', POINTER(VOICE), 1))
cListVoices.__doc__ = '''Reads the voice files from espeak-data/voices and creates an array of espeak_VOICE pointers.
   The list is terminated by a NULL pointer

   If voice_spec is NULL then all voices are listed.
   If voice spec is given, then only the voices which are compatible with the voice_spec
   are listed, and they are listed in preference order.'''

def ListVoices(voice_spec=None):
    '''Reads the voice files from espeak-data/voices and returns a list of VOICE objects.

   If voice_spec is None then all voices are listed.
   If voice spec is given, then only the voices which are compatible with the voice_spec
   are listed, and they are listed in preference order.'''
    ppv = cListVoices(voice_spec)
    res = []
    i = 0
    while ppv[i]:
        res.append(ppv[i][0])
        i += 1
    return res

SetVoiceByName = cfunc('espeak_SetVoiceByName', dll, c_int,
                       ('name', c_char_p, 1))
SetVoiceByName.__doc__ = '''Searches for a voice with a matching "name" field.  Language is not considered.
   "name" is a UTF8 string.

   Return: EE_OK: operation achieved 
           EE_BUFFER_FULL: the command can not be buffered; 
             you may try after a while to call the function again.
	   EE_INTERNAL_ERROR.'''

SetVoiceByProperties = cfunc('espeak_SetVoiceByProperties', dll, c_int,
                             ('voice_spec', POINTER(VOICE), 1))
SetVoiceByProperties.__doc__ = '''An espeak_VOICE structure is used to pass criteria to select a voice.  Any of the following
   fields may be set:

   name     NULL, or a voice name

   languages  NULL, or a single language string (with optional dialect), eg. "en-uk", or "en"

   gender   0=not specified, 1=male, 2=female

   age      0=not specified, or an age in years

   variant  After a list of candidates is produced, scored and sorted, "variant" is used to index
            that list and choose a voice.
            variant=0 takes the top voice (i.e. best match). variant=1 takes the next voice, etc'''

GetCurrentVoice = cfunc('espeak_GetCurrentVoice', dll, POINTER(VOICE),
                        )
GetCurrentVoice.__doc__ = '''Returns the espeak_VOICE data for the currently selected voice.
   This is not affected by temporary voice changes caused by SSML elements such as <voice> and <s>'''

Cancel = cfunc('espeak_Cancel', dll, c_int)
Cancel.__doc__ = '''Stop immediately synthesis and audio output of the current text. When this
   function returns, the audio output is fully stopped and the synthesizer is ready to
   synthesize a new message.

   Return: EE_OK: operation achieved 
	   EE_INTERNAL_ERROR.'''

IsPlaying = cfunc('espeak_IsPlaying', dll, c_int)
IsPlaying.__doc__ = '''Returns 1 if audio is played, 0 otherwise.'''

Synchronize = cfunc('espeak_Synchronize', dll, c_int)
Synchronize.__doc__ = '''This function returns when all data have been spoken.
   Return: EE_OK: operation achieved 
	   EE_INTERNAL_ERROR.'''

Terminate = cfunc('espeak_Terminate', dll, c_int)
Terminate.__doc__ = '''last function to be called.
   Return: EE_OK: operation achieved 
	   EE_INTERNAL_ERROR.'''

Info = cfunc('espeak_Info', dll, c_char_p,
             ('ptr', c_void_p, 1, 0))
Info.__doc__ = '''Returns the version number string.
   The parameter is for future use, and should be set to NULL'''

if __name__ == '__main__':
    def synth_cb(wav, numsample, events):
        print numsample,
        i = 0
        while True:
            if events[i].type == EVENT_LIST_TERMINATED:
                break
            print events[i].type,
            i += 1
        print
        return 0

    samplerate = Initialize(output=AUDIO_OUTPUT_PLAYBACK)
    SetSynthCallback(synth_cb)
    s = 'This is a test, only a test. '
    uid = c_uint(0)
    #print 'pitch=',GetParameter(PITCH)
    #SetParameter(PITCH, 50, 0)
    print Synth(s)
    while IsPlaying():
        time.sleep(0.1)
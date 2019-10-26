from helper import *
import unix_windows


section("Download additional data (Dictionary)")
CMD = '{} -m nltk.downloader -d jarviscli/data/nltk wordnet'
CMD = CMD.format(unix_windows.VIRTUALENV_PYTHON)
shell(CMD).should_not_fail()

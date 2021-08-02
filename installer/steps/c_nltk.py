from helper import *
import unix_windows


PACKAGES = ["wordnet", "punkt, stopwords"]

section("Download additional data (Dictionary)")
CMD = '{} -m nltk.downloader -d jarviscli/data/nltk {{}}'
CMD = CMD.format(unix_windows.VIRTUALENV_PYTHON)

for package in PACKAGES:
    printlog("* {}".format(package))
    shell(CMD.format(package)).should_not_fail()

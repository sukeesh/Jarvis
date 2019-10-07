from helper import *


section("Download additional data (Dictionary)")

shell('python -m nltk.downloader -d jarviscli/data/nltk wordnet', True).should_not_fail()

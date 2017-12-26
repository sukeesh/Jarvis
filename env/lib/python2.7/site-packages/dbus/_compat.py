# Python 2 / Python 3 compatibility helpers.

import sys

# In Python 2.6, sys.version_info is not a namedtuple, so we can't use
# sys.version_info.major.
is_py3 = (sys.version_info[0] == 3)
is_py2 = not is_py3

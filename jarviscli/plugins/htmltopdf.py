import pdfkit
from plugin import plugin, require, LINUX


@require(platform=LINUX, native=["wkhtmltopdf"])
@plugin("htmltopdf")
class htmltopdf:

    """Convert your html file or web page into pdf file"""

    def __call__(self, jarvis, s):
        jarvis.say("Welcome to the htmltopdf convertor! \nType 'help htmltopdf' to learn how to use it")







import pdfkit
from plugin import plugin, require, LINUX


@require(platform=LINUX, native=["wkhtmltopdf"])
@plugin("htmltopdf")
class htmltopdf:
    """Convert your html file or web page into pdf file"""

    def __call__(self, jarvis, s):
        jarvis.say("Welcome to the htmltopdf convertor! \nType 'help htmltopdf' to learn how to use it")


@require(platform=LINUX, native=["wkhtmltopdf"])
@plugin("htmltopdf file")
class htmltopdf_file:
    """
    Transform your html file into a pdf file in the Jarvis source directory.
    Type your url as the following:
    'htmltopdf example.html'
    The output file will be the following:
    'example.pdf'
    Your html file must be in the jarvis source directory
    """

    def __call__(self, jarvis, s):
        if not s:
            jarvis.say("please enter a file name after calling the plugin")
        elif "html" not in s:
            jarvis.say("Your file must end with '.html'")
        else:
            try:
                pdfkit.from_file(s, s.replace('.html', '') + '.pdf')
            except OSError as err:
                jarvis.say("OS error: {0}".format(err) + "\nMake sur your file is in the source directory of Jarvis and is an html file")


@require(platform=LINUX, native=["wkhtmltopdf"], network=True)
@plugin("htmltopdf url")
class htmltopdf_url:
    """
    Transform your url page into a pdf file in the Jarvis source directory. type your url as the following:
    'htmltopdf google.com'
    The output file will be the following:
    'google.com.pdf'
    """

    def __call__(self, jarvis, s):
        if not s:
            jarvis.say("please enter an url after calling the plugin")
        elif '.' not in s:
            jarvis.say("please make sur your url is valid")
        else:
            try:
                pdfkit.from_url(s, s + '.pdf')
            except IOError as err:
                jarvis.say("IO error: {0}".format(err) + "\nMake sure your URL is valid and that you have access to the internet")

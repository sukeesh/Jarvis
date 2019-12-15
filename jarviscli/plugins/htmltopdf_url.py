import pdfkit
from plugin import plugin, require, LINUX

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
        # We have to add the '.' back because the Jarvis API removes it
        dots = ["com", "org", "fr", "en"]
        for el in dots:
            if el in s:
                s = s.replace(el, "." + el)
        if not s:
            jarvis.say("please enter an url after calling the plugin")
        elif '.' not in s:
            jarvis.say("please make sur your url is valid")
        else:
       	    try:
                pdfkit.from_url(s, s + '.pdf')
            except IOError as err:
                jarvis.say("IO error: {0}".format(err) + "\nMake sure your URL is valid and that you have access to the internet")

import pdfkit
from plugin import plugin


@plugin("htmltopdf")
def htmltopdf(jarvis, s):
    
    """transform your url page into a pdf file in the Jarvis source directory. type your url as the following : \n
    'htmltopdf google.com'\n
    The output file will be the following : \n
    'google.com.pdf'"""

    dots = ["com", "org", "fr", "en"]
    for el in dots:
    	if el in s:
    		s = s.replace(el,"."+el)

    if not s:
    	jarvis.say("please enter an url after calling the plugin")
    else:
    	pdfkit.from_url(s, s + '.pdf')
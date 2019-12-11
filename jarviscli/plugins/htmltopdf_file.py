import pdfkit
from plugin import plugin

@plugin("htmltopdf file")
def htmltopdf(jarvis, s):
    
    """transform your html file into a pdf file in the Jarvis source directory. type your url as the following:
    'htmltopdf example.html'
    The output file will be the following:
    'example.pdf'
    Your html file must be in the jarvis source directory"""

    #We have to add the '.' back beacause the Jarvis API removes it
    s = s.replace('html', '.' + 'html')

    if not s:
        jarvis.say("please enter a file name after calling the plugin")
    else:
        pdfkit.from_file(s, s.replace('.html', '') + '.pdf')
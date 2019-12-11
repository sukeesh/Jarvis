import pdfkit
from plugin import plugin, require,  LINUX


@require(platform=LINUX, native=["wkhtmltopdf"])
@plugin("htmltopdf file")
class htmltopdf_file:
    
    """transform your html file into a pdf file in the Jarvis source directory. type your url as the following:
    'htmltopdf example.html'
    The output file will be the following:
    'example.pdf'
    Your html file must be in the jarvis source directory"""

    def __call__(self, jarvis, s):

    	
    	if not s:
    		jarvis.say("please enter a file name after calling the plugin")
    	elif not "html" in s:
    		jarvis.say("Your file must end with '.html'")
    	else:
    		#We have to add the '.' back beacause the Jarvis API removes it
    		s = s.replace('html', '.' + 'html')
    		try:
    			pdfkit.from_file(s, s.replace('.html', '') + '.pdf')
    		except OSError as err:
    			jarvis.say("OS error: {0}".format(err) + "\nMake sur your file is in the source directory of Jarvis and is an html file")
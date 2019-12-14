from plugin import plugin
from PIL import Image
import image2pdf


class htmltopdf_file:
    
    """transform your html file into a pdf file in the Jarvis source directory. type your url as the following:
    'htmltopdf example.html'
    The output file will be the following:
    'example.pdf'
    Your html file must be in the jarvis source directory"""

    def __call__(self, jarvis, s):

    	
    	if not s:
    		jarvis.say("please enter file path after calling the plugin")
    	elif not "png" in s:
    		jarvis.say("Your file must be a .png file")
    	else:
    		#We have to add the '.' back beacause the Jarvis API removes it
    		s = s.replace('png', '.' + 'png')
    		try:
                        source_path=s
                        dest_path= s.replace('.png', '') + '.pdf'
                        image = Image.open(source_path)
                        
                        pdf_bytes = img2pdf.convert(source_path.filename)
                        file = open(pdf_path, "wb")
                        file.write(pdf_bytes)
                        image.close() 
                        file.close() 
    			jarvis.say("file successfully converted, you may find your output file in the same folder as the input file")

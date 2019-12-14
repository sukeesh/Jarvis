from plugin import plugin
from PIL import Image
import pdf2image

@alias( "pdf2image")
@plugin("pdf2img")
class pdf2img:
    
    """converts pdf file from path to png, the output folder is in the same folder as the input file"""

    def __call__(self, jarvis, s):

    	
    	if not s:
    		jarvis.say("please enter file path after calling the plugin")
    	elif not "pdf" in s:
    		jarvis.say("Your file must be a .pdf file")
    	else:
    		#We have to add the '.' back beacause the Jarvis API removes it
    		s = s.replace('pdf', '.' + 'pdf')
    		
                source_path=s
                dest_path= s.replace('.pdf', '')
                pages=pdf2image.convert_from_file(source_path,output_file=dest_path)
                        
    		jarvis.say("file successfully converted, you may find your output folder in the same folder as the input file")

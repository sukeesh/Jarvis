from plugin import plugin
from pillow import Image
import image2pdf

@alias( "image2pdf")
@plugin("img2pdf")
class img2pdf:
    
    """converts png file from path to pdf, the output file is 
    in the same folder as the input file"""

    def __call__(self, jarvis, s):


        if not s:
            jarvis.say("please enter file path after calling the plugin")
        elif not "png" in s:
            jarvis.say("Your file must be a .png file")
        else:
            #We have to add the '.' back beacause the Jarvis API removes it
            s = s.replace('png', '.' + 'png')
            
            source_path=s
            dest_path= s.replace('.png', '') + '.pdf'
            image = Image.open(source_path)
                        
            pdf_bytes = img2pdf.convert(source_path.filename)
            file = open(dest_path, "wb")
            file.write(pdf_bytes)
            image.close() 
            file.close()
            jarvis.say("file successfully converted")

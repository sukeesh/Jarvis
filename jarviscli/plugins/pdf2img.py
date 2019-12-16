from plugin import plugin
from pdf2jpg import pdf2jpg


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
            jarvis.say(source_path)
            jarvis.say(dest_path)
            result = pdf2jpg.convert_pdf2jpg(source_path, dest_path, pages="ALL")
            jarvis.say("file successfully converted")

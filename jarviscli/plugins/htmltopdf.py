import pdfkit
from plugin import plugin





@require(platform=[LINUX], python=PYTHON3, network=True, native=["wkhtmltopdf"])
@plugin("htmltopdf")
def htmltopdf(jarvis, s):
    """transform your url page into a pdf file in the source directory of jarvis type your url as the following : \n
    'google.com' """

    splitUrl = s.split('.')
    pdfkit.from_url(s, splitUrl[0] + '.pdf')

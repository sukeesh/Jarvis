# importing the modules
import PyPDF2
from jarviscli import entrypoint

"""
A tool for reading out the pdf files using the jarvis.Uses PyPDF2 and pyttsx3 libraries
"""


@entrypoint
def read_pdf(jarvis, s):
    filename = jarvis.input("Enter your file path with '/' separations:")
    pdf = open(filename, 'rb')
    pdfRead = PyPDF2.PdfFileReader(pdf)
    for i in range(pdfRead.getNumPages()):
        page = pdfRead.getPage(i)
        jarvis.say("Page No: " + str(1 + pdfRead.getPageNumber(page)))
        pageContent = page.extractText()
        jarvis.say(pageContent)

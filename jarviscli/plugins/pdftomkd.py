import PyPDF2
from jarviscli import plugin
import os


@plugin("pdf to markdown")
class PdfToMarkdown:
    """Extracts text from a PDF using PyPDF2 and attempts to format it as Markdown."""

    def __init__(self):
        self.path = None

    def __call__(self, jarvis, s):
        self.pdf_to_mkd(jarvis, s)

    def pdf_to_mkd(jarvis, s):
        jarvis.say('')
        jarvis.say('This tool will help you convert pdf to markdown')
        pdf_input = jarvis.input("Enter the path to the PDF file: ")
        output_markdown = jarvis.input("Create a name for your output markdown file: ")

        try:

            with open(pdf_input, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)

                markdown_content = ""
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
                markdown_content += text + "\n\n"  # paragraph break between pages

                self.markdown_text(jarvis, output_markdown, markdown_content)

        except FileNotFoundError:
            jarvis.say(f"File {pdf_input} not found")


def markdown_text(self, jarvis, output_markdown, markdown_content, pdf_input):
    try:
        with open(output_markdown, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_content)
    finally:

        jarvis.say(f"Successfully extracted text from '{pdf_input}' and saved to '{output_markdown}'")

    except error as e:
    jarvis.say(f"An error occurred: {e}")

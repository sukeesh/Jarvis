import PyPDF2
import os

class PdfToMarkdown:
    """Extracts text from a PDF using PyPDF2 and attempts to format it as Markdown."""

    def __init__(self):
        self.path = None

    def pdf_to_mkd(self):
        print('')
        #would be jarvis.say('')
        print('This tool will help you convert a pdf to markdown')
        # would be jarvis.say()
        pdf_input = input("Enter the path to the PDF file: ")
        # would be jarvis.input()
        output_markdown = input("Create a name for your output markdown file: ")

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

                self.markdown_text(output_markdown, markdown_content, pdf_input)  # Pass pdf_input
        except FileNotFoundError:
            print(f"File {pdf_input} not found")

        except Exception as e:  # Catch errors in the process
            print(f"An error occurred during PDF processing: {e}")

    def markdown_text(self, output_markdown, markdown_content, pdf_input):

        try:
            with open(output_markdown, 'w', encoding='utf-8') as md_file:
                md_file.write(markdown_content)

            print(f"Successfully extracted text from '{pdf_input}' and saved to '{output_markdown}'") # Success message # Equivalent of jarvis.say()
        except Exception as e: # Catch errors
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    converter = PdfToMarkdown()
    converter.pdf_to_mkd()
    #
import PyPDF2
import tkinter as tk
from tkinter import filedialog, messagebox


class PdfToMarkdown:
    """ Extracts text from a PDF using PyPDF2 and saves in a mkdvisual.md """

    def __init__(self):
        self.output_file = "mkdvisual.md"

    def select_pdf_and_convert(self):
        pdf_path = filedialog.askopenfilename(
            title="Select a PDF file in your current directory",
            filetypes=[("PDF files only", "*.pdf")]
        )
        if not pdf_path:
            messagebox.showinfo("User has quit", "You did not select a PDF file.")
            return

        try:
            with open(pdf_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                markdown_content = "\n\n".join(
                    page.extract_text() or '' for page in reader.pages
                )
            with open(self.output_file, 'w', encoding='utf-8') as md_file:
                md_file.write(markdown_content)

            messagebox.showinfo("Success", f"Markdown saved to '{self.output_file}'")
        except FileNotFoundError:
            messagebox.showerror("Found", f"File '{pdf_path}' not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main TK window

    converter = PdfToMarkdown()
    converter.select_pdf_and_convert()
#
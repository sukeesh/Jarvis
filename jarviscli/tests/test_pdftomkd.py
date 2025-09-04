import pytest
from unittest.mock import patch
from pdftomkd import PdfToMarkdown

@patch("tkinter.filedialog.askopenfilename")
@patch("tkinter.messagebox.showinfo")
@patch("tkinter.messagebox.showerror")
def test_file_selected(mock_error, mock_info, mock_askopenfilename, tmp_path):
    try_pdf = tmp_path / "try.pdf"
    try_pdf.write_text("PDF Tryer")
    mock_askopenfilename.return_value = str(try_pdf)

    converter = PdfToMarkdown()
    converter.output_file = tmp_path / "tester_mkdvisual.md"
    converter.select_pdf_and_convert()
    assert converter.output_file.exists()

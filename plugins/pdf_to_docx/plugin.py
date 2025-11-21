# TITLE: PDF to DOCX
# AUTHOR: @sebastian

from pdf2docx import Converter

title = "PDF to DOCX"
input_format = "pdf"
output_format = "docx"


def convert(file_path):
    new_path = file_path.replace(".pdf", "_converted.docx")
    cv = Converter(file_path)
    cv.convert(new_path)
    cv.close()
    return new_path

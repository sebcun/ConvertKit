# TITLE: DOCX to PDF
# AUTHOR: @sebastian

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

title = "DOCX to PDF"
input_format = "docx"
output_format = "pdf"


def convert(file_path):
    new_path = file_path.replace(".docx", "_converted.pdf")
    
    doc = Document(file_path)
    pdf = SimpleDocTemplate(new_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    for para in doc.paragraphs:
        if para.text.strip():
            p = Paragraph(para.text, styles['Normal'])
            story.append(p)
            story.append(Spacer(1, 0.2*inch))
    
    pdf.build(story)
    return new_path
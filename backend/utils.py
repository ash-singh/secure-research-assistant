import re
from PyPDF2 import PdfReader
from docx import Document

ALLOWED_EXTENSIONS = {"pdf", "docx"}

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    return "\n".join(page.extract_text() for page in reader.pages)

def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def chunk_text(text, chunk_size=500):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_sources(answer: str):
    """Extract unique doc names cited in the answer."""
    pattern = r"\[Source:\s*([^\]]+)\]"
    return list(dict.fromkeys(re.findall(pattern, answer)))


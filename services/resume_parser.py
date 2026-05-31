import os
import PyPDF2
import pdfplumber

def extract_text_from_pdf(file_path):
    """
    Extracts text content from a PDF file.
    Tries pdfplumber first for better layout preservation, then falls back to PyPDF2.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at: {file_path}")
        
    extracted_text = ""
    
    # Try pdfplumber
    try:
        with pdfplumber.open(file_path) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            extracted_text = "\n".join(pages_text).strip()
    except Exception as e:
        print(f"pdfplumber failed: {e}. Falling back to PyPDF2.")
        extracted_text = ""

    # Fallback to PyPDF2 if pdfplumber returned empty or failed
    if not extracted_text:
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                pages_text = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        pages_text.append(text)
                extracted_text = "\n".join(pages_text).strip()
        except Exception as e:
            print(f"PyPDF2 failed: {e}")
            raise IOError(f"Could not extract text from PDF: {e}")
            
    return extracted_text

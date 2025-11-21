# %%
import re
import pymupdf
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import platform
import shutil
import os
# %%
if platform.system() == "Windows":
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    tesseract_cmd = shutil.which("tesseract")
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    else:
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
# %%   
def clean_extracted_text(text):
    if not text: return ""
    page_patterns = [
        r'(?i)page\s+\d+(?:\s+of\s+\d+)?',
        r'(?i)página\s+\d+',
        r'^\s*\d+\s*$',
        r'(?i)page\s*\|\s*\d+',
        r'(?i)\d+\s*/\s*\d+',
        r'(?i)\d+\s+of\s+\d+',
    ]
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        original_line = line
        line = line.strip()
        if not line: continue
        is_page_marker = False
        for pattern in page_patterns:
            if re.match(pattern, line):
                is_page_marker = True
                break
        if not is_page_marker:
            cleaned_line = re.sub(r'\s+', ' ', line)
            cleaned_lines.append(cleaned_line)
    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result.strip()

# %%
def extract_text_hybrid_fixed(pdf_path, dpi=300, lang="eng", min_char=50):
    try:
        doc = pymupdf.open(pdf_path)
        text_output = ""
        # Convert PDF to images for OCR fallback
        try:
            images = convert_from_path(pdf_path, dpi=dpi)
        except Exception:
            images = [] # Handle case where poppler is not installed
            
        for page_num, page in enumerate(doc):
            page_text = ""
            blocks = page.get_text("blocks")
            if blocks:
                blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
                block_texts = []
                for block in blocks:
                    block_content = block[4].strip()
                    if block_content:
                        block_texts.append(block_content)
                page_text = '\n'.join(block_texts)
            
            if len(page_text.strip()) >= min_char:
                text_output += page_text + "\n\n"
            else:
                # OCR Fallback
                if page_num < len(images):
                    ocr_text = pytesseract.image_to_string(images[page_num], lang=lang)
                    if ocr_text.strip():
                        text_output += ocr_text + "\n\n"
        doc.close()
        return clean_extracted_text(text_output)
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return ""

# %%
def categorize_resume_text(text):
    if not text: return {"error": "No text"}
    section_keywords = {
        'contact_info': ['email', 'phone', 'address', 'linkedin', 'github', 'contact'],
        'summary': ['summary', 'objective', 'profile', 'about', 'overview'],
        'experience': ['experience', 'employment', 'work history', 'work experience'],
        'education': ['education', 'academic', 'degree', 'university'],
        'skills': ['skills', 'technical skills', 'competencies', 'technologies'],
        'projects': ['projects', 'portfolio', 'achievements'],
        'certifications': ['certifications', 'certificates', 'awards']
    }
    return {"categorized_sections": {}, "extracted_contacts": {}}
# %%
def extract_text_from_image(image_path: str, lang="eng") -> str:
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang=lang)
        return clean_extracted_text(text)
    except Exception as e:
        return f"Error reading image: {str(e)}"
# %%
def process_raw_text(text: str) -> str:
    if not text:
        return ""
    return clean_extracted_text(text)
# %%

def get_resume_text(pdf_path: str) -> str:
    """Tool dùng để đọc text từ file PDF."""
    return extract_text_hybrid_fixed(pdf_path)



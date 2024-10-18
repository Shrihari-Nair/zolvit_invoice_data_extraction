import fitz  # PyMuPDF
import pdfplumber
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import re

def classify_pdf(pdf_path):
    """Classify the PDF as regular, scanned, or mixed."""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Check for text in the PDF page
            text = page.extract_text()
            if text.strip():
                return "regular"
    # If no text found, it is scanned or mixed
    return "scanned_or_mixed"




def extract_text_from_regular_pdf(pdf_path):
    """Extract text from regular PDFs using PyPDF2."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text


def extract_text_from_scanned_pdf(pdf_path):
    """Extract text from scanned PDFs using OCR."""
    images = convert_from_path(pdf_path)
    ocr_text = ""
    for image in images:
        ocr_text += pytesseract.image_to_string(image)
    return ocr_text

def get_ocr_confidence(image):
    """Get OCR confidence score from the image."""
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    confidences = [int(conf) for conf in data['conf'] if conf.isdigit()]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    return avg_confidence




def validate_invoice_fields(text):
    """Perform basic validation on extracted fields."""
    # Simple regex checks for critical fields
    invoice_number = re.search(r'Invoice #:\s*(INV-\d+)', text)
    invoice_date = re.search(r'Invoice Date:\s*(\d{2}\s\w{3}\s\d{4})', text)
    due_date = re.search(r'Due Date:\s*(\d{2}\s\w{3}\s\d{4})', text)
#     total_amount = re.search(r'Total:\s*\$?(\d+\.\d{2})', text)

    if invoice_number and invoice_date and due_date:
        return {
            "invoice_number": invoice_number.group(1),
            "invoice_date": invoice_date.group(1),
            "due_date": due_date.group(1),
            "valid": True
        }
    else:
        return {"valid": False}

def trust_determination(ocr_confidence, validation_result):
    """Determine if extracted data can be trusted based on OCR confidence and validation."""
    trust_threshold = 80  # Arbitrary confidence threshold for trusting OCR
    if ocr_confidence >= trust_threshold and validation_result['valid']:
        return True
    return False


def extract_invoice_data(pdf_path):
    """Main function to classify, extract, and validate invoice data."""
    pdf_type = classify_pdf(pdf_path)
    print(pdf_type)
    avg_confidence = 0
    if pdf_type == "regular":
        text = extract_text_from_regular_pdf(pdf_path)
    else:
        text = extract_text_from_scanned_pdf(pdf_path)
        # For mixed, apply OCR confidence checks
        images = convert_from_path(pdf_path)
        confidences = [get_ocr_confidence(img) for img in images]
        avg_confidence = sum(confidences) / len(confidences)
    print(text)
    validation_result = validate_invoice_fields(text)

    if pdf_type != "regular":
        trust = trust_determination(avg_confidence, validation_result)
    else:
        trust = validation_result['valid']
    
    return {
        "pdf_type": pdf_type,
        "extracted_data": validation_result,
        "trusted": trust
    }

extract_invoice_data('./data/Jan to Mar/INV-117_Naman.pdf')

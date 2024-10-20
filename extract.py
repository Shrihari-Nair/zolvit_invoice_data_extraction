import fitz  # PyMuPDF
import pdfplumber
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import re
import os
import easyocr
from gemini import gemini_response
from json_structure import get_json_structure_for_regular_pdf, get_json_structure_for_scanned_pdf
import json

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


def extract_text_from_regular_pdf(pdf_path, use_gemini = True):

    if use_gemini:
        images = convert_from_path(pdf_path)
        for image in images:
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            snaps_folder_path = f"./artifacts/invoice_snaps/'{pdf_name}'.png"
            image.save(snaps_folder_path, 'PNG')
            text = gemini_response(snaps_folder_path)

    else:
        """Extract text from regular PDFs using PyPDF2."""
        with open(pdf_path, 'rb') as file:
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            image_folder_path = f"./artifacts/images/{pdf_name}/"
            os.makedirs(image_folder_path, exist_ok=True)
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            for i in page.images:
                with open(os.path.join(image_folder_path, i.name), 'wb') as f:
                    f.write(i.data)
            print("Tables in the pdf")
            with pdfplumber.open(pdf_path) as pdf:
                # iterate over each page
                for page in pdf.pages:
                    print(page.extract_tables())

            with pdfplumber.open(pdf_path) as pdf:
                # iterate over each page
                for page in pdf.pages:
                    # extract text
                    text = page.extract_text()
            doc = fitz.open(pdf_path)
            print("Metadata:", doc.metadata)
            page = doc.load_page(0)
            text = page.get_text()

    return text


def extract_text_from_scanned_pdf(pdf_path, use_pytesseract = True, use_gemini = True):
    """Extract text from scanned PDFs using OCR."""
    images = convert_from_path(pdf_path)
    ocr_text = ""
    if use_pytesseract:
        for image in images:
            # config = r"--psm 11"
            ocr_text += pytesseract.image_to_string(image)
            # ocr_text = " ".join(ocr_text.splitlines())
    elif use_gemini:
        for image in images:
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            snaps_folder_path = f"./artifacts/invoice_snaps/'{pdf_name}'.png"
            image.save(snaps_folder_path, 'PNG')
            ocr_text = gemini_response(snaps_folder_path)
    else:
        reader = easyocr.Reader(['en'], gpu = False)
        for image in images:
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            snaps_folder_path = f"./artifacts/invoice_snaps/'{pdf_name}'.png"
            image.save(snaps_folder_path, 'PNG')
            ocr_text = reader.readtext(snaps_folder_path)
            extracted_text = []
            prev_cordinate = 0
            new_text = ""
            for (bbox, text, prob) in ocr_text:
                print((bbox, text))
                if abs(prev_cordinate - bbox[0][1]) < 30:
                    new_text += " " + text
                else:
                    extracted_text.append(new_text)
                    new_text = ""
                    new_text += " " + text
                prev_cordinate = bbox[0][1]
                # extracted_text.append((bbox[0][1],text))
            ocr_text = "\n".join(extracted_text)

    return ocr_text

def get_ocr_confidence(image):
    """Get OCR confidence score from the image."""
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    confidences = [int(conf) for conf in data['conf'] if str(conf).isdigit()]
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

def extract_invoice_data(pdf_path):
    """Main function to classify, extract, and validate invoice data."""
    use_gemini = False
    pdf_type = classify_pdf(pdf_path)
    print("PDF TYPE: ",pdf_type)
    # avg_confidence = 0
    if pdf_type == "regular":
        text = extract_text_from_regular_pdf(pdf_path, use_gemini = use_gemini)
    else:
        text = extract_text_from_scanned_pdf(pdf_path, use_pytesseract = False, use_gemini = False)

    print("\n -------------- PDF CONTENT ------------\n")
    print(text)
    if not text:
        return
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    text_data_path = f"./artifacts/text_data/{pdf_name}.txt"
    with open(text_data_path, 'w', encoding='utf-8') as file:
        file.write(text)

    json_data = text
    if pdf_type == "regular":
        if not use_gemini:
            json_data = get_json_structure_for_regular_pdf(text)
        json_path = f"./artifacts/json_dumps/scanned_pdf_jsons/{pdf_name}.json"
        with open(json_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
    else:
        if not use_gemini:
            json_data = get_json_structure_for_scanned_pdf(text)
        json_path = f"./artifacts/json_dumps/regular_pdf_jsons/{pdf_name}.json"
        with open(json_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)

    print("\n ------------ Structured JSON format -------------\n")
    print(json_data)
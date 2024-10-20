import json
import pytesseract

def trust_determination(ocr_confidence, validation_result):
    """Determine if extracted data can be trusted based on OCR confidence and validation."""
    trust_threshold = 80  # Arbitrary confidence threshold for trusting OCR
    if ocr_confidence >= trust_threshold and validation_result['valid']:
        return True
    return False

def load_json_string(file_path):
    """Load JSON data from a file where the data is stored as a string."""
    with open(file_path, 'r') as file:
        json_string = file.read()  # Read the file content
    return json.loads(json_string)  # Convert string to JSON

def load_json(file_path):
    """Helper function to load a JSON file from a given path."""
    with open(file_path, 'r') as file:
        return json.load(file)

def get_ocr_confidence(image):
    """Get OCR confidence score from the image."""
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    confidences = [int(conf) for conf in data['conf'] if str(conf).isdigit()]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    return avg_confidence
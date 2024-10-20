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

def get_items_list():
    item_list=['DermaQ Comprehensive Hair Health Diagnostic Test','Hair Nutrition Plan','8x Shampoo','LONITAB 2.5 mg',
          'Anaboom AD Lotion - 50 ml','Uprise D-3 60K Capsules - 12','ME-12 OD (15 tabs)','tab dutamax 0.5 mg','Uprise-D3 60K - 8 Capsule',
           'Acne-UV Gel - spf 50 (50 gm)','Keraglo- AD shampoo','Bioderma Pigmentbio C-concentrate','Cetaphil gentle cleansing lotion - 250 ML',
           'Dermatologist Consultation','Acutret 20 mg - 10 capsules','Isotroin 20 mg - 10 capsules','Biluma cream - 15 gm','Acne UV Gel - 30 SPF',
          'Clindac-A mist spray','AKNAYBAR soap','Solasafe sunscreen gel spf 50','Ahaglow Advanced Skin Rejuvenating Face Wash Gel','Acutret 10 capsules'
          ' Biluma cream - 15 gm','Triluma Cream - 15 gm','Isotroin 10 MG - 10 Capsule','Cetaphil DAM Advance Ultra-Hydrating Lotion Face - 100 gm',
           'Depiwhite Advanced Cream - 15 ml','Benzac AC 2.5%','Arachitol Nano (60k) 4*5ml','Neurobion Forte - 30 tablets',
           'Cutacapil Stem - 60 ml','Follihair AMPM Tablet Gluten Free - 20 tablets','Dermaq Basic Hair Test Men - B12, V-D & TST',
          'Vitamin b12 test','keraglo Eva - 30 Tablet','Cetaphil Moisturising Lotion with Avocado Oil, Vitamin E, B3 & B5 - 250 ml',
           'Comprehensive Hair & Health Test - Silver','Keraglo Men Tablet - 30 tablets','Livogen-Z Captabs 15s','Kera M 5% Solution','HBA1C Test',
           'Last bill pending','Hydrafacial','sotret nf 16 mg - 10 capsules','Ekran Aqua Sunscreen Spf 30','Glogeous facewash','Bristaa Intense Cream',
          'Anaoom AD Shampo','Acutret 5 mg','ATODERM Moisturiser','Tab flucon 400mg','Lupizol ZS Shampoo 100 ml',
          'Cetaphil Gentle Cleansing Lotion - Oily Skin 125 ml','IPCA Acne OC Moisturizer Cream - 75 gm ','Kera-FM 5% Topical Solution',
          'Bioderma Sebium Hydra Moisturiser - 40 ml','Kera XL New Hair Growth Serum','Arachitol','PRP','Lab test - full body checkup','GFC PRP',
          'due last bill','Faireye under eye cream','Trapic 500 TA - 10','Fixderma Shadow SPF 50+ Cream','Sortet F 16 mg - 10 cap',
          'Zincovit tablet','Sevenseas Cap','Excela Moisturiser - 50 gm ']
    return set(item_list)
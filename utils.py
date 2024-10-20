def trust_determination(ocr_confidence, validation_result):
    """Determine if extracted data can be trusted based on OCR confidence and validation."""
    trust_threshold = 80  # Arbitrary confidence threshold for trusting OCR
    if ocr_confidence >= trust_threshold and validation_result['valid']:
        return True
    return False
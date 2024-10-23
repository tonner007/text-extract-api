from celery_config import celery
from ocr_strategies.marker import MarkerOCRStrategy
from ocr_strategies.tesseract import TesseractOCRStrategy

OCR_STRATEGIES = {
    'marker': MarkerOCRStrategy(),
    'tesseract': TesseractOCRStrategy()
}

@celery.task(bind=True)
def ocr_task(self, pdf_bytes, strategy_name):
    """
    Celery task to perform OCR processing on a PDF file.
    """
    if strategy_name not in OCR_STRATEGIES:
        raise ValueError(f"Unknown strategy '{strategy_name}'. Available: marker, tesseract")
    
    ocr_strategy = OCR_STRATEGIES[strategy_name]
    self.update_state(state='PROGRESS', meta={'progress': 50})  # Example progress update
    
    extracted_text = ocr_strategy.extract_text_from_pdf(pdf_bytes)
    return extracted_text

import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from celery.result import AsyncResult
from celery_config import celery
from tasks import ocr_task, OCR_STRATEGIES

app = FastAPI()

OLLAMA_API_URL = "http://ollama:8000/generate"  # URL to call the Ollama API within Docker

@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...), strategy: str = "marker", async_mode: bool = True):
    """
    Endpoint to extract text from an uploaded PDF file using different OCR strategies.
    Supports both synchronous and asynchronous processing.
    """
    if file.content_type != None and file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are supported.")

    pdf_bytes = await file.read()

    if strategy not in OCR_STRATEGIES:
        raise HTTPException(status_code=400, detail=f"Unknown strategy '{strategy}'. Available: marker, tesseract")

    if async_mode:
        # Asynchronous processing using Celery
        task = ocr_task.apply_async(args=[pdf_bytes, strategy])
        return {"task_id": task.id}
    else:
        # Synchronous processing
        ocr_strategy = OCR_STRATEGIES[strategy]
        extracted_text = ocr_strategy.extract_text_from_pdf(pdf_bytes)
        return {"text": extracted_text}

@app.get("/ocr/result/{task_id}")
async def ocr_status(task_id: str):
    """
    Endpoint to get the status of an OCR task using task_id.
    """
    task = AsyncResult(task_id, app=celery)

    if task.state == 'PENDING':
        return {"state": task.state, "status": "Task is pending..."}
    elif task.state == 'PROGRESS':
        return {"state": task.state, "status": "Task is in progress...", "progress": task.info.get('progress', 0)}
    elif task.state == 'SUCCESS':
        return {"state": task.state, "status": "Task completed successfully.", "result": task.result}
    else:
        return {"state": task.state, "status": str(task.info)}

@app.post("/ocr/clear_cache")
async def clear_ocr_cache():
    """
    Endpoint to clear the OCR result cache in Redis.
    """
    redis_client.flushdb()
    return {"status": "OCR cache cleared"}

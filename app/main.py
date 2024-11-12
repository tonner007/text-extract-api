import time
from urllib import parse
import requests
from fastapi import FastAPI, Form, Request, UploadFile, File, HTTPException, Body
from celery.result import AsyncResult
from storage_manager import StorageManager
from celery_config import celery
from tasks import ocr_task, OCR_STRATEGIES
from hashlib import md5
import redis
import os
from pydantic import BaseModel
import ollama
import base64


app = FastAPI()

# Connect to Redis
redis_url = os.getenv('REDIS_CACHE_URL', 'redis://redis:6379/1')
redis_client = redis.StrictRedis.from_url(redis_url)

@app.post("/ocr")
async def ocr_endpoint(
    strategy: str = Form(...),
    prompt: str = Form(None),
    model: str = Form(...),
    file: UploadFile = File(...),
    ocr_cache: bool = Form(...),
    storage_profile: str = Form('default'),
    storage_filename: str = Form(None)
):    
    """
    Endpoint to extract text from an uploaded PDF file using different OCR strategies.
    Supports both synchronous and asynchronous processing.
    """
    if file.content_type is not None and file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are supported.")

    pdf_bytes = await file.read()

    # Generate a hash of the PDF content for caching
    pdf_hash = md5(pdf_bytes).hexdigest()

    if strategy not in OCR_STRATEGIES:
        raise HTTPException(status_code=400, detail=f"Unknown strategy '{strategy}'. Available: marker, tesseract")

    print(f"Processing PDF {file.filename} with strategy: {strategy}, ocr_cache: {ocr_cache}, model: {model}, storage_profile: {storage_profile}, storage_filename: {storage_filename}")

    # Asynchronous processing using Celery
    task = ocr_task.apply_async(args=[pdf_bytes, strategy, file.filename, pdf_hash, ocr_cache, prompt, model, storage_profile, storage_filename])
    return {"task_id": task.id}

# this is an alias for /ocr - to keep the backward compatibility
@app.post("/ocr/upload")
async def ocr_upload_endpoint(
    strategy: str = Form(...),
    prompt: str = Form(None),
    model: str = Form(...),
    file: UploadFile = File(...),
    ocr_cache: bool = Form(...),
    storage_profile: str = Form('default'),
    storage_filename: str = Form(None)
):
    """
    Alias endpoint to extract text from an uploaded PDF file using different OCR strategies.
    Supports both synchronous and asynchronous processing.
    """
    return await ocr_endpoint(strategy, prompt, model, file, ocr_cache, storage_profile, storage_filename)

class OllamaGenerateRequest(BaseModel):
    model: str
    prompt: str

class OllamaPullRequest(BaseModel):
    model: str

class OcrRequest(BaseModel):
    strategy: str
    prompt: str = None
    model: str
    file: str  # Base64 encoded file content
    ocr_cache: bool
    storage_profile: str = 'default'
    storage_filename: str = None

@app.post("/ocr/request")
async def ocr_request_endpoint(request: OcrRequest):
    """
    Endpoint to extract text from an uploaded PDF file using different OCR strategies.
    Supports both synchronous and asynchronous processing.
    """
    if not request.file:
        raise HTTPException(status_code=400, detail="File content is missing.")
    
    file_content = base64.b64decode(request.file)
    
    # Assuming the file is a PDF
    if not file_content.startswith(b'%PDF'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are supported.")
    
    # Process the file content as needed
    # ...

    return {"status": "File processed successfully"}

@app.get("/ocr/result/{task_id}")
async def ocr_status(task_id: str):
    """
    Endpoint to get the status of an OCR task using task_id.
    """
    task = AsyncResult(task_id, app=celery)

    if task.state == 'PENDING':
        return {"state": task.state, "status": "Task is pending..."}
    elif task.state == 'PROGRESS':
        task_info = task.info
        if task_info.get('start_time'):
            task_info['elapsed_time'] = time.time() - int(task_info.get('start_time'))
        return {"state": task.state, "status": task.info.get("status"), "info": task_info } 
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

@app.get("/storage/list")
async def list_files(storage_profile: str = 'default'):
    """
    Endpoint to list files using the selected storage profile.
    """
    storage_manager = StorageManager(storage_profile)
    files = storage_manager.list()
    return {"files": files}

@app.get("/storage/load")
async def load_file(file_name: str, storage_profile: str = 'default'):
    """
    Endpoint to load a file using the selected storage profile.
    """
    storage_manager = StorageManager(storage_profile)
    content = storage_manager.load(file_name)
    return {"content": content}

@app.delete("/storage/delete")
async def delete_file(file_name: str, storage_profile: str = 'default'):
    """
    Endpoint to delete a file using the selected storage profile.
    """
    storage_manager = StorageManager(storage_profile)
    storage_manager.delete(file_name)
    return {"status": f"File {file_name} deleted successfully"}

@app.post("/llm/pull")
async def pull_llama(request: OllamaPullRequest):
    """
    Endpoint to pull the latest Llama model from the Ollama API.
    """
    print("Pulling " + request.model)
    try:
        response = ollama.pull(request.model)
    except ollama.ResponseError as e:
        print('Error:', e.error)
        raise HTTPException(status_code=500, detail="Failed to pull Llama model from Ollama API")

    return {"status": response.get("status", "Model pulled successfully")}

@app.post("/llm/generate")
async def generate_llama(request: OllamaGenerateRequest):
    """
    Endpoint to generate text using Llama 3.1 model (and other models) via the Ollama API.
    """
    print(request)
    if not request.prompt:
        raise HTTPException(status_code=400, detail="No prompt provided")

    try:
        response = ollama.generate(request.model, request.prompt)
    except ollama.ResponseError as e:
        print('Error:', e.error)
        if e.status_code == 404:
            print("Error: ", e.error)
            ollama.pull(request.model)

        raise HTTPException(status_code=500, detail="Failed to generate text with Ollama API")

    generated_text = response.get("response", "")
    return {"generated_text": generated_text}

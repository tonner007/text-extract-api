import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv(".env")

import multiprocessing

multiprocessing.set_start_method("spawn", force=True)

def make_celery() -> Celery:
    celery_instance = Celery(
        "pdf_extract_api",
        broker="redis://redis:6379/0",
        backend="redis://redis:6379/0"
    )
    celery_instance.config_from_object({
        "worker_max_memory_per_child": 8200000
    })
    return celery_instance

# Used for worker
app = make_celery()

import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv(".env")

import multiprocessing

multiprocessing.set_start_method("spawn", force=True)


def make_celery():
    celery = Celery(
        "app",
        broker=os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'),
        backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
    )
    celery.config_from_object({
        "worker_max_memory_per_child": 8200000
    })
    return celery


celery = make_celery()

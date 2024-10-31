from celery import Celery
import multiprocessing

multiprocessing.set_start_method("spawn")

def make_celery():
    celery = Celery(
        "app",
        broker="redis://redis:6379/0",
        backend="redis://redis:6379/0"
    )
    celery.config_from_object({
        "worker_max_memory_per_child": 8200000
    })
    return celery

celery = make_celery()
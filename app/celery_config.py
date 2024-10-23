from celery import Celery

def make_celery():
    celery = Celery(
        "app",
        broker="redis://redis:6379/0",
        backend="redis://redis:6379/0"
    )
    return celery

celery = make_celery()
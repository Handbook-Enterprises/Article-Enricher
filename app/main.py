from fastapi import FastAPI
from pydantic import BaseModel
from .celery_worker import celery_app
# from .tasks import dummy_task
from typing import List
from utils import enrichment_utils
from .tasks import enrich_and_verify_article
app = FastAPI()

# class TaskRequest(BaseModel):
#     duration: int = 5

# @app.post("/enqueue-task")
# def enqueue_task(payload: TaskRequest):
#     task = dummy_task.delay(payload.duration)
#     return {"task_id": task.id}

# @app.get("/task-status/{task_id}")
# def get_status(task_id: str):
#     result = celery_app.AsyncResult(task_id, app=celery_app)
#     return {
#         "task_id": task_id,
#         "status": result.status,
#         "result": result.result if result.ready() else None
#     }

class ArticleSubmission(BaseModel):
    article: str
    keywords: List[str]


@app.post("/submit")
def submit_article(payload:ArticleSubmission):
    task = enrich_and_verify_article.delay(payload.article,payload.keywords)
    return {"task_id":task.id}

@app.get("/status/{task_id}")
def get_task_status(task_id:str):
    result = celery_app.AsyncResult(task_id)
    if result.state == "PENDING":
        return {"status": "not_found"}

    elif result.state in ("STARTED", "RETRY"):
        return {"status": "processing"}

    elif result.state == "FAILURE":
        return {"status": "failed", "error": str(result.result)}

    elif result.state == "SUCCESS":
        return {"status": "success", "result": result.result}





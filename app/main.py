from fastapi import FastAPI
from pydantic import BaseModel
from .celery_worker import celery_app

# from .tasks import dummy_task
from typing import List
from .tasks import enrich_and_verify_article

app = FastAPI()


class ArticleSubmission(BaseModel):
    article: str
    keywords: List[str]


@app.post("/submit")
def submit_article(payload: ArticleSubmission):
    task = enrich_and_verify_article.delay(payload.article, payload.keywords)
    return {"task_id": task.id}


@app.get("/status/{task_id}")
def get_task_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    if result.state == "PENDING":
        return {"status": "not_found"}

    elif result.state in ("STARTED", "RETRY"):
        return {"status": "processing"}

    elif result.state == "FAILURE":
        return {"status": "failed", "error": str(result.result)}

    elif result.state == "SUCCESS":
        return {"status": "success", "result": result.result}

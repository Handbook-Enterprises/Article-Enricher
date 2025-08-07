import time
import sys
import os
from .celery_worker import celery_app
import uuid

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.enrichment_utils import enrich_article
from utils.qa_utils import run_qa

MAX_RETRIES = 3

# @celery_app.task(name="app.tasks.enrich_and_verify_article")
# def enrich_and_verify_article(article: str, keywords: list[str]):
#     for attempt in range(1, MAX_RETRIES + 1):
#         enriched = enrich_article(article, keywords)
#         qa_result = run_qa(enriched)

#         if qa_result.accepted:
#             return {
#                 "enriched_article": enriched,
#                 "score": qa_result.score,
#                 "accepted": qa_result.accepted
#             }

#     # If we reach here, all attempts failed
#     raise Exception("QA failed after 3 retries")

DATA_DIR = os.path.join(project_root, "data")
os.makedirs(DATA_DIR, exist_ok=True)

@celery_app.task(name="app.tasks.enrich_and_verify_article")
def enrich_and_verify_article(article: str, keywords: list[str]):
    for attempt in range(1, MAX_RETRIES + 1):
        enriched = enrich_article(article, keywords)
        qa_result = run_qa(enriched)

        if qa_result.accepted:
            # Save enriched article to data directory
            filename = f"article_{uuid.uuid4().hex[:8]}_enriched.md"
            file_path = os.path.join(DATA_DIR, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(enriched)

            return {
                "enriched_article": enriched,
                "score": qa_result.score,
                "accepted": qa_result.accepted,
                "saved_path": file_path
            }

    # If all retries failed
    raise Exception("QA failed after 3 retries")
import os
import uuid
from .celery_worker import celery_app
from utils.enrichment_utils import enrich_article
from utils.qa_utils import run_qa
from schema import EnrichmentResponse, QAEnrichedArticle

MAX_RETRIES = 3

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(project_root, "data")
os.makedirs(DATA_DIR, exist_ok=True)


@celery_app.task(name="app.tasks.enrich_and_verify_article")
def enrich_and_verify_article(article: str, keywords: list[str]):
    previous_qa_explanation = None

    for attempt in range(1, MAX_RETRIES + 1):
        enriched_response: EnrichmentResponse = enrich_article(
            article, keywords, previous_qa_explanation=previous_qa_explanation
        )

        qa_result: QAEnrichedArticle = run_qa(enriched_response.enriched_article)

        if qa_result.accepted:
            filename = f"article_{uuid.uuid4().hex[:8]}_enriched.md"
            file_path = os.path.join(DATA_DIR, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(enriched_response.enriched_article)

            return {
                "enriched_article": enriched_response.enriched_article,
                "explanation": qa_result.explanation,
                "score": qa_result.score,
                "accepted": qa_result.accepted,
                "saved_path": file_path,
            }

        previous_qa_explanation = qa_result.explanation  # Carry into next attempt

    raise Exception(
        f"QA failed after {MAX_RETRIES} retries. Last explanation: {previous_qa_explanation or 'No explanation provided.'}"
    )

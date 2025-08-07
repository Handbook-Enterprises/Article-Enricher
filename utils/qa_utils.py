from utils.llm_client import call_qa_llm
from schema import QAEnrichedArticle
from utils.logger import get_logger

logger = get_logger(__name__)


def run_qa(article: str) -> QAEnrichedArticle:
    qa_result = call_qa_llm(article)

    logger.info(
        f" QA Result:\n"
        f"  has_two_links = {qa_result.has_two_links}\n"
        f"  has_two_images = {qa_result.has_two_images}\n"
        f"  has_valid_alt_text = {qa_result.has_valid_alt_text}\n"
        f"  follows_brand_voice = {qa_result.follows_brand_voice}\n"
        f"  accepted = {qa_result.accepted}\n"
        f"  score = {qa_result.score}\n"
        f"  explanation = {qa_result.explanation}\n"
        f"QA Verdict → accepted: {qa_result.accepted}, score: {qa_result.score}"
    )

    return qa_result

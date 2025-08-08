import os
import openai
import instructor
from dotenv import load_dotenv
from utils.logger import get_logger
from schema import QAEnrichedArticle, EnrichmentResponse

load_dotenv()

logger = get_logger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = instructor.patch(
    openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
)

DEFAULT_MODEL = "google/gemini-2.5-flash-lite"

# QA prompt
QA_PROMPT = """
You are a senior content QA analyst.

Your task is to evaluate a markdown article based on the following criteria and return a JSON object conforming to the QAEnrichedArticle schema. Ensure you include the enriched_article content itself, along with your evaluation and explanation.

Criteria:
1. **has_two_links**: The article contains exactly **2 inline hyperlinks**, embedded within flowing text using Markdown syntax.
2. **has_two_images**: The article contains exactly **2 different images**: one *hero image* near the top, one in-body.
3. **has_valid_alt_text**: Each image has descriptive alt text under 125 characters and does not begin with "Image of".
4. **follows_brand_voice**: Uses a friendly‑expert tone, sentence-case headings, and concise language.
5. **accepted**: Return `true` only if all above criteria are met.
6. **score**: If accepted, score must be ≥ 7. If not, score must be < 7.
7. **explanation**: Detailed reasoning behind your decision and what needs fixing if rejected.
"""


# For enrichment step
def call_enrichment_llm(prompt: str) -> EnrichmentResponse | None:
    try:
        return client.chat.completions.create(
            model=DEFAULT_MODEL,
            response_model=EnrichmentResponse,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that enriches markdown articles.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
    except Exception as e:
        logger.error(f"Enrichment LLM failed: {e}")
        return None


# For QA step
def call_qa_llm(article: str) -> QAEnrichedArticle | None:
    try:
        return client.chat.completions.create(
            model=DEFAULT_MODEL,
            response_model=QAEnrichedArticle,
            messages=[
                {"role": "system", "content": QA_PROMPT},
                {"role": "user", "content": article},
            ],
            temperature=0.3,
        )
    except Exception as e:
        logger.error(f"QA LLM failed: {e}")
        return None

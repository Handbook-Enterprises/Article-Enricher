import openai
import instructor
from shema import QAEnrichedArticle as QA
from utils import llm_client
from utils.logger import get_logger

logger = get_logger(__name__)

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=llm_client.OPENROUTER_API_KEY,
)
instructor_client = instructor.patch(client)

QA_PROMPT = """
You are a senior content QA analyst.

Your task is to verify whether a markdown article meets each of the following criteria:

1. **has_two_links**: The article contains exactly **2 inline hyperlinks**, embedded within flowing text using Markdown syntax. Do not count if the links are standalone or repeated.
2. **has_two_images**: The article contains exactly **2 different images**:
   - One *hero image* after the first paragraph
   - One *in-body image* later in the article
3. **has_valid_alt_text**: Each image has descriptive alt text that is under 125 characters and does not begin with "Image of" or "Picture of".
4. **follows_brand_voice**: The article uses a friendly‑expert tone, avoids generic AI text, has sentence-case headings, and follows inclusive, concise writing style.
5. **accepted**: Only return `true` if **all of the above are true**.
6. **score**: Return a score from 0–10. If accepted, the score must be **≥7**. If rejected, it must be **<7**.

Now evaluate the article below:
"""
def run_qa(enriched_article: str):
    response = instructor_client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        response_model=QA,
        messages=[
            {"role": "system", "content": QA_PROMPT},
            {"role": "user", "content": enriched_article}
        ]
    )
    logger.info(
        f" QA Result:\n"
        f"  has_two_links = {response.has_two_links}\n"
        f"  has_two_images = {response.has_two_images}\n"
        f"  has_valid_alt_text = {response.has_valid_alt_text}\n"
        f"  follows_brand_voice = {response.follows_brand_voice}\n"
        f"  accepted = {response.accepted}\n"
        f"  score = {response.score}\n"
        f"QA Verdict → accepted: {response.accepted}, score: {response.score}"
     )
    #logger.info(f"QA Verdict → accepted: {response.accepted}, score: {response.score}")
    return response

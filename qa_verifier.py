import openai
import instructor
from schema import QAEnrichedArticle as QA
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


def verify_article(markdown_path):
    with open(markdown_path, "r", encoding="utf-8") as f:
        enriched_article = f.read()
    response = instructor_client.chat.completions.create(
        model="google/gemini-2.5-flash-lite",
        response_model=QA,
        messages=[
            {"role": "system", "content": QA_PROMPT},
            {"role": "user", "content": enriched_article},
        ],
    )

    logger.info(f"QA Verdict → accepted: {response.accepted}, score: {response.score}")
    return response


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run QA verification on enriched article"
    )
    parser.add_argument(
        "--markdown_path", required=True, help="Path to enriched markdown article"
    )
    args = parser.parse_args()
    verify_article(args.markdown_path)

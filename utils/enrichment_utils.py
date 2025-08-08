from . import prompt_builder, db_utils, llm_client
from schema import EnrichmentResponse


def enrich_article(
    article_text: str, keywords: list[str], previous_qa_explanation: str | None = None
) -> EnrichmentResponse:
    brand_rules = prompt_builder.load_file("data/brand_rules.txt")
    links = db_utils.get_links_for_keywords(keywords)
    images = db_utils.get_images_for_keywords(keywords)

    prompt = prompt_builder.build_prompt(
        article_text, keywords, links, images, brand_rules, previous_qa_explanation
    )
    enriched_response = llm_client.call_enrichment_llm(prompt)

    if not enriched_response:
        raise Exception("LLM did not return a valid enrichment response.")

    return enriched_response

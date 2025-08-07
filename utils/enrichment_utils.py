from . import prompt_builder, db_utils, llm_client

def enrich_article(article_text: str, keywords: list[str]) -> str:
    brand_rules = prompt_builder.load_file("data/brand_rules.txt")
    links = db_utils.get_links_for_keywords(keywords)
    images = db_utils.get_images_for_keywords(keywords)

    prompt = prompt_builder.build_prompt(article_text, keywords, links, images, brand_rules)
    enriched_markdown = llm_client.call_llm(prompt)
    
    return enriched_markdown.strip()
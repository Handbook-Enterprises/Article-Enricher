from utils import prompt_builder, db_utils, llm_client
import argparse
from utils.logger import get_logger

logger = get_logger(__name__)


def main(article_path, keywords_path):
    # Load inputs
    article_text = prompt_builder.load_file(article_path)
    keywords = prompt_builder.load_file(keywords_path).splitlines()
    brand_rules = prompt_builder.load_file("data/brand_rules.txt")

    # Get matching assets
    links = db_utils.get_links_for_keywords(keywords, db_path="links.db")
    images = db_utils.get_images_for_keywords(keywords, db_path="media.db")
    logger.info(f"Found links: {links}")
    logger.info(f"Found images: {images}")
    # Build prompt
    prompt = prompt_builder.build_prompt(
        article_text, keywords, links, images, brand_rules
    )

    logger.info(f"Generated prompt:\n{prompt}")
    logger.info("\nSending to LLM...\n")
    enriched_markdown = llm_client.call_llm(prompt)

    if not enriched_markdown:
        logger.error("Error: LLM did not return a valid response.")
        return

    # Save to file
    output_path = article_path.replace(".md", "_enriched.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(enriched_markdown.strip())

    logger.info(f"Enriched markdown saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run article enrichment pipeline.")
    parser.add_argument(
        "--article_path", required=True, help="Path to input article markdown file."
    )
    parser.add_argument(
        "--keywords_path", required=True, help="Path to keywords .txt file."
    )
    args = parser.parse_args()

    main(args.article_path, args.keywords_path)

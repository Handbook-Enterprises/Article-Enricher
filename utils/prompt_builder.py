import os


def load_file(filepath):
    """Utility to load content from a file."""

    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


def build_prompt(
    article_text,
    keywords,
    links,
    images,
    brand_rules,
    previous_qa_explanation: str | None = None,
):
    """
    Build a well-structured prompt for the LLM.
    """
    # Split links and images into primary and fallback
    primary_links = links[:2]
    fallback_links = links[2:]

    primary_images = images[:2]
    fallback_images = images[2:]

    link_instructions = (
        "\n".join(
            [
                f"- Insert a Markdown link for the keyword: '{link['keyword']}', using this URL: {link['url']}"
                for link in primary_links
            ]
        )
        or "No internal links to insert."
    )

    image_instructions = (
        "\n".join(
            [
                f"- (Candidate #{i + 1}) For keyword '{img['keyword']}', insert this image URL: {img['url']} (add descriptive alt-text)"
                for i, img in enumerate(primary_images)
            ]
        )
        or "No images to insert."
    )

    # Add fallback note if more than 2 are available
    if fallback_links:
        link_instructions += (
            "\n- If any of the above are not contextually relevant, you may use these alternatives:\n"
            + "\n".join(
                [
                    f"  - Alternative link: '{link['keyword']}' → {link['url']}"
                    for link in fallback_links
                ]
            )
        )

    if fallback_images:
        image_instructions += (
            "\n- You may also consider these alternate image candidates:\n"
            + "\n".join(
                [
                    f"  - Alt image: '{img['keyword']}' → {img['url']}"
                    for img in fallback_images
                ]
            )
        )

    qa_feedback = ""
    if previous_qa_explanation:
        qa_feedback = f"""
--- Previous QA Feedback ---
Your last attempt failed QA with the following explanation:
{previous_qa_explanation}

Carefully review this feedback and adjust your approach to meet all criteria in this attempt.
---"""

    prompt = f"""
You are a content editor AI.

Your job is to:
1. Embed exactly **two different** relevant internal links from the list below:
  - Hyperlinks must be embedded **inline**, as part of flowing sentences or paragraphs.
  - Do **not** place links at the end of sections or as standalone lines.
  - Use natural anchor text that fits the surrounding context (can vary slightly from keywords).
  - **Do not reuse the same link twice.**

2. Insert exactly **two different** images from the list:
  - One **hero image** near the top of the article, ideally after the first paragraph.
  - One **in-body image** embedded in a relevant section later in the article.
  - Add short, descriptive alt-text (≤125 characters) using Markdown image syntax.
  - **Do not reuse the same image twice. Choose two different image URLs.**

3. Follow the brand style rules below carefully.

{qa_feedback}

---
### EXAMPLES:

    #### GOOD Inline Link:
        > According to the [IEA’s carbon capture roadmap](https://example.com/ccs-roadmap), global storage capacity must triple by 2040.

    #### BAD Link:
        > [IEA’s carbon capture roadmap](https://example.com/ccs-roadmap)

---
    #### GOOD Image Use:
        > ![A direct air capture facility surrounded by desert](https://example.com/dac-image.jpg)

    #### BAD Image Use:
        > Just paste an image link here: https://example.com/dac-image.jpg
---

### LINK INSTRUCTIONS:
{link_instructions}

### IMAGE INSTRUCTIONS:
{image_instructions}

### BRAND RULES:
{brand_rules}

### KEYWORDS TO CONSIDER:
{", ".join(keywords)}

---

Now here is the article you need to enrich:

{article_text}

---

Your output should contain two main parts:
1.  `enriched_article`: The full enriched article in Markdown format.
2.  `explanation`: A brief explanation (2-3 sentences) of your reasoning for link and image placement, how you adhered to brand guidelines, and how you addressed any previous QA feedback.
"""
    return prompt

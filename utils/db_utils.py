import sqlite3
from typing import List, Dict
import re
import random


def tokenize(text):
    return re.split(r"[,\s\-]+", text.lower())


def dedupe_and_sample(results: List[Dict], max_items=4) -> List[Dict]:
    seen_urls = set()
    unique = []
    for item in results:
        if item["url"] not in seen_urls:
            seen_urls.add(item["url"])
            unique.append(item)
        if len(unique) == max_items:
            break
    return unique


def get_links_for_keywords(keywords, db_path="links.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    results = []

    for kw in keywords:
        kw_parts = tokenize(kw)
        patterns = [f"%{part}%" for part in kw_parts]
        placeholders = " OR ".join(["LOWER(topic_tags) LIKE ?" for _ in patterns])

        cursor.execute(
            f"""
            SELECT url, topic_tags FROM resources WHERE {placeholders}
        """,
            patterns,
        )

        for row in cursor.fetchall():
            db_tags = tokenize(row[1])
            if any(part in db_tags for part in kw_parts):
                results.append({"keyword": kw, "url": row[0]})

    conn.close()
    random.shuffle(results)
    return dedupe_and_sample(results, max_items=4)


def get_images_for_keywords(keywords, db_path="media.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    results = []

    for kw in keywords:
        kw_parts = tokenize(kw)
        patterns = [f"%{part}%" for part in kw_parts]
        placeholders = " OR ".join(["LOWER(tags) LIKE ?" for _ in patterns])

        cursor.execute(
            f"""
            SELECT url, tags FROM images WHERE {placeholders}
        """,
            patterns,
        )

        for row in cursor.fetchall():
            db_tags = tokenize(row[1])
            if any(part in db_tags for part in kw_parts):
                results.append({"keyword": kw, "url": row[0]})

    conn.close()
    random.shuffle(results)
    return dedupe_and_sample(results, max_items=4)

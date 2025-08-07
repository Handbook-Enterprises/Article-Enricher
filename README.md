# Article Enricher

A Python application that automatically enriches markdown articles by adding relevant internal links and images from local databases.

## Overview

The Article Enricher takes a markdown article and a list of keywords, then:
1. Searches local SQLite databases for matching links and images
2. Uses an LLM (via OpenRouter API) to intelligently insert exactly 2 links and 2 images
3. Outputs an enriched markdown file following brand guidelines

## Prerequisites

- Python 3.11 or higher
- OpenRouter API key

## Installation

1. Clone or download the project 
```bash
git clone https://github.com/GloryKO/Article-Enricher.git article_enricher
```
2. Install `uv`(if you haven't already):

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

run :

```bash
  source ~/.zshrc
```
3. Navigate Navigate to the project directory and install dependencies:
```bash
    cd article_enricher
```
```bash
uv sync
```
This will:

- Create a virtual environment automatically
- Install all dependencies from pyproject.toml
- Install the project in editable mode

4. Create a `.env` file in the root directory with your OpenRouter API key:

```
OPENROUTER_API_KEY=your_api_key_here
```
Note: uv automatically manages the virtual environment. If you need to activate it manually for other tools, 
use source .venv/bin/activate (or .venv\Scripts\activate on Windows).

## Database Setup
The application expects two SQLite databases:

### `links.db`
- Table: `resources`
- Columns: `id`, `url`, `title`, `description`, `topic_tags`, `type`

### `media.db`  
- Table: `images`
- Columns: `id`, `url`, `title`, `description`, `tags`

You can inspect your database schemas using:
```bash
uv run python main.py
```

## Usage

### Article Enrichment

Run the enrichment pipeline:

```bash
uv run python run.py --article_path data/article_1.md --keywords_path data/keywords_1.txt
```

### FastAPI Application

The project also includes a FastAPI application for handling background tasks using Celery.

**1. Start the Celery Worker:**

In a separate terminal, start the Celery worker. This will listen for tasks from the Redis queue. Make sure you have Redis running on your machine.

```bash
uv run celery -A app.tasks worker --loglevel=info
```

**2. Start the FastAPI Server:**

In another terminal, start the FastAPI server using uvicorn.

```bash
uv run uvicorn app.main:app --reload
```

**3. Interact with the API:**

You can now send requests to the API.

*   **Start a new task:**

    ```bash
    curl -X POST "http://127.0.0.1:8000/start-task?x=5&y=10"
    ```

    This will return a `task_id`.

*   **Check task status:**

    ```bash
    curl http://127.0.0.1:8000/task-status/{task_id}
    ```

    Replace `{task_id}` with the ID you received from the previous step.


### Input Files

**Article file** (`data/article_1.md`):
- Standard markdown format
- Will be enriched with links and images

**Keywords file** (`data/keywords_1.txt`):
- One keyword per line
- Used to match against database tags
- Example:
  ```
  electric bike commuting
  e‑bike infrastructure
  urban cycling adoption
  ```

### Output

The enriched article is saved as `{original_name}_enriched.md` in the same directory.


## Brand Guidelines

The application follows strict brand rules defined in `data/brand_rules.txt`:
- Friendly-expert tone
- Descriptive alt-text for images (≤125 characters)
- Semantic markdown structure
- Proper link anchor text

## Logging

Logs are written to `logs/enrichment.log` and displayed in the console.

## Project Structure

```
article_enricher/
├── app/
│   ├── main.py           # FastAPI application
│   └── tasks.py          # Celery tasks
├── run.py              # Main entry point
├── main.py             # Database inspection utility
├── utils/
│   ├── prompt_builder.py   # LLM prompt construction
│   ├── llm_client.py      # OpenRouter API client
│   ├── db_utils.py        # Database query functions
│   └── logger.py          # Logging configuration
├── data/
│   ├── article_1.md       # Sample article
│   ├── article_2.md       # Sample article
│   ├── keywords_1.txt     # Sample keywords
│   ├── keywords_2.txt     # Sample keywords
│   └── brand_rules.txt    # Style guidelines
├── links.db           # Links database
├── media.db           # Images database
└── logs/              # Log files
```

## Troubleshooting
**Dependencies not installing**: Ensure you have a pyproject.toml file in the project root and are running uv sync from the correct directory

**No links/images found**: Check that your keywords match the tags in your databases using `uv run python main.py`

**LLM errors**: Verify your OpenRouter API key in the `.env` file

**File not found**: Ensure all paths are relative to the project root directory

**Module not found**: Make sure you're using uv run to execute Python scripts, which ensures they run in the correct virtual environment
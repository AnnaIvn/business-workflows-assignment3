import json
import os
from pathlib import Path

from openai import OpenAI


# Ollama configuration
MODEL_NAME = "qwen3:1.7b"
OLLAMA_BASE_URL = "http://localhost:11434/v1"

# Limit input size to avoid overwhelming the local model
MAX_INPUT_CHARS = 2500


def create_client() -> OpenAI:
    return OpenAI(
        base_url=os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL),
        api_key="ollama",
        timeout=900.0,
        max_retries=0
    )


def prepare_text(markdown: str) -> str:
    # Prepare Markdown text for the LLM
    markdown = markdown.strip()

    if not markdown:
        raise ValueError("The Markdown document is empty.")

    if len(markdown) > MAX_INPUT_CHARS:
        half = MAX_INPUT_CHARS // 2
        markdown = (
            markdown[:half]
            + "\n\n[Middle section omitted due to input length]\n\n"
            + markdown[-half:]
        )

    return markdown


def extract_metadata(markdown_path: str) -> dict:
    markdown_path = Path(markdown_path)

    if not markdown_path.exists():
        raise FileNotFoundError(
            f"Markdown file not found: {markdown_path}"
        )

    markdown = markdown_path.read_text(encoding="utf-8")
    markdown = prepare_text(markdown)

    prompt = f"""
/no_think

Analyze this research paper and extract its metadata.

Return a JSON object with exactly these fields:
- title: paper title
- summary: summary in 3 sentences
- keywords: list of 5 keywords
- category: one main subject category

Use only information from the document.
Do not invent facts.
Return valid JSON only.

DOCUMENT:

{markdown}
"""

    client = create_client()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
        max_tokens=1000,
        extra_body={"think": False}
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("The LLM returned an empty response.")

    try:
        metadata = json.loads(content)
        # print("\n--- GENERATED JSON ---")
        # print(json.dumps(metadata, indent=4, ensure_ascii=False))
        # print("--- END GENERATED JSON ---\n")
    except json.JSONDecodeError as error:
        raise ValueError(
            f"The LLM returned invalid JSON: {content}"
        ) from error

    # Validate the returned structure
    required_fields = ["title", "summary", "keywords", "category"]

    for field in required_fields:
        if field not in metadata:
            raise ValueError(f"Missing metadata field: {field}")

    if not isinstance(metadata["keywords"], list):
        raise ValueError("The keywords field must be a list.")

    for field in ["title", "summary", "category"]:
        if not isinstance(metadata[field], str) or not metadata[field].strip():
            raise ValueError(f"The {field} field must be a non-empty string.")

    return metadata
import sqlite3
import json

from pathlib import Path
from datetime import datetime, timezone


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "markdown" / "papers.db"


def initialize_database():
    """Create the database and papers table if they don't exist."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file TEXT NOT NULL UNIQUE,
                markdown_file TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                keywords TEXT NOT NULL,
                category TEXT NOT NULL,
                processed_at TEXT NOT NULL
            )
        """)

    print("Database initialized successfully.")


def save_paper_metadata(
    metadata: dict,
    source_file: str,
    markdown_file: str
):
    """Save extracted paper metadata to SQLite."""

    processed_at = datetime.now(timezone.utc).isoformat()

    keywords_json = json.dumps(
        metadata["keywords"],
        ensure_ascii=False
    )

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            INSERT INTO papers (
                source_file,
                markdown_file,
                title,
                summary,
                keywords,
                category,
                processed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(source_file) DO UPDATE SET
                markdown_file = excluded.markdown_file,
                title = excluded.title,
                summary = excluded.summary,
                keywords = excluded.keywords,
                category = excluded.category,
                processed_at = excluded.processed_at
        """, (
            source_file,
            markdown_file,
            metadata["title"],
            metadata["summary"],
            keywords_json,
            metadata["category"],
            processed_at
        ))

    print(f"Metadata saved for: {source_file}")


def get_all_papers():
    """Retrieve all papers from the database."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            "SELECT * FROM papers ORDER BY processed_at DESC"
        ).fetchall()

    papers = []

    for row in rows:
        paper = dict(row)
        paper["keywords"] = json.loads(paper["keywords"])
        papers.append(paper)

    return papers
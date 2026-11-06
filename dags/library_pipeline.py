from pathlib import Path
import sys
import pendulum
from datetime import timedelta

from airflow.sdk import dag, task


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
PAPERS_DIR = PROJECT_ROOT / "papers"
MARKDOWN_DIR = PROJECT_ROOT / "data" / "markdown"

# Make project modules available to Airflow
sys.path.insert(0, str(SRC_DIR))

from pdf_converter import convert_pdf_to_markdown
from llm_processor import extract_metadata
from database import (
    initialize_database,
    get_all_papers,
    save_paper_metadata
)
from html_generator import generate_html
from discord_notifications import send_discord_notification


@dag(
    dag_id="library_pipeline",
    description="Process research PDFs and build a searchable study library",
    schedule="0 8 * * *",
    start_date=pendulum.datetime(2026, 11, 6, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    tags=["library", "pdf", "llm"]
)
def research_library_pipeline():

    # Task 1: Discover PDFs that have not been processed yet
    @task
    def discover_new_pdfs():

        initialize_database()

        processed_papers = {
            paper["source_file"]
            for paper in get_all_papers()
        }

        PAPERS_DIR.mkdir(parents=True, exist_ok=True)

        pdf_files = sorted(
            path.resolve()
            for path in PAPERS_DIR.iterdir()
            if path.is_file() and path.suffix.lower() == ".pdf"
        )

        new_pdfs = [
            str(pdf)
            for pdf in pdf_files
            if str(pdf) not in processed_papers
        ]

        print(f"Found {len(pdf_files)} PDF files.")
        print(f"Found {len(new_pdfs)} new PDF files.")

        return new_pdfs

    # Task 2: Convert new PDFs to Markdown
    @task
    def convert_pdfs(pdf_paths):

        MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)

        converted_files = []

        for pdf_path in pdf_paths:
            pdf_path = Path(pdf_path)

            markdown_path = (
                MARKDOWN_DIR / f"{pdf_path.stem}.md"
            )

            convert_pdf_to_markdown(
                str(pdf_path),
                str(markdown_path)
            )

            converted_files.append({
                "pdf_path": str(pdf_path),
                "markdown_path": str(markdown_path)
            })

        return converted_files

    # Task 3: Extract metadata using the local LLM
    @task(execution_timeout=timedelta(minutes=20))
    def extract_paper_metadata(converted_files):

        papers_with_metadata = []

        for file_info in converted_files:

            print(
                f"Starting metadata extraction: {file_info['pdf_path']}",
                flush=True
            )

            metadata = extract_metadata(
                file_info["markdown_path"]
            )

            print(
                f"Finished metadata extraction: {metadata['title']}",
                flush=True
            )

            papers_with_metadata.append({
                **file_info,
                "metadata": metadata
            })

        return papers_with_metadata

    # Task 4: Save extracted metadata in SQLite
    @task
    def save_metadata(papers_with_metadata):

        saved_titles = []

        for paper in papers_with_metadata:

            save_paper_metadata(
                metadata=paper["metadata"],
                source_file=paper["pdf_path"],
                markdown_file=paper["markdown_path"]
            )

            saved_titles.append(paper["metadata"]["title"])

        print(f"Saved {len(saved_titles)} papers.")

        return saved_titles

    # Task 5: Regenerate the searchable HTML library
    @task
    def regenerate_html(saved_titles):
        output_path = generate_html()
        print(f"HTML library generated: {output_path}")
        return {
            "html_path": str(output_path),
            "saved_titles": saved_titles
        }

    # Task 6: Notify the user through Discord
    @task
    def send_notification(result):

        saved_titles = result["saved_titles"]
        html_path = result["html_path"]

        if saved_titles:
            title_list = "\n".join(
                f"- {title}" for title in saved_titles[:10]
            )

            message = (
                f"**Research Library: Processing completed**\n\n"
                f"Processed {len(saved_titles)} new paper(s):\n"
                f"{title_list}\n\n"
                f"HTML library updated: `{html_path}`"
            )
        else:
            message = (
                "**Research Library: Pipeline completed**\n\n"
                "No new PDF files were found. "
                "The existing HTML library was regenerated."
            )
        send_discord_notification(message)

    # Define task dependencies
    new_pdfs = discover_new_pdfs()
    converted_files = convert_pdfs(new_pdfs)
    papers_with_metadata = extract_paper_metadata(converted_files)
    saved_titles = save_metadata(papers_with_metadata)
    html_result = regenerate_html(saved_titles)
    send_notification(html_result)

research_library_pipeline()
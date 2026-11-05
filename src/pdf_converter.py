
from pathlib import Path
import pymupdf4llm


def convert_pdf_to_markdown(
    pdf_path: str,
    output_path: str | None = None
) -> str:
    pdf_path = Path(pdf_path)

    # Check that the input file exists
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("The input file must be a PDF.")

    # Convert PDF to Markdown
    markdown = pymupdf4llm.to_markdown(str(pdf_path))

    # Check that content was extracted
    if not markdown.strip():
        raise ValueError(f"No text could be extracted from {pdf_path.name}")

    # Save Markdown if an output path was provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")

    print(f"Successfully converted: {pdf_path.name}")

    return markdown

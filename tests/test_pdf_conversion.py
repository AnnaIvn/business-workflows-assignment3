
from pathlib import Path
import sys

# Allow importing modules from src/
sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src")
)

from pdf_converter import convert_pdf_to_markdown


pdf_path = "tests/bread.pdf"

output_path = "data/markdown/sample.md"

markdown = convert_pdf_to_markdown(
    pdf_path,
    output_path
)

print("\nExtracted Markdown preview:\n")
print(markdown[:1500])

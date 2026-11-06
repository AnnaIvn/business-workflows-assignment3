from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from llm_processor import extract_metadata
from database import initialize_database, save_paper_metadata, get_all_papers


markdown_path = PROJECT_ROOT / "data" / "markdown" / "bread.md"

metadata = extract_metadata(markdown_path)

print("\nExtracted metadata:\n")
print(json.dumps(metadata, indent=4, ensure_ascii=False))

initialize_database()

save_paper_metadata( # save metadata
    metadata=metadata,
    source_file="tests/bread.pdf",
    markdown_file="data/bread.md"
)

papers = get_all_papers() # verify what's in database

print("\nPapers stored in database:\n")
print(json.dumps(papers, indent=4, ensure_ascii=False))
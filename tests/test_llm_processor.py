from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from llm_processor import extract_metadata


markdown_path = PROJECT_ROOT / "data" / "markdown" / "bread.md"

metadata = extract_metadata(markdown_path)

print("\nExtracted metadata:\n")
print(json.dumps(metadata, indent=4, ensure_ascii=False))
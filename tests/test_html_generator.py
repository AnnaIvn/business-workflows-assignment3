from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from html_generator import generate_html

output_path = PROJECT_ROOT / "output" / "index.html"

generate_html(output_path)
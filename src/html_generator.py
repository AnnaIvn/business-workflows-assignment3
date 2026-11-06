
import html
from pathlib import Path

from database import get_all_papers


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "output" / "index.html"


def generate_html(output_path=None):
    papers = get_all_papers()

    if output_path is None:
        output_path = DEFAULT_OUTPUT

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate paper cards
    paper_cards = []

    categories = sorted({
        paper["category"] for paper in papers
    })

    for paper in papers:
        title = html.escape(paper["title"])
        summary = html.escape(paper["summary"])
        category = html.escape(paper["category"])
        processed_at = html.escape(paper["processed_at"])

        keywords = paper["keywords"]

        keyword_tags = "".join(
            f'<span class="keyword">{html.escape(str(keyword))}</span>'
            for keyword in keywords
        )

        # Text used by the search functionality
        searchable_text = html.escape(
            " ".join([
                paper["title"],
                paper["summary"],
                paper["category"],
                " ".join(keywords)
            ]).lower(),
            quote=True
        )

        paper_card = f"""
        <article class="paper-card"
                 data-category="{category}"
                 data-search="{searchable_text}">

            <h2>{title}</h2>

            <span class="category">{category}</span>

            <p class="summary">{summary}</p>

            <div class="keywords">
                {keyword_tags}
            </div>

            <p class="date">
                Processed: {processed_at}
            </p>

        </article>
        """

        paper_cards.append(paper_card)

    if not paper_cards:
        paper_content = """
        <p class="empty-message">
            No research papers have been added yet.
        </p>
        """
    else:
        paper_content = "\n".join(paper_cards)

    # Generate category filter options
    category_options = "\n".join(
        f'<option value="{html.escape(category, quote=True)}">'
        f'{html.escape(category)}</option>'
        for category in categories
    )

    # Complete HTML document
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Research Paper Library</title>

    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: Arial, sans-serif;
            background: #f4f6f9;
            color: #263238;
            margin: 0;
            padding: 30px 20px;
        }}

        .container {{
            max-width: 1000px;
            margin: auto;
        }}

        header {{
            margin-bottom: 30px;
        }}

        h1 {{
            color: #263b53;
            margin-bottom: 8px;
        }}

        .subtitle {{
            color: #667085;
        }}

        .filters {{
            display: flex;
            gap: 12px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }}

        input, select {{
            padding: 12px;
            border: 1px solid #ccd2d9;
            border-radius: 6px;
            font-size: 15px;
        }}

        input {{
            flex: 1;
            min-width: 220px;
        }}

        select {{
            min-width: 200px;
            background: white;
        }}

        .paper-card {{
            background: white;
            border: 1px solid #e0e5eb;
            border-radius: 8px;
            padding: 22px;
            margin-bottom: 18px;
        }}

        .paper-card h2 {{
            color: #263b53;
            font-size: 20px;
            margin-top: 0;
        }}

        .category {{
            display: inline-block;
            background: #e8eff8;
            color: #31577d;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 13px;
        }}

        .summary {{
            line-height: 1.6;
            color: #485465;
        }}

        .keywords {{
            display: flex;
            flex-wrap: wrap;
            gap: 7px;
            margin-top: 15px;
        }}

        .keyword {{
            background: #edf2ed;
            color: #45634b;
            padding: 5px 9px;
            border-radius: 4px;
            font-size: 12px;
        }}

        .date {{
            color: #89929e;
            font-size: 12px;
            margin-bottom: 0;
            margin-top: 18px;
        }}

        .results-count {{
            color: #667085;
            margin-bottom: 15px;
            font-size: 14px;
        }}

        .empty-message {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            text-align: center;
        }}

        .no-results {{
            display: none;
            text-align: center;
            color: #667085;
            padding: 30px;
        }}

        @media (max-width: 600px) {{
            body {{
                padding: 20px 12px;
            }}

            .filters {{
                flex-direction: column;
            }}

            input, select {{
                width: 100%;
            }}
        }}
    </style>
</head>

<body>

<div class="container">

    <header>
        <h1>Research Paper Library</h1>
        <p class="subtitle">
            Your searchable collection of research papers.
        </p>
    </header>

    <div class="filters">

        <input
            type="text"
            id="searchInput"
            placeholder="Search by title, summary or keywords..."
        >

        <select id="categoryFilter">
            <option value="">All categories</option>
            {category_options}
        </select>

    </div>

    <p class="results-count" id="resultsCount">
        {len(papers)} papers found
    </p>

    <main id="paperList">
        {paper_content}
    </main>

    <p class="no-results" id="noResults">
        No matching papers found.
    </p>

</div>

<script>
    const searchInput = document.getElementById("searchInput");
    const categoryFilter = document.getElementById("categoryFilter");
    const paperCards = document.querySelectorAll(".paper-card");
    const resultsCount = document.getElementById("resultsCount");
    const noResults = document.getElementById("noResults");

    function filterPapers() {{
        const searchTerm = searchInput.value.toLowerCase().trim();
        const selectedCategory = categoryFilter.value;

        let visibleCount = 0;

        paperCards.forEach(card => {{
            const searchText = card.dataset.search;
            const category = card.dataset.category;

            const matchesSearch = searchText.includes(searchTerm);

            const matchesCategory =
                selectedCategory === "" ||
                category === selectedCategory;

            const visible = matchesSearch && matchesCategory;

            card.style.display = visible ? "block" : "none";

            if (visible) {{
                visibleCount++;
            }}
        }});

        resultsCount.textContent =
            `${{visibleCount}} papers found`;

        noResults.style.display =
            visibleCount === 0 ? "block" : "none";
    }}

    searchInput.addEventListener("input", filterPapers);
    categoryFilter.addEventListener("change", filterPapers);
</script>

</body>
</html>
"""

    output_path.write_text(html_content, encoding="utf-8")

    print(f"HTML library generated: {output_path}")
    print(f"Number of papers: {len(papers)}")

    return output_path

import feedparser
import csv
from collections import defaultdict
import time
from urllib.parse import quote
import requests
import re

# Farama project keywords to search for and match
FARAMA_PROJECTS = {
    "PettingZoo": ["PettingZoo", "terry2021pettingzoo"],
    "Gymnasium": ["Gymnasium", "Farama Gymnasium", "towers2024gymnasium"],
    "SuperSuit": ["SuperSuit", "SuperSuit wrapper", "SuperSuit"],
    "MiniGrid": ["MiniGrid", "minigrid environment", "MinigridMiniworld23"],
    "Minari": ["Minari", "minari", "minari2024"],
    "MetaWorld+": ["Meta-World+", "MetaWorld", "mclean2025metaworldimprovedstandardizedrl"],
    "Shimmy": ["Shimmy"],
    "Gymnasium Robotics": ["Gymnasium Robotics"],
    "MAgent": ["MAgent", "magent2020", "zheng2018magent"],
    "MOMAland": ["MOMAland", "felten2024momaland"],
    "ViZDoom": ["ViZDoom", "Wydmuch2019ViZdoom", "Kempka2016ViZDoom"],
    "ALE": ["Arcade Learning Environment", "ALE", "bellemare13arcade", "machado18arcade", "farebrother2024cale"],
    "ChatArena": ["ChatArena", "chatarena"],
    "CrowdPlay": ["CrowdPlay", "gerstgrasser2022crowdplay"],
    "Highway-env": ["Highway-env", "highway-env"],
    "Stable-Retro": ["Stable Retro", "stable-retro"],
    "BabyAI": ["BabyAI", "chevalier2018babyai"],
    "Multi-Agent Actor-Critic": ["Multi-Agent Actor-Critic", "lowe2017multi"],
    "Workflow-Guided Exploration": ["Workflow-Guided Exploration", "liu2018reinforcement"],
    "Mordatch Language Emergence": ["Emergence of Grounded Compositional Language", "mordatch2017emergence"],
    "Procgen2": ["Procgen2"],
    "Jumpy": ["Jumpy"]
}

PARTIAL_MATCH_PATTERNS = {
    "PettingZoo": r"pettingzoo[-_.a-z0-9]*",
    "Gymnasium": r"gymnasium[-_.a-z0-9]*",
    "MiniGrid": r"minigrid[-_.a-z0-9]*",
    "Minari": r"minari[-_.a-z0-9]*",
    "MetaWorld+": r"metaworld[-_.a-z0-9]*",
    "Shimmy": r"shimmy[-_.a-z0-9]*",
    "Gymnasium Robotics": r"gymnasium[-_.a-z0-9]*robotics",
    "MAgent": r"magent[-_.a-z0-9]*",
    "ViZDoom": r"vizdoom[-_.a-z0-9]*",
    "SuperSuit": r"supersuit[-_.a-z0-9]*",
    "ALE": r"ale[-_.a-z0-9]*",
    "ChatArena": r"chatarena[-_.a-z0-9]*",
    "Procgen2": r"procgen2[-_.a-z0-9]*",
    "Jumpy": r"jumpy[-_.a-z0-9]*"
}

def build_query(keywords):
    """Build and URL-encode a single keyword for arXiv search."""
    return quote(f'all:"{keywords}"')

def search_arxiv_paginated(keywords, batch_size=100):
    """Search arXiv for each keyword with deep pagination (no max limit)."""
    base_url = 'http://export.arxiv.org/api/query?'
    seen_urls = set()
    results = defaultdict(list)

    for project, kws in keywords.items():
        for kw in kws:
            print(f"Searching arXiv for: {kw}")
            start = 0
            while True:
                query = build_query(kw)
                url = f'{base_url}search_query={query}&start={start}&max_results={batch_size}'
                feed = feedparser.parse(url)
                if not feed.entries:
                    break
                for entry in feed.entries:
                    if entry.link not in seen_urls:
                        text = f"{entry.title} {entry.summary} {entry.get('arxiv_comment', '')}"
                        matched = detect_projects(text, {project: kws})
                        if matched:
                            results[project].append({
                                "title": entry.title,
                                "url": entry.link,
                                "summary": entry.summary.replace("\n", " ").strip()
                            })
                            seen_urls.add(entry.link)
                start += batch_size
                time.sleep(0.5)
    return results, seen_urls

def search_semantic_scholar(keywords, seen_ids):
    """Query Semantic Scholar API and return unique papers mentioning Farama keywords."""
    headers = {"User-Agent": "FaramaPaperScraper/1.0"}
    project_results = defaultdict(list)

    for project, kws in keywords.items():
        for kw in kws:
            print(f"Querying Semantic Scholar for: {kw}")
            response = requests.get(
                f"https://api.semanticscholar.org/graph/v1/paper/search?query={quote(kw)}&limit=100&fields=title,url,abstract",
                headers=headers
            )
            if response.status_code != 200:
                continue
            data = response.json()
            for paper in data.get("data", []):
                pid = paper.get("url")
                if pid and pid not in seen_ids:
                    seen_ids.add(pid)
                    text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                    matched_projects = detect_projects(text, keywords)
                    for match in matched_projects:
                        project_results[match].append({
                            "title": paper.get("title", ""),
                            "url": paper.get("url", ""),
                            "summary": paper.get("abstract", "")
                        })
            time.sleep(1)
    return project_results

def detect_projects(text, project_keywords):
    """Detect which Farama projects are referenced in a text using partial word matching."""
    matches = []
    for project, keywords in project_keywords.items():
        if any(re.search(re.escape(kw), text, re.IGNORECASE) for kw in keywords):
            matches.append(project)
        elif project in PARTIAL_MATCH_PATTERNS:
            if re.search(PARTIAL_MATCH_PATTERNS[project], text, re.IGNORECASE):
                matches.append(project)
    return matches

def run_scraper():
    print("\nQuerying arXiv...")
    arxiv_results, seen_urls = search_arxiv_paginated(FARAMA_PROJECTS)

    print("\nQuerying Semantic Scholar...")
    ss_results = search_semantic_scholar(FARAMA_PROJECTS, seen_urls)

    results = defaultdict(list)
    for project, papers in arxiv_results.items():
        results[project].extend(papers)
    for project, papers in ss_results.items():
        results[project].extend(papers)

    with open("csv/farama_all_papers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Project", "Title", "URL"])
        for project, papers in results.items():
            for paper in papers:
                writer.writerow([project, paper["title"], paper["url"]])

    print("\nTally by project:")
    for project, papers in results.items():
        print(f"{project}: {len(papers)} papers")

if __name__ == "__main__":
    run_scraper()

"""
Freelance Lead Finder Agent
Searches the web for people looking for web developers, websites, or related services.
Returns qualified leads with context for Howard to pitch.

Usage:
    python agents/freelance-finder/finder.py
    python agents/freelance-finder/finder.py --query "need a website built"
    python agents/freelance-finder/finder.py --platform reddit
"""

import json
import os
import sys
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Default search queries -- things potential clients would say
DEFAULT_QUERIES = [
    "looking for someone to build my website reddit",
    "need a web developer for my small business reddit",
    "hire web developer for landing page reddit",
    "looking for freelance web developer",
    "need help building a website for my business",
]

# Platforms to search on
PLATFORM_SEARCHES = {
    "reddit": "site:reddit.com",
    "facebook": "site:facebook.com",
    "twitter": "site:twitter.com OR site:x.com",
    "general": "",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def search_web(query, num_results=10):
    """Search DuckDuckGo HTML and return result links + snippets."""
    results = []
    search_url = "https://html.duckduckgo.com/html/"
    params = {"q": query}

    try:
        resp = requests.post(search_url, data=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for r in soup.select("div.result"):
            link_el = r.select_one("a.result__a")
            snippet_el = r.select_one("a.result__snippet")

            if link_el and link_el.get("href"):
                url = link_el["href"]
                title = link_el.get_text(strip=True)
                snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "source": extract_platform(url),
                })

            if len(results) >= num_results:
                break
    except Exception as e:
        print(f"  Search error: {e}")

    return results


def extract_platform(url):
    if "reddit.com" in url:
        return "Reddit"
    elif "facebook.com" in url:
        return "Facebook"
    elif "twitter.com" in url or "x.com" in url:
        return "Twitter/X"
    elif "upwork.com" in url:
        return "Upwork"
    elif "fiverr.com" in url:
        return "Fiverr"
    else:
        return "Web"


def find_leads(queries=None, platform="general", max_per_query=5):
    """Search for freelance leads across the web."""
    if queries is None:
        queries = DEFAULT_QUERIES

    platform_filter = PLATFORM_SEARCHES.get(platform, "")
    all_leads = []
    seen_urls = set()

    for query in queries:
        full_query = f"{query} {platform_filter}".strip()
        print(f"Searching: {full_query}")

        results = search_web(full_query, max_per_query)
        for r in results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                all_leads.append(r)

    return all_leads


def score_lead(lead):
    """Basic scoring: how likely is this a real lead?"""
    score = 0
    text = (lead.get("title", "") + " " + lead.get("snippet", "")).lower()

    # Positive signals
    if any(w in text for w in ["need", "looking for", "hire", "help me", "build"]):
        score += 2
    if any(w in text for w in ["website", "landing page", "web developer", "frontend"]):
        score += 2
    if any(w in text for w in ["budget", "pay", "price", "quote", "$"]):
        score += 3
    if any(w in text for w in ["asap", "urgent", "this week", "deadline"]):
        score += 2
    if lead.get("source") in ["Reddit", "Facebook"]:
        score += 1

    # Negative signals
    if any(w in text for w in ["tutorial", "how to", "course", "learn"]):
        score -= 3
    if any(w in text for w in ["free", "volunteer"]):
        score -= 2

    lead["score"] = max(score, 0)
    return lead


def save_results(leads):
    today = date.today().isoformat()
    filepath = os.path.join(DATA_DIR, f"{today}_leads.json")
    with open(filepath, "w") as f:
        json.dump({"date": today, "lead_count": len(leads), "leads": leads}, f, indent=2)
    return filepath


def print_report(leads):
    scored = [score_lead(l) for l in leads]
    scored.sort(key=lambda x: x["score"], reverse=True)

    print(f"\n{'='*60}")
    print(f"FREELANCE LEADS REPORT")
    print(f"Date: {date.today().isoformat()} | Found: {len(scored)} leads")
    print(f"{'='*60}")

    if not scored:
        print("\nNo leads found. Try different search queries.")
        return scored

    top = [l for l in scored if l["score"] >= 3]
    rest = [l for l in scored if l["score"] < 3]

    if top:
        print(f"\nHOT LEADS ({len(top)}):")
        for i, l in enumerate(top, 1):
            print(f"\n  {i}. [{l['source']}] {l['title']}")
            if l["snippet"]:
                print(f"     {l['snippet'][:120]}...")
            print(f"     URL: {l['url']}")
            print(f"     Score: {l['score']}/10")

    if rest:
        print(f"\nOTHER LEADS ({len(rest)}):")
        for i, l in enumerate(rest, 1):
            print(f"  {i}. [{l['source']}] {l['title'][:60]} -- {l['url']}")

    print(f"\n{'='*60}")
    print("Next steps: Review hot leads, draft pitches for the top 2-3.")
    print(f"{'='*60}\n")

    return scored


def find(queries=None, platform="general", max_per_query=5):
    """Main entry point."""
    print("Finding freelance leads...")
    leads = find_leads(queries, platform, max_per_query)
    scored = print_report(leads)
    if scored:
        filepath = save_results(scored)
        print(f"Data saved to: {filepath}")
    return scored


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Freelance Lead Finder")
    parser.add_argument("--query", help="Custom search query (overrides defaults)")
    parser.add_argument("--platform", choices=["reddit", "facebook", "twitter", "general"],
                        default="general", help="Platform to search (default: general)")
    parser.add_argument("--max", type=int, default=5, help="Max results per query (default: 5)")
    args = parser.parse_args()

    queries = [args.query] if args.query else None
    find(queries, args.platform, args.max)

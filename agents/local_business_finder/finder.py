"""
Local Business Finder Agent
Searches Google Maps for businesses in Cavite that don't have a website.
These are hot leads -- build them a demo site + pitch BookMe.

Usage:
    python3 agents/local_business_finder/finder.py
    python3 agents/local_business_finder/finder.py --city "Cavite City"
    python3 agents/local_business_finder/finder.py --category "barbershop" --max 10

Requires: GOOGLE_MAPS_API_KEY in .env
Get a key: https://console.cloud.google.com/apis/library/places-backend.googleapis.com
"""

import json
import os
import time
from datetime import date

import requests
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

DEFAULT_CITY = "Cavite, Philippines"

# Business types that BookMe is built for and likely have no website
DEFAULT_CATEGORIES = [
    "barbershop",
    "photography studio",
    "dental clinic",
    "tutorial center",
    "nail salon",
    "massage spa",
    "catering service",
]


def text_search(query, api_key):
    """Search Google Places Text Search API."""
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    try:
        resp = requests.get(url, params={"query": query, "key": api_key}, timeout=10)
        data = resp.json()
        status = data.get("status")
        if status not in ("OK", "ZERO_RESULTS"):
            print(f"  Places API error: {status} - {data.get('error_message', '')}")
            return []
        return data.get("results", [])
    except Exception as e:
        print(f"  Search error: {e}")
        return []


def get_place_details(place_id, api_key):
    """Get website, phone, and Maps URL for a specific place."""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,website,formatted_phone_number,rating,user_ratings_total,url,formatted_address",
        "key": api_key,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("status") != "OK":
            return None
        return data.get("result", {})
    except Exception as e:
        print(f"  Details error: {e}")
        return None


def score_lead(business):
    """
    Score how good a lead this is.
    No website = required (already filtered for this).
    More reviews = established business worth pitching.
    Lower rating = they have problems, more receptive to help.
    Has phone = reachable.
    """
    score = 0

    reviews = business.get("user_ratings_total", 0)
    if reviews >= 50:
        score += 3
    elif reviews >= 20:
        score += 2
    elif reviews >= 5:
        score += 1

    rating = business.get("rating", 0)
    if 0 < rating <= 3.5:
        score += 2  # Low rating = unhappy customers, open to improvement
    elif 3.5 < rating <= 4.2:
        score += 1

    if business.get("phone"):
        score += 1  # Has a contact number = reachable

    business["score"] = score
    return business


def find_leads(city=DEFAULT_CITY, categories=None, max_per_category=5):
    """Run searches and return businesses without websites."""
    if not GOOGLE_MAPS_API_KEY:
        print("ERROR: GOOGLE_MAPS_API_KEY not set in .env")
        print("Get a free key at: https://console.cloud.google.com/apis/library/places-backend.googleapis.com")
        return []

    if categories is None:
        categories = DEFAULT_CATEGORIES

    all_leads = []
    seen_ids = set()

    for category in categories:
        query = f"{category} in {city}"
        print(f"  Searching: {query}")

        results = text_search(query, GOOGLE_MAPS_API_KEY)
        found = 0

        for r in results:
            if found >= max_per_category:
                break

            place_id = r.get("place_id")
            if not place_id or place_id in seen_ids:
                continue
            seen_ids.add(place_id)

            time.sleep(0.2)  # avoid hammering the API
            details = get_place_details(place_id, GOOGLE_MAPS_API_KEY)
            if not details:
                continue

            # Skip businesses that already have a website
            if details.get("website"):
                continue

            business = {
                "name": details.get("name", r.get("name", "")),
                "category": category,
                "address": details.get("formatted_address", r.get("formatted_address", "")),
                "phone": details.get("formatted_phone_number", ""),
                "website": "",
                "rating": details.get("rating", r.get("rating", 0)),
                "user_ratings_total": details.get("user_ratings_total", r.get("user_ratings_total", 0)),
                "maps_url": details.get("url", ""),
            }

            all_leads.append(score_lead(business))
            found += 1

        print(f"    Found {found} leads without websites")

    return all_leads


def save_results(leads):
    today = date.today().isoformat()
    filepath = os.path.join(DATA_DIR, f"{today}_local_leads.json")
    with open(filepath, "w") as f:
        json.dump({"date": today, "lead_count": len(leads), "leads": leads}, f, indent=2)
    return filepath


def print_report(leads):
    leads_sorted = sorted(leads, key=lambda x: x.get("score", 0), reverse=True)

    print(f"\n{'='*60}")
    print("LOCAL BUSINESS LEADS (No Website)")
    print(f"Date: {date.today().isoformat()} | Found: {len(leads_sorted)} leads")
    print(f"{'='*60}")

    if not leads_sorted:
        print("\nNo leads found. Try a different city or category.")
        return leads_sorted

    for i, b in enumerate(leads_sorted, 1):
        rating_str = f"{b['rating']}/5 ({b['user_ratings_total']} reviews)" if b.get("rating") else "No ratings"
        print(f"\n{i}. {b['name']}  [{b['category'].title()}]")
        print(f"   Address : {b['address']}")
        print(f"   Phone   : {b['phone'] or 'Not listed'}")
        print(f"   Rating  : {rating_str}")
        print(f"   Maps    : {b['maps_url']}")
        print(f"   Score   : {b['score']}/6")

    print(f"\n{'='*60}")
    print("Next step: Build a demo site for the top 2-3, then message them.")
    print(f"{'='*60}\n")

    return leads_sorted


def find(city=DEFAULT_CITY, categories=None, max_per_category=5):
    """Main entry point called by morning_briefing.py."""
    print(f"Searching for businesses without websites in {city}...")
    leads = find_leads(city, categories, max_per_category)
    sorted_leads = print_report(leads)
    if sorted_leads:
        filepath = save_results(sorted_leads)
        print(f"Data saved to: {filepath}")
    return sorted_leads


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find local businesses without websites on Google Maps")
    parser.add_argument("--city", default=DEFAULT_CITY, help=f"City to search (default: {DEFAULT_CITY})")
    parser.add_argument("--category", help="Single category to search (overrides defaults)")
    parser.add_argument("--max", type=int, default=5, help="Max leads per category (default: 5)")
    args = parser.parse_args()

    categories = [args.category] if args.category else None
    find(args.city, categories, args.max)

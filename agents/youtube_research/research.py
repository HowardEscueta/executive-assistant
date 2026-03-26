"""
YouTube Research Agent
Quick research tool for Howard's morning kickoff and content planning.
Searches YouTube for trending videos in specified topics, returns a concise summary.

Usage:
    python agents/youtube-research/research.py "AI automation"
    python agents/youtube-research/research.py "web development tips" --max 10
    python agents/youtube-research/research.py "AI automation" --new-only
"""

import json
import os
import re
import sys
from datetime import datetime, date, timedelta

from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def get_youtube_client():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("ERROR: YOUTUBE_API_KEY not found in .env")
        sys.exit(1)
    return build("youtube", "v3", developerKey=api_key)


def parse_duration(duration_str):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    h = int(match.group(1) or 0)
    m = int(match.group(2) or 0)
    s = int(match.group(3) or 0)
    return h * 3600 + m * 60 + s


def search_trending(query, max_results=10, new_only=False):
    """Search YouTube and return enriched video data."""
    youtube = get_youtube_client()

    # Search for videos
    search_params = {
        "q": query,
        "part": "id",
        "type": "video",
        "order": "relevance",
        "maxResults": min(max_results, 50),
        "relevanceLanguage": "en",
    }

    if new_only:
        week_ago = (date.today() - timedelta(days=7)).isoformat() + "T00:00:00Z"
        search_params["publishedAfter"] = week_ago

    response = youtube.search().list(**search_params).execute()
    video_ids = [item["id"]["videoId"] for item in response.get("items", [])]

    if not video_ids:
        return []

    # Get full details
    details = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids),
    ).execute()

    videos = []
    for item in details.get("items", []):
        snippet = item["snippet"]
        stats = item.get("statistics", {})
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        upload_date = snippet.get("publishedAt", "")[:10]
        duration = parse_duration(item.get("contentDetails", {}).get("duration", "PT0S"))

        days_since = 1
        if upload_date:
            try:
                days_since = max((datetime.now() - datetime.strptime(upload_date, "%Y-%m-%d")).days, 1)
            except ValueError:
                pass

        videos.append({
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "views": views,
            "likes": likes,
            "engagement_rate": round(likes / views * 100, 2) if views > 0 else 0,
            "views_per_day": round(views / days_since),
            "upload_date": upload_date,
            "duration_min": f"{duration // 60}m{duration % 60}s",
            "url": f"https://www.youtube.com/watch?v={item['id']}",
            "tags": snippet.get("tags", [])[:5],
        })

    # Sort by engagement rate
    videos.sort(key=lambda v: v["engagement_rate"], reverse=True)
    return videos


def save_results(query, videos):
    today = date.today().isoformat()
    safe_query = query.replace(" ", "_").lower()
    filepath = os.path.join(DATA_DIR, f"{today}_{safe_query}.json")
    with open(filepath, "w") as f:
        json.dump({"query": query, "date": today, "videos": videos}, f, indent=2)
    return filepath


def print_report(query, videos):
    print(f"\n{'='*60}")
    print(f"YOUTUBE RESEARCH: {query}")
    print(f"Date: {date.today().isoformat()} | Found: {len(videos)} videos")
    print(f"{'='*60}")

    for i, v in enumerate(videos[:10], 1):
        print(f"\n{i}. {v['title']}")
        print(f"   Channel: {v['channel']}")
        print(f"   Views: {v['views']:,} | Likes: {v['likes']:,} | Engagement: {v['engagement_rate']}%")
        print(f"   Views/day: {v['views_per_day']:,} | Duration: {v['duration_min']} | Uploaded: {v['upload_date']}")
        print(f"   URL: {v['url']}")

    # Quick insights
    if videos:
        avg_engagement = sum(v["engagement_rate"] for v in videos) / len(videos)
        avg_views = sum(v["views"] for v in videos) / len(videos)
        top_channels = list(set(v["channel"] for v in videos[:5]))

        print(f"\n{'='*60}")
        print("QUICK INSIGHTS")
        print(f"  Avg engagement: {avg_engagement:.2f}%")
        print(f"  Avg views: {avg_views:,.0f}")
        print(f"  Top channels: {', '.join(top_channels)}")

        # Common tags
        all_tags = []
        for v in videos:
            all_tags.extend(v.get("tags", []))
        if all_tags:
            from collections import Counter
            common = Counter(all_tags).most_common(5)
            print(f"  Trending tags: {', '.join(t[0] for t in common)}")

    print(f"{'='*60}\n")


def _is_english_or_filipino(title, channel, tags, description):
    """
    Strict filter: ONLY allow songs that are clearly English (American/Western)
    or Filipino/Tagalog. Block everything else.
    """
    text = f"{title} {channel} {' '.join(tags)} {description}".lower()

    # Block: any non-Latin characters in title (CJK, Devanagari, Arabic, Cyrillic, etc.)
    for c in title:
        cp = ord(c)
        # Allow basic Latin, Latin Extended, punctuation, digits, common symbols
        if cp > 0x024F and cp not in range(0x2000, 0x206F):  # general punctuation ok
            return False

    # Explicitly allow: Filipino/Tagalog indicators
    filipino_words = ["opm", "tagalog", "filipino", "pinoy", "p-pop",
                      "bisaya", "visayan", "hugot", "kanta", "awitin",
                      "wish 107.5", "sb19", "bgyo", "bini", "ppop",
                      "manila", "philippines"]
    if any(w in text for w in filipino_words):
        return True

    # Block: non-English/non-Filipino language keywords
    block_words = [
        # Indian languages
        "hindi", "bollywood", "punjabi", "tamil", "telugu", "bengali",
        "bhojpuri", "marathi", "gujarati", "kannada", "malayalam",
        "rajasthani", "haryanvi", "santali", "konkani", "devotional",
        "bhajan", "meenawati", "chhattisgarh", "garo", "bodo",
        "bwisagu", "assamese", "nepali", "pashto", "urdu", "farsi",
        "chakma", "mizo", "manipuri",
        # Other languages
        "arabic", "nasheed", "turkish", "russian", "korean",
        "japanese", "chinese", "thai", "vietnamese", "indonesian",
        "malay", "burmese", "khmer", "lao",
        # Latin American (non-US mainstream)
        "reggaeton", "corrido", "cumbia", "bachata", "vallenato",
        "sertanejo", "forr", "pagode",
        # African
        "afrobeats", "amapiano", "bongo flava",
        # Worship/religious (non-mainstream)
        "worship song", "gospel song", "praise and worship",
        "christian song", "zinda khuda",
    ]
    if any(w in text for w in block_words):
        return False

    # Default: allow (likely English)
    return True


def _has_lyrics_in_video(title, tags):
    """Check if the video already contains lyrics (Howard wants to ADD lyrics himself)."""
    text = f"{title} {' '.join(tags)}".lower()
    lyrics_words = ["lyrics", "lyric video", "lyric vid", "with lyrics",
                    "letra", "lyrics video", "(lyrics)", "[lyrics]"]
    return any(w in text for w in lyrics_words)


def search_new_songs(max_results=15):
    """
    Search for brand new individual songs (not playlists/compilations).
    ONLY English (American) and Filipino/Tagalog songs.
    EXCLUDES videos that already have lyrics.
    Filters: Music category, uploaded in last 7 days, under 10 minutes.
    """
    youtube = get_youtube_client()
    week_ago = (date.today() - timedelta(days=7)).isoformat() + "T00:00:00Z"

    queries = [
        # English songs
        ("new song official music video", "en"),
        ("new pop song official video 2026", "en"),
        ("new R&B song official video", "en"),
        ("new hip hop song official video 2026", "en"),
        # Filipino/OPM songs
        ("new OPM song official music video", None),
        ("bagong kanta OPM 2026", None),
        ("P-pop new song 2026", None),
    ]

    all_ids = []
    for q, lang in queries:
        try:
            params = {
                "q": q,
                "part": "id",
                "type": "video",
                "order": "date",
                "maxResults": 20,
                "publishedAfter": week_ago,
                "videoCategoryId": "10",
                "videoDuration": "medium",
            }
            if lang:
                params["relevanceLanguage"] = lang
            response = youtube.search().list(**params).execute()
            all_ids.extend(item["id"]["videoId"] for item in response.get("items", []))
        except Exception as e:
            print(f"  Search error for '{q}': {e}")

    # Deduplicate
    seen = set()
    unique_ids = []
    for vid in all_ids:
        if vid not in seen:
            seen.add(vid)
            unique_ids.append(vid)

    if not unique_ids:
        return []

    # Get details
    details = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(unique_ids[:50]),
    ).execute()

    songs = []
    for item in details.get("items", []):
        snippet = item["snippet"]
        stats = item.get("statistics", {})
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        upload_date = snippet.get("publishedAt", "")[:10]
        duration = parse_duration(item.get("contentDetails", {}).get("duration", "PT0S"))
        title = snippet.get("title", "")
        tags = snippet.get("tags", []) or []
        description = (snippet.get("description", "") or "")[:300]
        channel = snippet.get("channelTitle", "")

        # Skip compilations, playlists, mixes
        title_lower = title.lower()
        skip_words = ["playlist", "compilation", "mix 20", "top hits", "top opm", "nonstop",
                       "best of", "collection", "mashup", "1 hour", "2 hour", "medley",
                       "top 10", "top 20", "top 50"]
        if any(w in title_lower for w in skip_words):
            continue

        # Skip if longer than 10 minutes
        if duration > 600:
            continue

        # ONLY English or Filipino songs
        if not _is_english_or_filipino(title, channel, tags, description):
            continue

        # SKIP videos that already have lyrics
        if _has_lyrics_in_video(title, tags):
            continue

        days_since = 1
        if upload_date:
            try:
                days_since = max((datetime.now() - datetime.strptime(upload_date, "%Y-%m-%d")).days, 1)
            except ValueError:
                pass

        songs.append({
            "title": title,
            "channel": channel,
            "views": views,
            "likes": likes,
            "engagement_rate": round(likes / views * 100, 2) if views > 0 else 0,
            "views_per_day": round(views / days_since),
            "upload_date": upload_date,
            "duration_min": f"{duration // 60}m{duration % 60}s",
            "url": f"https://www.youtube.com/watch?v={item['id']}",
            "tags": tags[:5],
        })

    # Sort by most recent first, then by views
    songs.sort(key=lambda v: (v["upload_date"], v["views"]), reverse=True)
    return songs[:max_results]


def research(query, max_results=10, new_only=False):
    """Main entry point. Returns videos list and saves to disk."""
    print(f"Researching: '{query}'...")
    videos = search_trending(query, max_results, new_only)
    if videos:
        filepath = save_results(query, videos)
        print_report(query, videos)
        print(f"Data saved to: {filepath}")
    else:
        print(f"No videos found for '{query}'.")
    return videos


def research_new_songs(max_results=10):
    """Search for new individual songs. Returns list and saves to disk."""
    print("Searching for new songs (English + Tagalog)...")
    songs = search_new_songs(max_results)
    if songs:
        filepath = save_results("new_songs", songs)
        print_report("New Songs (This Week)", songs)
        print(f"Data saved to: {filepath}")
    else:
        print("No new songs found this week.")
    return songs


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube Research Agent")
    parser.add_argument("query", nargs="?", default=None, help="Topic to search")
    parser.add_argument("--max", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("--new-only", action="store_true", help="Only videos from last 7 days")
    parser.add_argument("--new-songs", action="store_true", help="Search for new songs specifically")
    args = parser.parse_args()

    if args.new_songs:
        research_new_songs(args.max)
    elif args.query:
        research(args.query, args.max, args.new_only)
    else:
        print("Usage: research.py 'topic' or research.py --new-songs")
        print("  research.py 'AI automation' --max 10 --new-only")
        print("  research.py --new-songs --max 15")

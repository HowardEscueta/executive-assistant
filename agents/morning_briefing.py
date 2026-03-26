"""
Morning Briefing Runner
Runs all 3 research agents and sends results via email.

Usage:
    python3 agents/morning_briefing.py
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "agents"))

from agents.youtube_research.research import research, research_new_songs
from agents.freelance_finder.finder import find
from agents.emailer import send_briefing


def run_briefing():
    print("=" * 60)
    print("RUNNING MORNING BRIEFING")
    print("=" * 60)

    # 1. New songs
    print("\n[1/3] Searching for new songs...")
    new_songs = research_new_songs(max_results=10)

    # 2. AI automation trends
    print("\n[2/3] Searching AI automation trends...")
    ai_trends = research("AI automation", max_results=5, new_only=True)

    # 3. Freelance leads
    print("\n[3/3] Finding freelance leads...")
    leads = find()

    # 4. Send email
    print("\n[EMAIL] Sending briefing...")
    success = send_briefing(new_songs=new_songs, ai_trends=ai_trends, leads=leads)

    if success:
        print("\nBriefing sent! Check your email.")
    else:
        print("\nEmail failed, but results are saved locally.")

    return new_songs, ai_trends, leads


if __name__ == "__main__":
    run_briefing()

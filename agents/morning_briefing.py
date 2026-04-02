"""
Morning Briefing Runner
Runs all 3 research agents, generates PPT report, and sends email with attachment.

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
from agents.local_business_finder.finder import find as find_local_businesses
from agents.report import generate_report
from agents.emailer import send_briefing


def run_briefing():
    print("=" * 60)
    print("RUNNING MORNING BRIEFING")
    print("=" * 60)

    # 1. New songs (English + Filipino only, no lyrics videos)
    print("\n[1/4] Searching for new songs...")
    new_songs = research_new_songs(max_results=10)

    # 2. AI automation trends
    print("\n[2/4] Searching AI automation trends...")
    ai_trends = research("AI automation", max_results=5, new_only=True)

    # 3. Freelance leads
    print("\n[3/4] Finding freelance leads...")
    leads = find()

    # 4. Local businesses without websites (Cavite)
    print("\n[4/4] Finding local businesses without websites...")
    local_leads = find_local_businesses()

    # 5. Generate PowerPoint report
    print("\n[REPORT] Generating PowerPoint...")
    pptx_path = generate_report(new_songs=new_songs, ai_trends=ai_trends, leads=leads, local_leads=local_leads)

    # 6. Send email with PPT attached
    print("\n[EMAIL] Sending briefing with PPT...")
    success = send_briefing(new_songs=new_songs, ai_trends=ai_trends, leads=leads, local_leads=local_leads, pptx_path=pptx_path)

    if success:
        print("\nBriefing sent! Check your email.")
    else:
        print("\nEmail failed, but results are saved locally.")

    return new_songs, ai_trends, leads, local_leads


if __name__ == "__main__":
    run_briefing()

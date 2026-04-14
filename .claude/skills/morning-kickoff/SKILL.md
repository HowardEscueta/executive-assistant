# Morning Kickoff

Run this when Howard checks in for the day (says hey, good morning, what's up, etc.).

## Steps

1. **Daily habits reminder:**
   - Make your bed
   - Walk Chopper
   - Work out
   - Eat something healthy

2. **Today's priorities:** Read `context/current-priorities.md` and surface the top 2-3 things to focus on today.

3. **Open items:** Check `decisions/log.md` and any active project READMEs in `projects/` for pending items or next steps.

4. **New Songs Research** (Claude does this directly using WebSearch/WebFetch):
   - Search music blogs for this week's real new releases (Official Charts, Billboard, Spotify New Music Friday, etc.)
   - Only English (American) and Filipino/OPM songs
   - Only songs that do NOT already have lyrics videos
   - Find 10+ verified real artist releases
   - For each song, search YouTube for the official music video and include the URL
   - Save results to `agents/youtube_research/data/`

5. **Freelance Leads** (Claude does this directly using WebSearch):
   - Search Freelancer.com, PeoplePerHour, and other platforms for web dev/landing page jobs
   - Include: job title, description, budget, link
   - Save results to `agents/freelance_finder/data/`

7. **Generate PPT + Send Email:**
   ```bash
   python3 agents/morning_briefing.py
   ```
   Or build the data in Python and call the report/emailer directly.

8. **Set the day:** Ask Howard what he wants to focus on today and help him pick 1-3 concrete tasks.

## Output Format

Keep it short. Use this structure:

```
**Daily habits:** [checklist]
**Top priorities today:** [2-3 bullets]
**New songs this week:** [list with YouTube links]
**Freelance leads:** [list with links]
**What do you want to tackle today?**
```

## Email

After presenting the briefing, generate a PPT report and email it to Howard with both sections (New Songs, Freelance Leads).

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

4. **Run the full morning briefing** (searches + email):
   ```bash
   python3 agents/morning_briefing.py
   ```
   This runs all 3 agents (new songs, AI trends, freelance leads) and emails results to Howard.

   Or run individually:
   ```bash
   python3 agents/youtube_research/research.py --new-songs --max 10
   python3 agents/youtube_research/research.py "AI automation" --max 5 --new-only
   python3 agents/freelance_finder/finder.py --max 5
   ```

5. **Set the day:** Ask Howard what he wants to focus on today and help him pick 1-3 concrete tasks.

## Output Format

Keep it short. Use this structure:

```
**Daily habits:** [checklist]
**Top priorities today:** [2-3 bullets]
**Open items:** [anything pending]
**What do you want to tackle today?**
```

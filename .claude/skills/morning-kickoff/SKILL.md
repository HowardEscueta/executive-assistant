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

4. **YouTube research:** Run both searches:
   ```bash
   # New songs -- Howard recreates these with lyrics content
   python3 agents/youtube-research/research.py "new music 2026" --max 5 --new-only
   python3 agents/youtube-research/research.py "new song released this week" --max 5 --new-only
   # AI automation trends
   python3 agents/youtube-research/research.py "AI automation" --max 5 --new-only
   ```
   Also check for freelance leads:
   ```bash
   python3 agents/freelance-finder/finder.py --max 3
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

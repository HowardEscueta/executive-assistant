# Research Skill

Deep research on any topic, tailored to Howard's business context. More than a couple of web searches — this is multi-source, synthesized, actionable intel.

## When to use

When Howard asks to "research X", "look into X", "what's the deal with X", or wants to understand something deeply before making a decision. Also use when he's evaluating a tool, platform, niche, or opportunity.

## How it works

This skill reads Howard's context first, then does deep research using WebSearch + WebFetch across multiple sources, then synthesizes findings into a short, actionable brief.

## Steps

1. **Load context** — Read these files silently before researching:
   - `context/me.md` — who Howard is and what he's building
   - `context/current-priorities.md` — what he's focused on right now
   - `context/work.md` — his revenue streams and tools
   - `context/goals.md` — his quarterly and long-term targets
   - Any relevant project README in `projects/` if the topic overlaps

2. **Clarify the research goal** (if the topic is vague) — Ask one focused question before starting: "What do you want to do with this information?" Skip this if intent is clear.

3. **Plan the research** — Before searching, identify:
   - What is the core question?
   - What angles matter for Howard specifically (freelancing? clip automation? content creation?)
   - What sources are most credible for this topic?

4. **Deep research** — Do at least 5-8 distinct searches across multiple angles:
   - General overview (what is it, how does it work)
   - Current state / recent developments (use current year in queries)
   - Opportunities and risks specifically for Howard's situation
   - How others in similar positions have used it (case studies, Reddit, forums)
   - Pricing, tools, platforms, or technical requirements if relevant
   - Filipino / Southeast Asian angle if it matters

   Use WebFetch to go deeper on promising pages — don't just skim headlines.

5. **Synthesize** — Don't just dump search results. Write a brief that answers:
   - What is this, in plain terms?
   - Why does it matter for Howard specifically?
   - What's the opportunity or risk?
   - What should he do next (if anything)?

6. **Save the report** — Save to `research/YYYY-MM-DD_topic.md` (create the folder if it doesn't exist). Format: title, date, summary, key findings, next steps.

## Output Format

```
## Research: [Topic]
*Date: YYYY-MM-DD*

### TL;DR
[2-3 sentences. What this is and why it matters for Howard.]

### Key Findings
- [Finding 1 — specific, not generic]
- [Finding 2]
- [Finding 3]
- ...

### Relevant to Howard
[1-2 paragraphs connecting findings to his current work: freelancing, clip automation, content, goals.]

### Next Steps
- [ ] [Specific action he can take today or this week]
- [ ] [Another action]

### Sources
- [Source title](URL)
- ...
```

## Notes

- If PERPLEXITY_API_KEY is set in .env, you can optionally use it via the Perplexity API for deeper research. Check `.env` and mention it to Howard if available.
- Keep it tight. Howard is 16 and moving fast — 500 words max unless he asks for more.
- Always tie findings back to his North Star: hit 1M PHP before 18.
- Don't hedge everything. Give a clear take.

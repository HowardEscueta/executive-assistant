# Decision Log

Append-only. When a meaningful decision is made, log it here.

Format: [YYYY-MM-DD] DECISION: ... | REASONING: ... | CONTEXT: ...

---

[2026-04-02] DECISION: Published executive-assistant repo to GitHub (public) | REASONING: Howard wants to polish it and make it accessible | CONTEXT: github.com/HowardEscueta/executive-assistant

[2026-04-02] DECISION: Published BookMe to GitHub + deployed on Vercel | REASONING: First product to go live, needs to be publicly accessible | CONTEXT: github.com/HowardEscueta/bookme, live at bookme-ochre.vercel.app

[2026-04-02] DECISION: Used Neon free tier PostgreSQL (Singapore region) for BookMe production DB | REASONING: Free, closest region to Philippines, works with Prisma out of the box | CONTEXT: Postgres 17, ap-southeast-1

[2026-04-02] DECISION: Set up separate SSH key for HowardEscueta GitHub account | REASONING: Already had SSH key for rodeloescueta account, needed separate key | CONTEXT: ~/.ssh/id_howardescueta, host alias github-howard in ~/.ssh/config

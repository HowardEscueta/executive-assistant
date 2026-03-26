# Client Project Kickoff

Run this when Howard lands a new client or starts a new web dev project.

## Input Needed

Ask Howard for:
- Client name
- What they want built (one-liner)
- Budget (if known)
- Deadline (if known)
- Any specific requirements or preferences

## Steps

1. **Create project folder:** `projects/[client-name]/`

2. **Create README.md** in the project folder:
   ```markdown
   # [Client Name] - [Project Name]

   **Description:** [what they want]
   **Status:** Active
   **Budget:** [amount or TBD]
   **Deadline:** [date or TBD]
   **Started:** [today's date]

   ## Requirements
   - [list from intake]

   ## Tasks
   - [ ] [break down the work into steps]

   ## Notes
   - [anything else relevant]
   ```

3. **Create task breakdown:** Break the project into concrete steps Howard can work through.

4. **Log the decision:** Add an entry to `decisions/log.md`:
   ```
   [YYYY-MM-DD] DECISION: Took on [client] project | REASONING: [why] | CONTEXT: [budget, timeline]
   ```

5. **Update priorities:** If this is a big project, consider updating `context/current-priorities.md`.

## Output

Show Howard the project README and task list for review before finalizing.

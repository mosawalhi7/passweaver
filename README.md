# PassWeaver (pwv)

PassWeaver (`pwv`) is a focused command-line tool that generates personalized password wordlists from user-provided strings, dates, and numbers. It reads generation rules from `rules.txt`, applies case/leet/symbol variations, and writes candidate passwords to files under `data/output/`.

> Many people include personal information (names, birthdays, pet names, etc.) in their passwords. PassWeaver helps create focused wordlists for **authorized** security testing and account recovery — use responsibly and with permission.

---

## Key features

- Interactive, colorized CLI with simple prompts.  
- Generates targeted combinations from provided strings, dates, and numbers.  
- Reads generation rules from `rules.txt` (rules-driven behavior).  
- Prioritizes likely/realistic variants (common capitalization, substitutions, and placements).  
- Memory-efficient streaming output — suitable for large lists.  
- Real-time progress feedback while generating.  
- Filters: minimum/maximum length, require uppercase, require symbol.  
- Save and resume generation sessions.  
- Outputs saved under `data/output/`.  
- Pure Python — no external dependencies.

---

## Quick start

```bash
git clone https://github.com/mosawalhi7/passweaver.git
cd passweaver
python pwv.py
```

Follow the interactive prompts:

1. Enter one or more **strings** (space-separated) — **required**.  
2. Optionally enter **dates** (`D/M/YYYY`) and **numbers**.  
3. Configure minimum/maximum length and requirement flags.  
4. Choose whether to save the session (optional) or run ephemeral.  
5. Generated passwords are written to `data/output/`.

---

## File locations

- **Rules file:** `rules.txt` — defines how combinations are produced (one rule per non-empty line).  
- **Sessions:** `data/sessions.json` — saved session metadata for resuming runs.  
- **Outputs:** `data/output/` — generated password lists (auto-named unless you provide a filename).

---

## Use cases

- Authorized security assessments and penetration tests to evaluate password policy effectiveness.  
- Account recovery scenarios where targeted candidate lists are needed.  
- Personal audits or training demonstrations to highlight weak password patterns.

---

## Best practices

- Provide comprehensive personal strings (name variants, nicknames) and relevant dates for targeted results.  
- Use filters (min/max length, uppercase/symbol requirements) to reduce noise and focus on likely candidates.  
- Avoid excessive leet/symbol expansion unless needed — it multiplies combinations quickly.  
- Ensure you have permission before using wordlists against accounts or systems.

---

## Notes & limitations

- The tool is designed to model common human password patterns; it is **not** a brute-force generator.  
- Generation can produce very large outputs; monitor disk space and limit totals as needed.  
- The rules are read from `rules.txt` in the repository root — editing that file changes generation behavior.

---

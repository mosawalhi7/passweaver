# PassWeaver (pwv)

PassWeaver (`pwv`) is a command-line tool that generates personalized password wordlists using a target's personal strings (names, nicknames, places), dates, and numbers.  
It creates rule-based combinations and leet/case variations to help build targeted wordlists for authorized security testing, password recovery, or research.

---

## Features

- Clear, colorized interactive CLI
- **Strings are mandatory** — provide one or more target strings (space-separated)
- Dates and numbers are optional
- Rule-driven generation (`rules.txt`) with leet and case variations
- Resume previous sessions and continue generation anytime
- Password filtering by length, uppercase presence, and symbols
- Outputs saved under `data/output/`
- No external dependencies (pure Python)

---

## Quick start

```bash
git clone https://github.com/mosawalhi7/passweaver.git
cd passweaver
python pwv.py

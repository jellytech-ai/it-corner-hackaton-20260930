# JellyTech

Team 9: Wojtek, Rafał, Walerian. Final delivery: tag `v1.1`, 7 vans, 85750 PLN over five years.

## 1. Workflow

- **Read before building.** 10:10–11:10: profiled the five files, found the data traps (222 duplicate rows, P-17/P-17B, a negative odometer reading, GPS gaps) and wrote one handoff document with every assumption, its time and its status.
- **Asked five questions, each with a fallback.** We dropped two questions we could answer from the data (P-17, fridge vans); Ewa later confirmed both.
- **Specified before coding.** A contract (who owns which file, function signatures, table columns), a parameter file (`params.csv`) and fixture files in the agreed format, so three tracks could start at 11:20 without waiting for each other.
- **Three parallel tracks:** data cleaning and check figures; feasibility, ranking and export; economics and documents. Merged to one branch at agreed times, tests run on every push.
- **Two requirement changes absorbed as parameter and data changes.** Ewa's noon rules (3 → 8 vans) and her 15:18 change (new export, new register, worst-day rule: 8 → 7 vans, plus `impact.csv`). The second took about 15 minutes from her message to our post in the thread.
- **Verified twice.** Check figures recomputed with `sort`/`awk`; the noon shortlist recomputed independently in a second session; both matched to the zloty.
- **Released like software.** PR to `main`, tag, zip built from the tag and rerun in an empty folder, then posted with the CSVs, the board note, the assumptions and the rerun instructions.

## 2. Humans and agents

- **Wojtek:** data track, the contract and shared conventions, questions and replies to Ewa, releases. **Rafał:** feasibility, ranking, export, integration, the slide builder. **Walerian:** economics, board note, assumptions list, rerun instructions.
- **Each person ran several agent sessions** (Claude Code), one per track in its own git worktree, plus one session that only watched the organisers' repository and discussions and relayed Ewa's answers.
- **Agents did:** data profiling, code and tests, reading Ewa's answers at the source, cross-checks, releases, documents, slides.
- **People decided:** what Ewa's problem is, which questions to ask, every merge to the shared branch, every message to Ewa, and the business calls (list only vans that pay back; after the freeze, add a caveat rather than change the formula).
- **Where the time went:** mostly reviewing agent output and deciding, then prompting; very little typing code. The scarce resource was human attention for review, not implementation speed.
- **One honest exception:** at 15:18, under time pressure, the agent chose two rules itself (GPS for an impossible 1383 km odometer reading; how to scale the two new vans to a year). It wrote both into the assumptions and flagged them instead of hiding them.

## 3. Tools and technologies

- **Agent and model:** Claude Code in the terminal (Claude Opus); sessions message each other and keep handoff notes.
- **Isolation:** one git worktree per track (Orca). **Editor:** Cursor for reading and small manual fixes.
- **Repository and CI:** GitHub, track branches → `devel` → `main` by merge only; GitHub Actions on Python 3.9 and 3.13.
- **The tool for Ewa:** Python, standard library only, `unittest` (104 tests); no install for her analyst, all numbers in `params.csv`.
- **Independent check:** shell (`sort -u`, `awk` with `LC_ALL=C`).
- **Client channel:** GitHub Discussions. **Slides:** a Python script (reportlab) that builds the PDF.

## 4. Where our usual way of working didn't fit

- **Second-person review.** Normally a second person approves every PR. Today both releases were approved by one person; the agents produced changes faster than three people could review them.
- **Requirements sign-off.** Normally we agree the requirements before coding. Today the client answered twice a day and changed the rules twice, so we coded against our own written assumptions and treated every answer as a parameter change.
- **One owner per task.** Normally one developer carries a task end to end. With several agents per person, outputs collided (mixed languages in messages, columns added outside the contract, `.pyc` files committed) until we wrote the contract and a shared "constitution".
- **Hand-written logs.** We are used to trusting a log. An agent wrote times from its own estimate rather than the clock, and we had to correct them from the commit history.
- **Acceptance by outsiders.** Normally someone who did not write the code accepts it. Today the rerun test was done by people and agents who knew it.

## 5. What we'll do differently

- **As a team, from now on:** specification first on agent-assisted work. Contract, parameter file, fixtures, CI and a deliberately broken sample export exist before the first line of code. Our assumption "the next export has the same columns" failed on the first new file; the tool caught it only because it was built to stop and name the column.
- **In today's work:** ask first about what changes the result most (the range rule, the grant). Ewa's noon answer changed the shortlist from 3 to 8 vans.

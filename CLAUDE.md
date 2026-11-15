# CLAUDE.md — instantrag-poc

Proof of concept for Roland Kummer's bachelor thesis (HS Offenburg x t2b AG, company supervisor
Luca Strozzi): streamed tool-call interception ("Instant RAG") using arithmetic proxy tools
`<ADD .../>` and `<MUL .../>`. Repository owner: Luca Strozzi (GitHub `lstrozzi/instantrag-poc`).

## Read first
- `doc/poc-sprint-plan.md` — single source of truth for the current PoC sprint: decisions, open
  decisions, notebook spec, implementation steps, status log. Read it at the start of every
  session before proposing any work.
- `doc/instantrag.md` — Luca's documentation of the harness and the recorded reference runs.

## Layout
- `src/instantrag_qwen_demo.py` — reference harness (phases -1/-2/-3), Luca's instrument
- `src/llm_request.py` — config and API-key helpers
- `config/instantrag.txt` — system prompt S0 (known inconsistencies, see plan §4)
- `config/llm_config.json` — endpoint and default model
- `.env` — `LLM_API_KEY` (secret)

## Rules
1. One approved step per session (plan §10). Before editing anything, present a short plan
   (files, changes, tests) and wait for Roland's explicit approval ("Freigabe").
2. Keep changes small and testable. No unrequested refactors, abstractions or architecture changes.
3. Do not modify Luca's reference files without explicit approval: `src/instantrag_qwen_demo.py`,
   `src/llm_request.py`, `config/instantrag.txt`, `config/llm_config.json`, `doc/instantrag.md`.
   Extend from outside instead (e.g. wrap `run_turn` from the notebook).
4. No requests to the LLM endpoint (`llm.thalabus.ai`) unless Roland approves that specific run.
   Offline tests with mocked streams are fine.
5. Secrets: never print, log or commit the API key. `load_model()` stores it in
   `model_cfg["token"]`, so never display `model_cfg`; never print `.env`; never log request headers.
6. Experiment data is append-only (`results/runs.jsonl`): never delete, overwrite or filter out
   failed runs. Log infrastructure errors and report them separately.
7. In reports, separate: facts from code / results of tests actually run / hypotheses /
   open questions / recommendations. Never claim something was tested without evidence;
   never invent results.
8. No new dependencies without approval.
9. No git commit or push without approval; pushes go to Luca's repository.

## End of every step
- Append a dated entry to `doc/poc-sprint-plan.md` §13 (status log): what changed, how it was
  tested and with what result, open issues, proposed next step.
- Propose a commit message; commit only after approval.
- Commit message format (Roland's standard): compact and structured. One imperative subject line
  (max. ~60 chars), blank line, 2–5 short bullets (`- area: what changed`). No long prose.
- Scientific or design questions: add them to plan §3 and ask. Roland decides; the scientific
  discussion happens in his Claude Desktop project.

## Environment
- Windows, VS Code, Anaconda. Python environment: conda env `instantrag` (Python 3.11).
  Claude Code is started from an Anaconda Prompt after `conda activate instantrag`, so `python`
  is the env interpreter (check: `python -c "import sys; print(sys.executable)"` ends in
  `envs\instantrag\python.exe`). Notebook kernel: `instantrag`. Do not create a venv.
- Live harness run (makes LLM requests, approval needed):
  `python src\instantrag_qwen_demo.py -3 --model qwen-3.5-35b`
  Exit code is 0 even when the protocol fails; it is not a success signal.

## Language
- Answer in the user's language (Roland: German, informal "Du"). Code, comments and commit
  messages in English.

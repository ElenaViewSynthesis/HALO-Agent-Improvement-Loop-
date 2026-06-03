 # HALO Agent Improvement Loop — Demo

 HALO stands for Hierarchical Agent Loop Optimizer.
 This repository contains a minimal, runnable demonstration of an "agent improvement loop":
 traces → human & model feedback → generated evals → Promptfoo gate → HALO optimization → Codex handoff.

 ## Features

 - Materializes a synthetic dataroom with structured and narrative files.
 - Writes local runtime validation tools (`data/tools/*`).
 - Generates per-trace artifacts (summary, memo, risk register, citations, evidence table).
 - Produces mock human and LLM feedback and auto-generated Promptfoo evals (demo/fake results).
 - Writes a HALO-style optimization context and a `codex_handoff.md` implementer handoff.

 ## Quickstart (offline demo)

 1. Create and activate a Python virtual environment.

    Windows (PowerShell):
    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```

    macOS / Linux:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

 2. Run the offline demo (no external APIs required):

 ```powershell
 python run_loop.py demo
 ```

 3. Inspect generated artifacts under:

 `examples/agents_sdk/agent_improvement_loop_artifacts/`

 ## Live mode (optional)

 - A real live run uses the OpenAI SDK. To enable it install `openai` and set `OPENAI_API_KEY`.
 - Dry-run: `python run_loop.py live` (generates artifacts without calling models).
 - Live run (calls models):

 ```powershell
 $env:OPENAI_API_KEY="sk-..."; python run_loop.py live --run
 ```

 Notes:
 - The demo provides a deterministic, reviewable pipeline. A full production flow requires model credentials and may need Node.js / `promptfoo` if you wish to run real Promptfoo evaluations.

 ## Key files

 - `run_loop.py` — CLI driver with `demo` and `live` flows.
 - `agent_improvement_loop/data/workspace_files.py` — synthetic dataroom sources.
 - `agent_improvement_loop/tools.py` — local validation tool templates.
 - `requirements.txt` — declared dependencies for live runs.

## Use case — Financial analyst agents

This workflow can be adapted to improve financial analyst agents (research, reporting, and compliance).

- Data: populate the synthetic dataroom with financial statements, ledgers, filings, earnings-call transcripts, and market snapshots.
- Validators: add runtime checks to reconcile balances, verify numeric calculations, and confirm evidence coverage for investment claims.
- Evals: use Promptfoo-style tests to require supporting citations, correct computations, conservative risk disclosures, and regulatory wording.
- HALO optimization: tune prompt templates, evidence retrieval scoring, and aggregation strategies to maximize factuality and auditability.
- Handoff: `codex_handoff.md` should include reproducible data-extraction scripts, analyst notebooks, and QA checklists for engineers and auditors.

Security & compliance: when running on real financial data, enforce strict access controls, encryption, data retention policies, PII redaction, and human approvals before publishing.

## Development

 - Show help: `python run_loop.py --help`
 - Run the demo: `python run_loop.py demo`
 - Run live (dry-run): `python run_loop.py live`
 - Run live (actual model calls): `python run_loop.py live --run` (requires `OPENAI_API_KEY`).

 If you want, I can run a live dry-run now or perform a real live run using the current environment.

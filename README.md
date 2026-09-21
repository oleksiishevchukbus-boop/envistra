# ENVISTRA

**Комп'ютерна програма «ENVISTRA — агентно-орієнтована система імітаційного
моделювання поведінкових стратегій підприємств в умовах зеленого переходу
та екологічних обмежень»**

*ENVISTRA (ENVIronmental STRAtegy) — Agent-Based Simulation of Enterprise
Behavioural Strategies under Green Transition and Environmental Constraints*

Version 1.0 · © 2026 Oleksii Shevchuk. All rights reserved.

---

## Name

**ENVI**ronmental + **STRA**tegy
«ENVI» від *environmental* (екологічний), «STRA» від *strategy* (стратегія).

ENVISTRA is a portmanteau, not a strict acronym — there is no letter-by-letter decoding.

## Overview

ENVISTRA (ENVIronmental STRAtegy) — agent-based simulation of how enterprises adapt
their behavioural strategies to green regulatory constraints: efficiency investment,
expense adaptation and emission-quota compliance under a configurable policy regime.
Mesa core, ML pollution forecasting, FastAPI + React UI.

The model is configuration-driven and sector-agnostic. Historical data from electricity
generation (hydro, solar, petroleum and other sources, 2010–2019) is used for calibration
and validation only; it does not restrict the scope of the model.

## Running it

```bash
python run_web.py
```

Starts the API and the web interface together and opens
[http://localhost:5173](http://localhost:5173). Ctrl+C stops both. Pass
`--api-port` / `--ui-port` to move them, `--no-browser` to stay put, or
`--no-reload` to stop the API restarting on file changes.

If something is missing — the package, node modules, the data workbooks, a port
already taken — it says so before starting rather than failing halfway.

### First-time setup

```bash
pip install -e ".[web]"
cd web/frontend && npm install
```

Then place the source workbooks under `data/`. They are **not committed** — see
[data/README.md](data/README.md) for the schema and why.

### Running the two parts separately

```bash
python -m uvicorn web.backend.main:app --reload --port 8000   # API, from the repo root
cd web/frontend && npm run dev                                 # interface
```

The interface proxies to the API, so the API must be on the port the proxy
expects (8000 by default).

### Using the model directly

```python
from envistra.bootstrap import initialize_model

model, reader, companies, calculators = initialize_model(seed=42)
for _ in range(20):
    model.step()
history = model.datacollector.get_agent_vars_dataframe()
```

A run repeats exactly only when given a `seed`.

## Configuration

Everything lives in JSON under `config/`, which is the only source of truth:

| Path | What |
|---|---|
| `config/environment.json` | The regulatory regime — quota allocation, penalties, revenue and pollution |
| `config/strategies/<id>.json` | One behavioural strategy each; any number of them |
| `config/companies/<id>.json` | One agent each — the file count is the agent count |
| `config/simulation.json` | Plot output settings |

All of it is editable from the web interface.

## Status

**Port in progress.** The model, its configuration and the full web stack are in
place; the two command-line runners are not yet transferred.

## Licence

All rights reserved. See [LICENSE](LICENSE).

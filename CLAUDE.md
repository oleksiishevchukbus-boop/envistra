# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project Overview

**ENVISTRA** — an agent-based model of enterprise behavioural strategies under green
transition and environmental constraints. Enterprises decide how to split investment
between financial and ecological efficiency, adapt operating expenses, forecast their
own pollution, and comply with an emission-quota regime that includes allocation,
a trading market and tiered penalties.

**Framework:** Mesa (Python agent-based modelling)
**Language:** Python 3.10+ (backend & model), JavaScript/JSX (Web UI)
**Domain:** Environmental economics, green-transition policy

The model is configuration-driven and sector-agnostic. Electricity-generation data
(2010–2019) is used for calibration and validation only.

---

## Port status

This repository is being assembled **component by component** from an earlier
implementation at `E:\PHD\application\green-projects-abm`. The architecture below
describes the finished target; not all of it exists yet.

**Landed so far:** repository foundation; `data/` (workbooks untracked — see
`data/README.md`); `src/` — the model core; `config/` — file-driven JSON;
`utilities/` — data reader, plots, run metadata, plus `bootstrap.py`;
`web/backend/` — the REST + WebSocket API; `web/frontend/` — the React UI.

**Only the two CLI runners remain** (`run_main.py`, `run_strategy_comparison.py`).
Everything else is transferred and the whole stack runs.

**The model runs.** `initialize_model()` builds 15 agents from the company files and the
workbooks, steps, and produces a history DataFrame; the plot suite and `run_config.json`
work. What is missing is the CLI runners and `web/`.

```python
from envistra.bootstrap import initialize_model
model, reader, companies, calculators = initialize_model(seed=42)
for _ in range(20):
    model.step()
history = model.datacollector.get_agent_vars_dataframe()
```

When a part is transferred, update the two lines above.

> **Results diverge from the predecessor project from the `src/` transfer onward.**
> A live bug in the `economically_efficient` quota-buy path destroyed quota instead of
> returning it to the market; fixing it changes the numbers for the Business and
> RevenueByQuotaSale strategies. Output is no longer comparable with green-projects-abm.

---

## Port conventions

These are standing decisions. Apply them to every component transferred.

### Layout — src-layout package

| Source (`green-projects-abm`) | Target (`envistra`) |
|---|---|
| `config/*.py`, `config/Agent/`, `config/Environment/`, `config/Strategies/` | `src/envistra/config/` (lowercase sub-packages) |
| `config/Strategies/Strategies.py` | **deleted** → `config/strategies/*.json` |
| `config/Agent/CampaignAgentConfig.py` | **deleted** → `config/companies/*.json` |
| `config/environment.json`, `config/strategies.json` | `config/` at the repo root — runtime data |
| `src/CampaignAgentModel.py` | `src/envistra/model.py` |
| `src/Agent/` | `src/envistra/agent/` |
| `src/Agent/Estimators/`, `src/Agent/Calculators/` | `src/envistra/agent/estimators/`, `…/calculators/` |
| `src/Environment/` | `src/envistra/environment/` |
| `src/Environment/Calculators/` | `src/envistra/environment/calculators/` |
| `utilities/` | `src/envistra/utilities/` |
| `run_main.py`, `run_strategy_comparison.py` | repo root |
| `web/`, `data/` | unchanged |

The source had **no packaging at all** — `config/`, `src/` and `utilities/` were bare
directories that imported only because the CWD happened to be the repo root. Here they
are a real package: imports are absolute, `from envistra.config.Enums import …`.

**Package directories are lowercase** (`agent/`, `environment/`, `config/`,
`estimators/`, `calculators/`); **module files stay PascalCase** (`CompanyAgent.py`,
`QuotaToBuyPriceCalculator.py`). Relative imports are used within a sub-package
(`from .estimators import AgentEstimators`) and absolute ones across packages.

Because the Python config and the JSON config now live in different trees,
**`ConfigLoader.PROJECT_ROOT` must be recomputed** — the module sits two levels deeper
inside `src/` than it used to.

### Naming

The source used `Campaign` throughout where it meant `Company`, and carried several
spelling errors. Both are corrected on transfer. The existing style — PascalCase methods,
camelCase attributes — is **kept**, so the diff stays reviewable.

Apply:

| Source | Target |
|---|---|
| `CampaignAgent` | `CompanyAgent` |
| `CampaignEntity` | `CompanyEntity` |
| `CampaignAgentModel` | `CompanyAgentModel` |
| `CampaignAgentUtilities` | `CompanyAgentUtilities` |
| `CampaignAgentConfig` / `…Entity` / `…s` | `CompanyAgentConfig` / `…Entity` / `…s` |
| `CampaignAgentFields` | `CompanyAgentFields` |
| `campaignEntities`, `campaignReports` | `companyEntities`, `companyReports` |
| `InitCampaignReportDict` | `InitCompanyReportDict` |
| `ImplementInvestmets` | `ImplementInvestments` |
| `__ApplyQuotaPurchaseTrasactions` | `__ApplyQuotaPurchaseTransactions` |
| `GetRevenueToExpensesDestributionParams` | `GetRevenueToExpensesDistributionParams` |
| `__GenneralApproach` | `__GeneralApproach` |
| `startindData` | `startingData` |

**Do NOT rename** — these are shared vocabulary across Python, JSON and the React
dropdowns; renaming in one place silently breaks the others:

- approach strings (`industry_based`, `gap_full_cover`, `MLP_based`, `reserve_based`, …)
- `GreenStrategy` and the `"Green"` display name — a model concept (0 % financial /
  100 % ecological investment), not branding
- the **string values** of `CompanyAgentFields` — they are DataCollector keys and
  DataFrame column names
- JSON keys, and the `name_to_attr` map in `ConfigLoader`

### Identity

The brand must not contain the word "green"; it dates fastest in policy discourse while
the code outlives it. "Green" survives only in prose, in the GitHub description, in the
topics list, and in the `GreenStrategy` model concept.

Every occurrence of `"Green Projects ABM"` in a transferred file becomes ENVISTRA. Known
touchpoints, to handle as their files arrive: `config/__init__.py`, `web/backend/main.py`
(FastAPI title, description, root payload), `web/frontend/index.html`, both
`package.json` files, `Layout.jsx` (nav brand), `About.jsx`, `requirements-web.txt`,
and the `ConfigSerializer` output header.

Program names are defined once in `src/envistra/__init__.py` (`FULL_NAME_UK`,
`SHORT_NAME`, `FULL_NAME_EN`). **Import them — never re-type them.** They must stay
character-identical to the назва in the заява and on the титульний аркуш of the deposited
source listing; see `E:\PHD\application\ENVISTRA-naming-and-registration.md`.

### Configuration is file-driven

`config/` at the repository root is the source of truth. There are **no Python default
literals** — the predecessor kept three copies of "the defaults" which had already drifted
apart (`competition_influence` was 0.2, 0.2 and 0.1 in three places), and a missing key
silently took whichever copy the code path reached.

The environment classes enforce this rather than merely documenting it: they declare no
attributes at all, and a metaclass turns any read before `load_environment()` into a
`ConfigNotLoadedError` naming the setting and saying what to call. So forgetting to load
config fails immediately instead of running the model on stale numbers. `EnvironmentConfig`
holds the classes themselves, not instances, so every read goes through that check.

```
config/environment.json        the regulatory regime
config/strategies/<id>.json    one per strategy; id is the filename stem
config/companies/<id>.json     one per agent — the file count IS the agent count
```

A company names its strategy by id and adds its four personal parameters:

```json
{ "name": "AES CORP Business", "dataSource": "AES CORP", "strategy": "business",
  "parameters": { "finEffCoef": 1.0, "ecoEffCoef": 1.4,
                  "finEffInvest": 1.0, "ecoEffInvest": 1.0 } }
```

`name` is the agent label (DataCollector `Name`, plot legends, results folders).
`dataSource` is a workbook's filename without `.xlsx`. A workbook's identity is its path,
`data/<industry>/<dataSource>.xlsx` — the top-level folder is the industry, and the `Name`
and `Industry` columns inside are overwritten on read. Several companies may share one, as
the four AES CORP variants do. This one file replaces both hardcoded structures the
predecessor used — `GlobalConfig.AgentList` and `CampaignAgentConfigDict` — so the
unguarded `KeyError` when a name appeared in one but not the other is gone by construction.

`envistra.config.Loader` owns discovery, validation and construction:

- `load_environment()` applies to the `EnvironmentConfig` classes in place — the model
  reads those module-level singletons live on every step, so that contract is fixed.
- `load_strategies()` returns `{id: StrategyEntity}`. **Any number of strategies works.**
  The predecessor mapped strategies onto four fixed class attributes through a hardcoded
  name table, so a fifth was written to disk, shown in the UI, and silently dropped before
  it could ever run.
- `load_companies()` discovers `config/companies/*.json` in filename order.
- `verify_data_links()` is called by the data reader once workbooks are loaded — not at
  parse time, because `data/*.xlsx` is untracked and may be absent.

**Validation runs on the load path** (it ran nowhere in the predecessor). Unknown keys are
an error with a spelling suggestion, missing required keys name the field, `approach`
values are checked against the **implemented** sets only, and a dangling strategy
reference lists the available ids. Two pairs are shares of one whole and must each sum to
exactly 1, every share within [0, 1]: `finInvestment` + `ecoInvestment`, and
`featuresImpact.netRevenue` + `featuresImpact.quotaExceedance`. The strategy form
enforces the same rule by setting the other share of a pair whenever one is edited. Adding a parameter means editing the config class and
`Loader`; there is no separate serializer to keep in sync.

### Transfer order

Derived from the import graph; each tier depends only on earlier ones.

```
DONE    config layer, model core, DataReader, PlotBuilder, ConfigSerializer,
        bootstrap.initialize_model
NEXT    run_main.py and run_strategy_comparison.py — they reuse PlotSuite
```

---

## Architecture

### Execution flow (each step)

Driven by `CompanyAgentModel.step()` in `src/envistra/model.py`:

1. `EstimateExpenses()` — agents project operating costs
2. `EstimateInvestments()` — split investment between financial and ecological efficiency
3. `EstimatePollution()` — forecast pollution (MLP or ratio-based)
4. `SendExpensesReport()` — report to the QuotaManager
5. `CalculateQuotas()` — manager allocates quotas by industry / expenses
6. `ReceiveQuota()` — agents receive their allocation
7. `SellQuota()` — agents offer surplus quota to the market
8. `SortMarketLotDict()` — sort market offers by price
9. `BuyQuota()` (shuffled order) — agents purchase the quota they need
10. `ReEstimateExpenses()` — agents adapt expenses to close the remaining gap
11. `ProduceRevenue()` — realised revenue
12. `ProducePollution()` — realised pollution
13. `PayQuotaExceedancePenalty()` — tiered penalties on exceedance
14. `ImplementInvestments()` — apply efficiency improvements
15. `ImplementOperations()` — update assets and net revenue
16. `ApplyLinearReductionFactor()` — tighten the quota cap (climate policy)

> The model dispatches these phases by **string literal**
> (`self.agents.do("EstimateExpenses")`). Renaming a phase method without updating its
> string fails at *runtime*, not at import, and only for that phase — so the run continues
> with one stage silently skipped. Change both together.

> The source's CLAUDE.md claimed `ReEstimateExpenses()` was commented out. **It is
> active.** Only a trailing second `datacollector.collect` call is commented out.

### Components

**Config layer (`src/envistra/config/`)**
- `GlobalConfig.py` — money/efficiency multipliers, agent list, starting year
- `Enums.py` — `CompanyAgentFields`, the canonical field names used as DataCollector
  keys and DataFrame columns. This is the model's real schema.
- `ConfigHelpers.py` — `require_kwarg()` / `optional_kwarg()`
- `Strategies/Strategies.py` — the four strategies
- `Agent/CompanyAgentConfig.py` — maps agent names to strategies and coefficients
- `Agent/Estimators/`, `Agent/Calculators/` — config class per behaviour module
- `Environment/EnvironmentConfig.py` — QuotaManager, Revenue and Pollution calculator
  configs, including the penalty tiers

**Core simulation**
- `model.py` — the Mesa `Model`; owns the QuotaManager, QuotaMarket and environment
  calculators. No grid or space: the "environment" is the quota regime. Uses the Mesa 3
  `AgentSet` API (`agents.do(...)`, `agents.shuffle_do(...)`), not a classic scheduler.
- `agent/CompanyAgent.py` — the per-step agent behaviour listed above
- `agent/CompanyEntity.py` — validated data container built from historical data
- `agent/estimators/` — Expenses, Investment, Pollution (MLP), ExpensesRe-estimation
- `agent/calculators/` — quota buy/sell amount and price
- `environment/QuotaManager.py` — allocation, penalties, cap tightening
- `environment/QuotaMarket.py` — the lot book
- `environment/calculators/` — Revenue, Pollution

**Utilities (`src/envistra/utilities/`)**
- `DataReader.py` — loads Excel data, applies scaling, builds `CompanyEntity` objects
- `PlotBuilder.py` — plotting; writes a timestamped subfolder under `results/`
- `ConfigLoader.py` — reloads the JSON configs; **JSON is the source of truth, the
  Python literals are fallback defaults**
- `EnvironmentSerializer.py`, `StrategySerializer.py` — JSON ↔ config-class mapping
- `ConfigSerializer.py` — writes `run_config.json` for reproducibility

**Web UI (`web/`)** — FastAPI backend (`/api` prefix, WebSocket progress channel) and a
React 18 + Vite + Tailwind SPA. The frontend is **plain JSX, not TypeScript**.

**Data (`data/`)** — Excel files by generation type, 15 company slots, 2010–2019.
Fields: `TotalAssets`, `COGS`, `TotalOperatingExpenses`, `Revenue`, `Pollution`.

### Strategies

| Strategy | Fin/Eco split | Pollution estimator | Buy-price approach | Quota reserve |
|---|---|---|---|---|
| Ignorance | 100 % / 0 % | general | ignorance | 0 % |
| Business | 70 % / 30 % | MLP_based | economically_efficient | 2 % |
| Green | 0 % / 100 % | MLP_based | gap_full_cover | 10 % |
| Revenue by Quota | 20 % / 80 % | MLP_based | economically_efficient | 2 % |

To add one: create a `StrategyEntity` in `config/Strategies/Strategies.py`, then assign
it to agents in `config/Agent/CompanyAgentConfig.py`. Note the display name of the fourth
strategy is `"Revenue by Quota"` while its attribute is `RevenueByQuotaSaleStrategy` —
the mapping lives in the `name_to_attr` dict in `ConfigLoader`.

### Approaches actually implemented

Every estimator and calculator takes an `approach` string and dispatches on it with
`match`/`case`. The source's documentation over-promised here; this list is what exists:

| Module | Implemented |
|---|---|
| ExpensesEstimator | `general`, `performance_based`, `performance_based_relative` |
| InvestmentEstimator | `revenue_based`, `performance_based` |
| PollutionEstimator | `general`, `MLP_based` |
| ExpensesReEstimation | `none`, `gap_proportional` |
| QuotaToBuyAmount | `reserve_based` |
| QuotaToBuyPrice | `ignorance`, `economically_efficient`, `gap_full_cover` |
| QuotaToSellAmount | `reserve_based` |
| QuotaToSellPrice | `general`, `history_based` |

> The source's CLAUDE.md listed 7 investment approaches and 5 re-estimation approaches.
> Only the ones above are implemented; the rest were documented but never written.

### Data scaling

Money is scaled by `MoneyValueMultiplier = 10e-9`, efficiency by
`EfficiencyValueMultiplier = 8e-3`, both in `config/GlobalConfig.py`.

---

## Fixed during the `web/backend/` transfer

- **The chart list is declared once**, in `envistra.utilities.PlotSuite`. The backend
  duplicated `run_strategy_comparison.generate_plots` almost exactly — 29 versus 28 plot
  calls, 19 shared titles — so a chart changed in one silently diverged from the other.
  The titles are also the image filenames the UI groups by, so they are now single-sourced.
- **The progress total is derived**, not hand-kept. The backend advertised 21 plots while
  emitting 25; the suite declares 24 and reports 24.
- **Path traversal on image requests is rejected.** `image_name` came from the URL and was
  joined onto the results folder unchecked.
- **The image format is no longer hardcoded** as jpg in two places; it follows
  `config/simulation.json`.
- **Progress frames survive a late connection** (see above).

## Fixed during the `utilities/` transfer

- **Charts could be written into the wrong run's folder.** Every plot method built its own
  figure but then called the module-level `plt.savefig`/`plt.close`, so two simulations
  plotting concurrently — which the web backend does, on a two-worker pool — interleaved on
  the same current figure. Now `fig.savefig(...)` / `plt.close(fig)`, with a threaded test.
- **A run could not be reproduced.** See Reproducibility above.
- **The strategy-name heuristic is deleted.** It inferred the strategy from approach values
  and a `finInvestment >= 0.5` threshold, returning `"Unknown"` beyond the original four.
- **`run_config.json` was incomplete**: the pollution block read class defaults, so a
  strategy overriding an MLP hyperparameter had the override silently dropped from the
  record; `smoothingAlpha` was omitted although the estimator consumes it; and `agent_count`
  could exceed the number of agents actually recorded.
- **Plot filenames are slugged.** Titles become filenames and company names now come from
  user-authored JSON, so a `/` or `:` would have produced an unwritable Windows path.

## Fixed during the `src/` transfer

Kept on record because they explain why behaviour differs from the predecessor.

- **Quota destroyed by the `economically_efficient` buy path.**
  `__CreatePurchaseTransactionDictForGapFullCover` decrements every lot it takes from the
  shared market; the caller then filtered out the lots priced above the penalty and passed
  the **already-filtered** dict to `__ReturnExpensiveLotsToMarket`, so those lots were
  never refunded. That function's own condition was the exact negation of the filter, so
  its body was unreachable and nothing was ever refunded. It now receives the unfiltered
  dict and does both the refund and the filtering. **This changes results** for the
  Business and RevenueByQuotaSale strategies.
- **`QuotaMarket.TakeQuotaLot` raised `UnboundLocalError`** — `lot` was bound only in the
  full-lot branch while the partial branch dereferenced it. Behaviour-neutral: the method
  is dead, because the buy-side calculator mutates `marketDict` directly.
- **Nine `match self.approach` dispatchers had no `case _`**, so an unrecognised approach
  returned `None` and failed far from the cause. They now raise `ValueError`.
- **Dead code removed**: an unused `CompanyAgentFields` import in `ExpensesEstimator`; the
  `historyData`/`steps`, `finEff`/`penaltyHistory` and
  `industryAvgEcoEff`/`agentEcoEff`/`avgQuotaPrice`/`baseQuotaPrice` kwargs that no branch
  read, together with the per-agent-per-step market scan and industry eco-eff aggregation
  that existed only to compute them.

`self.penaltyHistory` is still accumulated in `PayQuotaExceedancePenalty` although nothing
reads it now; it was left as agent state rather than deleted.

## Known issues carried over from the source

Flag these when the relevant component is transferred; each needs a decision.

- **`simulation_runner._run_strategy_comparison_sync` duplicates ~200 lines** of
  `run_strategy_comparison.generate_plots`.
- **`utilities/Startup.py` is a 60+ symbol god-module** wildcard-imported by a runner.
  Consider a thin `bootstrap.py` exposing only `initialize_model`.
- **Config classes are mutable module-level singletons**, applied in place by
  `Loader.load_environment()`. The model reads them live on every step, so this is
  deliberate; note it is process-global, which matters if the web backend ever runs
  simulations concurrently.

### Reproducibility

**Every run is seeded: `initialize_model` generates a seed when none is given.** There are
two independent sources of randomness and both must be pinned: Mesa's own RNG drives the
shuffled buy order in `shuffle_do("BuyQuota")`, and `RevenueCalculator` samples
`random.gauss` from the `random` module. Seeding one and not the other looks deterministic
and is not — seeding only `random` was what the predecessor's structure invited, and a
regression test asserts it does *not* suffice.

The seed actually used is `model.seed_value` and `run_config.json` records it; `null` there
appears only in results made before seeds were generated, which cannot be reproduced.

### Plot output

Settings live in `config/simulation.json` (`dpi`, `figsize`, `format`, `resultsFolder`);
the default is 600 dpi. Each run writes a timestamped folder under `results/`.
They are edited on the web UI's **Settings** page (`GET/PUT /api/settings`, written through
`Writer.save_simulation`), and apply to the next run without a restart. `resultsFolder` is
read-only there: the backend fixes it at startup and lists runs from it. Because the format
can change between runs, the results page lists and serves images of every supported
format by each file's own extension, not one format fixed at startup.

`model_history.csv` has a `Year` column beside `Step` (`start year + step - 1`, the charts'
mapping); only the file gains it, the in-memory history is unchanged.

`format` may be one format or a list (`["png", "pdf"]`); every chart is then saved once per
format, and a single string still resolves to a one-item list. The results page shows one
entry per chart: it previews the first browser-viewable copy (`PlotBuilder.PREVIEW_ORDER`,
png → jpg → svg) and offers each copy for download. A PDF-only chart has no image preview;
it is opened in an embedded viewer instead.

### Two independent company flags

`config/companies/*.json` carries two booleans, both defaulting to `true`, so a newly
added file both runs and appears without further edits.

| Flag | Effect | Helper |
|---|---|---|
| `enabled` | Takes part in the simulation. A disabled company becomes **no agent**: it does not trade, and removing it changes the quota market for everyone else. | `Loader.enabled(companies)` |
| `plot` | Is drawn in the charts. Purely presentational — an enabled company still moves the market whether or not it is plotted. | `Loader.plotted(companies)` |

`plot: true` with `enabled: false` is rejected at load: a disabled company produces no
results to draw. An all-disabled roster is rejected too. Only *enabled* companies have
their `dataSource` verified against the workbooks, so a company can be disabled precisely
because its data is missing.

Today the four AES CORP variants are `plot: true` and the other eleven `false`, which
reproduces the predecessor's `AgentList[:4]` comparison without its positional assumption.

Note that disabling is industry-sensitive: quota allocation is scoped per industry, so
disabling a company only moves another's quota when they share an industry — though the
shared quota market means traded amounts and prices shift regardless.

**Line colour comes from the company**, `color` in `config/companies/*.json`. The loader
gives any company without one a distinct generated hue, deterministic for a given set of
files so two runs stay comparable. The four AES CORP files carry the original palette
explicitly, so the strategy-comparison charts look as they always did. The predecessor
cycled a four-entry list, which silently repeated colours beyond four agents.

### Running the web stack

One command, from the repository root:

```bash
python run_web.py
```

`run_web.py` starts uvicorn and Vite together, prefixes their output, opens the
browser and stops both on Ctrl+C. It runs a preflight first — package, node modules,
workbooks, ports — so a missing prerequisite is named instead of surfacing as a
confusing failure later.

It kills each child's whole process tree on exit. Uvicorn's `--reload` runs the
server in a subprocess, so terminating only the parent leaves the real server
holding the port.

The two parts separately, still from the repository root (`web` sits on the path):

```bash
python -m uvicorn web.backend.main:app --reload --port 8000
cd web/frontend && npm run dev      # http://localhost:5173
```

Vite proxies `/api` and `/ws` to `ENVISTRA_API_TARGET`, defaulting to port 8000 —
which is why the launcher can move the API port and the proxy still follows.

- **Config files are the API's shape**, so the managers read and write them
  directly instead of round-tripping through a serializer. `envistra.config.Writer`
  validates through the loader's own parser before writing, and writes atomically, so
  a rejected change leaves the previous file intact — which matters because invalid
  config now stops the app from starting rather than falling back.
- **`ConfigError` maps to 400** through an exception handler, so the loader's messages
  (which name the file and field) reach the client instead of becoming a 500.
- **Strategies are addressed by display name**, storage by filename id; both are
  returned. A rename edits the `name` field and leaves the file alone, because company
  configs reference the id. Deleting a strategy a company uses is refused, naming the
  companies — referential integrity the predecessor never had.
- **`/reset` is gone** for strategies and environment. It restored Python defaults that
  were deliberately deleted; `git checkout config/` is the honest equivalent. `/reload`
  remains.
- **`/api/companies` is new** — the predecessor had no agent API because the roster was
  hardcoded. Full CRUD, so creating a file adds an agent.
- **Progress frames are buffered per run and replayed on connect**, so a client that
  connects a moment late still sees the whole run. Previously only the last status
  survived.

### The web frontend

- **`/companies` is a new page** — the roster is file-driven now, so it lists every
  company with its effective colour and toggles for `enabled` (takes part in the
  simulation) and `plot` (drawn in the charts), plus create, edit and delete.
- **The data source is picked from a list**, served by `/api/data-sources`, which globs
  the workbook paths on each request without opening them; the form groups it by industry,
  i.e. by folder. A stored value not in the data is kept and flagged "missing", never
  replaced. With no workbooks present, or the list unreadable, the field falls back to free
  text. The list is refetched each time the form opens, so a workbook or folder added while
  the app runs appears without a restart; Excel's `~$` lock files are skipped here and by
  `DataReader.Read`. A copied-and-renamed workbook is a new source, and a new folder a new
  industry. A filename in two folders is a conflict: flagged in the UI (banner, table,
  form) and rejected by `DataReader.Read`.
- **Runs can be renamed, favourited, and deleted only after confirmation.** A run's id is
  its folder name, `<name>_<YYYY-MM-DD>_<HH-MM-SS>`; renaming (`PATCH /api/simulations/{id}`)
  renames the folder and keeps the timestamp suffix, so names stay unique and the date
  survives, and the UI shows the part before the suffix. Names are slugged Windows- and
  URL-safe. The favourite flag is in the run's `run_meta.json` (never in `run_config.json`,
  the reproducibility record); favourites are listed first. While the web runner writes a
  run's charts it keeps an `.in_progress` marker in the folder, and rename/delete answer 409.
- **Unsaved edits are guarded.** Environment, Settings, a strategy in edit mode and the
  company dialog each compare their form with the last loaded/saved copy; while they
  differ, `components/UnsavedChangesGuard.jsx` intercepts in-app navigation (React
  Router's `useBlocker`) with Stay / Discard and leave / Save and leave, and reload or
  tab close raises the browser's own prompt. `useBlocker` needs a data router, so
  `main.jsx` uses `createBrowserRouter` with one catch-all route around App's `<Routes>`.
- **A company's colour is set in its form**: a picker plus hex field, or "Automatic",
  which clears `color` so the loader assigns one. `PUT /api/companies/{name}` therefore
  treats an explicit `"color": null` as "clear"; every other null field means "unchanged".
- **The history's `Industry` values are folder names** (`hydro`, `solar`, …) rather than
  the EXIOBASE labels in the cells. The grouping is the same, so results are unchanged.
- **The Dashboard's counts come from the API.** It used to say a hardcoded "4 agents";
  it now reports how many are simulated and how many charted, and offers a seed field.
- **Reset buttons became "Reload from Disk"** on both config pages, matching the backend.
- **The WebSocket handler follows the backend's frames** — `started`, `initialized`,
  `step`, `plot`, `completed`, `error`, `ping` — and reads the explicit `progress`
  percentage rather than deriving one from the step count. Since the backend replays
  buffered frames on connect, the handler clears its plot list when a socket opens.
- **About is rewritten** to describe the current model: file-driven configuration, the
  two company flags, the 16-phase step, reproducibility via seed, and a note that
  results are not comparable with the predecessor.

A contract check in the verification suite asserts every endpoint the client calls
exists, every frame the backend emits is handled, and every approach the forms offer is
one the loader accepts.

## Decisions waiting on later steps

- **Only one chart set exists.** `plot` is a single boolean, so producing both a
  four-agent comparison and a fifteen-agent overview means flipping flags between runs.
  Named groups would allow several sets at once, if that becomes worth the schema.
- **`run_main.py` selected its agent by index** (`--agent`, default 14 = the last of 15).
  An index into a discovered directory is fragile; prefer selection by company name.
- **The web backend has no agent CRUD**, and its `strategy_manager` rewrites one whole
  `strategies.json`. Both need rework for per-file configs; strategy identity in the REST
  API is the display name, which is now distinct from the filename id.

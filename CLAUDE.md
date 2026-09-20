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

**Landed so far:** repository foundation (packaging, licence, documentation); `data/`
(workbooks untracked — see `data/README.md`); `src/` — the whole model core;
`config/` — restructured as file-driven JSON.

**The package imports and the configuration loads.** What is still missing is the layer
that joins them to the data: `utilities/` (`DataReader`, `PlotBuilder`, the run-config
writer), the CLI runners, and `web/`.

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
`dataSource` joins to the workbooks' `Name` column; several companies may share one, as
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
reference lists the available ids. Adding a parameter means editing the config class and
`Loader`; there is no separate serializer to keep in sync.

### Transfer order

Derived from the import graph; each tier depends only on earlier ones.

```
DONE    config layer, QuotaMarket, estimators, calculators, QuotaManager,
        CompanyAgent, CompanyEntity, CompanyAgentModel
NEXT    DataReader — joins config to data; calls Loader.verify_data_links
        PlotBuilder, the run-config writer
        a thin bootstrap exposing initialize_model
        CLI runners, web backend, web frontend
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
- **`RevenueCalculator` uses unseeded `random`/`numpy`** — runs are not reproducible.
- **Config classes are mutable module-level singletons**, applied in place by
  `Loader.load_environment()`. The model reads them live on every step, so this is
  deliberate; note it is process-global, which matters if the web backend ever runs
  simulations concurrently.

## Decisions waiting on later steps

- **How the strategy comparison picks its agents.** The predecessor sliced
  `AgentList[:4]`, assuming the first four entries were the four AES CORP variants, and
  `PlotBuilder.COLORS` has exactly four colours. Company files are discovered in filename
  order, which is deterministic but arbitrary — the runners need an explicit selector
  (a group field, or a named list) when they are transferred.
- **`run_main.py` selected its agent by index** (`--agent`, default 14 = the last of 15).
  An index into a discovered directory is fragile; prefer selection by company name.
- **The web backend has no agent CRUD**, and its `strategy_manager` rewrites one whole
  `strategies.json`. Both need rework for per-file configs; strategy identity in the REST
  API is the display name, which is now distinct from the filename id.

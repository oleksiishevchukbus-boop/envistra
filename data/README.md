# Source data

Historical company data used to seed the simulation. Twelve Excel workbooks, one per
company, ten rows each covering 2010–2019.

---

## ⚠ Provenance — TO BE CONFIRMED before this repository is made public

**This is a blocker on the first push, not a nice-to-have.**

The workbooks carry no attribution of any kind. Every one of the twelve reports
`creator='openpyxl'` and the identical creation timestamp `2025-03-16T15:48:07`, which
means they were regenerated in a single machine pass by a script that is not part of this
project. That pass stripped whatever metadata the original export carried. There is no
vendor name, licence, query record or download date in the files, and none anywhere in
the predecessor project either — its `Readme.txt` says only "The 1-st category type data
is used (Eectricity production)".

What the content suggests, as inference and **not** as evidence:

- the financial columns (`TotalAssets`, `TotalCurrentAssets`, `TotalOperatingExpenses`,
  `COGS`, `Revenue` for listed utilities, in reporting currency) look like a commercial
  terminal export — Refinitiv/Eikon, Datastream, Bloomberg, Capital IQ and Orbis are all
  plausible;
- the `Industry` strings are verbatim EXIOBASE/GTAP-style electricity activity labels,
  which suggests `Pollution` was joined from an emissions or environmentally-extended
  input-output database rather than from the financial vendor.

Before publishing, establish from outside this codebase — thesis notes, the original
download — and record here: **vendor, product, query date, and whether the licence
permits redistribution.** Redistributing terminal-sourced financials is typically
prohibited.

## Why the workbooks are not committed

`.gitignore` excludes `/data/**/*.xlsx` precisely because the above is unresolved. This
directory structure and this file are tracked; the data is not. A fresh clone therefore
has the layout but no workbooks, and the model will not run until they are placed.

To run the model, copy the twelve workbooks into the folders below. Any layout works —
see "Folder names are decorative".

```
data/
├── hydro/        AES CORP, DRAX GROUP PLC, NRG ENERGY, INC.
├── nec/          AGL ENERGY LTD, ATCO LTD, CEZ A.S, CHUBU ELECTRIC POWER CO INC
├── petroleum/    ITALGAS SPA, SNAM SPA
└── solar/        EDP RENOVAVEIS, ENGIE BRASIL ENERGIA SA, INFIGEN ENERGY
```

---

## Required schema

Each workbook: **first sheet only**, header in row 1, these ten columns in this order.

| Column | Type | Used for |
|---|---|---|
| `Year` | integer | starting-row filter and sort |
| `Name` | text | the join key to an agent — see the contract below |
| `Country` | text | **unused** by the code |
| `Industry` | text | `groupby` key for industry-level ratios; passed to the entity |
| `Pollution` | number | initial pollution |
| `TotalAssets` | number | initial assets |
| `TotalCurrentAssets` | number | scaled but **never read** — must still exist |
| `TotalOperatingExpenses` | number | summed with `COGS` into initial expenses |
| `COGS` | number | summed with `TotalOperatingExpenses` |
| `Revenue` | number | initial revenue |

## The contract

The loader is unforgiving and its failures are opaque — a violation usually surfaces as
`ValueError: can only convert an array of size 1 to a Python scalar`, thrown from an
`.item()` call deep inside entity creation, with nothing naming the offending company.
Check these before blaming the model:

1. **Exactly one row per `Name` with `Year == 2010`.** Zero rows and two rows fail
   identically. 2010 is `GlobalConfig.Startup.Year`.
2. **`Year` must be an integer column.** It is compared with `==` against a Python `int`.
   Stored as text or as a date, the filter silently matches nothing.
3. **`Name` must match `GlobalConfig`'s `DataName` byte-for-byte.** Two traps:
   - `CEZ A.S` is the data value; `CEZ A S` (no dot) is the *agent* name. They differ
     deliberately and are not interchangeable.
   - `NRG ENERGY, INC.` contains a comma and a trailing period. Both are significant.
4. **`Industry` strings must be identical across files in the same group** — they are
   `groupby` keys, so a stray space silently splits one industry into two.
5. **All ten columns must be present.** Six of them are scaled in one statement, so a
   missing column raises `KeyError` even if nothing later reads it — this is why
   `TotalCurrentAssets` cannot simply be dropped.

## Folder names are decorative

`DataReader.Read()` performs a single recursive glob, `data/**/*.xlsx`, and concatenates
whatever it finds. The file path is never parsed. Nesting depth, folder names and file
names carry no meaning: the four folders here mirror the four `Industry` values purely as
a human convenience, and the taxonomy the model actually uses comes from the `Industry`
**column**.

The predecessor project used `_Hydro/`, `_Nec/`, `_Petroleum/`, `_Solar/` and filenames
with a trailing underscore. Those underscores were dropped on transfer; the cell contents
were not touched. `nec` is "not elsewhere classified".

`GlobalConfig.DataFolder` is the relative path `"data"`, resolved against the **process
working directory** — so the model must be run from the repository root, and this folder
must stay there.

## Fifteen agents, twelve companies

`GlobalConfig.Startup.AgentList` has 15 entries but only 12 workbooks exist. `AES CORP`
is deliberately reused four times so the four strategies can be compared on an identical
company with identical starting conditions.

**The order of `AgentList` is load-bearing.** Slots 0–3 are the four `AES CORP` strategy
variants, and the strategy-comparison entry point takes `AgentList[:4]`. Slot 14
(`CHUBU ELECTRIC POWER`) is the default agent for the single-agent entry point. Do not
reorder the list.

## Scaling

Six columns — `Pollution`, `TotalAssets`, `TotalCurrentAssets`,
`TotalOperatingExpenses`, `COGS`, `Revenue` — are multiplied by
`GlobalConfig.Startup.MoneyValueMultiplier` (`10e-9`, i.e. 1e-8) as soon as they are
read. Note that **`Pollution` is scaled by the money multiplier too**; that is inherited
behaviour, not an oversight in the transfer. Raw values in these files are therefore
unscaled reporting-currency figures and raw pollution units.

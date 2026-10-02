import { useState, useEffect } from 'react'
import { api } from '../api/client'

// One file under config/companies/ per company, so the number of rows here is
// the number of agents. `enabled` decides whether a company takes part in the
// simulation at all — disabling one changes the quota market for the rest —
// while `plot` only decides whether it is drawn.

const EMPTY = {
  name: '',
  dataSource: '',
  strategy: '',
  enabled: true,
  plot: false,
  parameters: { finEffCoef: 1.0, ecoEffCoef: 1.4, finEffInvest: 1.0, ecoEffInvest: 1.0 },
}

const PARAMETERS = [
  ['finEffCoef', 'Financial efficiency coefficient'],
  ['ecoEffCoef', 'Ecological efficiency coefficient'],
  ['finEffInvest', 'Financial investment capacity'],
  ['ecoEffInvest', 'Ecological investment capacity'],
]

function Companies() {
  const [companies, setCompanies] = useState([])
  const [strategies, setStrategies] = useState([])
  const [dataSources, setDataSources] = useState([])
  const [sourceError, setSourceError] = useState(null)
  const [totals, setTotals] = useState({ total: 0, enabled: 0, plotted: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(null)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(null)

  useEffect(() => { load() }, [])

  const load = async () => {
    try {
      const [companyData, strategyData] = await Promise.all([
        api.listCompanies(),
        api.listStrategies(),
        loadDataSources(),
      ])
      setCompanies(companyData.companies || [])
      setTotals({
        total: companyData.total,
        enabled: companyData.enabled,
        plotted: companyData.plotted,
      })
      setStrategies(strategyData.strategies || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Fetched apart from the rest, and on every opening of the form, so a
  // workbook added while the app runs is offered without a reload. A failure
  // (an unreadable workbook) only degrades the field to free text.
  const loadDataSources = async () => {
    try {
      const data = await api.listDataSources()
      setDataSources(data.dataSources || [])
      setSourceError(null)
      return data.dataSources || []
    } catch (err) {
      setDataSources([])
      setSourceError(err.message)
      return []
    }
  }

  // The backend rejects a change that would produce unloadable config — a
  // plotted-but-disabled company, or disabling the last one — so surface its
  // message rather than pre-empting the rules here.
  const apply = async (action) => {
    try {
      setError(null)
      await action()
      await load()
      return true
    } catch (err) {
      setError(err.message)
      await load()
      return false
    }
  }

  const toggle = async (company, field) => {
    setBusy(company.name)
    await apply(() => api.updateCompany(company.name, { [field]: !company[field] }))
    setBusy(null)
  }

  const save = async () => {
    const payload = {
      ...form,
      parameters: Object.fromEntries(
        Object.entries(form.parameters).map(([k, v]) => [k, Number(v)])
      ),
    }
    const ok = await apply(() =>
      editing === '__new__'
        ? api.createCompany(payload)
        : api.updateCompany(editing, payload)
    )
    if (ok) { setEditing(null); setForm(null) }
  }

  const remove = async (company) => {
    if (!confirm(`Delete ${company.name}? This removes an agent from the simulation.`)) return
    setBusy(company.name)
    await apply(() => api.deleteCompany(company.name))
    setBusy(null)
  }

  const startEdit = (company) => {
    setEditing(company ? company.name : '__new__')
    setForm(company
      ? {
          name: company.name,
          dataSource: company.dataSource,
          strategy: company.strategy,
          enabled: company.enabled,
          plot: company.plot,
          parameters: { ...company.parameters },
        }
      : { ...EMPTY, strategy: strategies[0]?.id || '', dataSource: dataSources[0]?.name || '' })

    loadDataSources().then((sources) => {
      if (company || !sources.length) return
      setForm((f) => (f && !f.dataSource ? { ...f, dataSource: sources[0].name } : f))
    })
  }

  // With no workbooks loaded nothing can be checked, so nothing is flagged.
  const knownSources = new Set(dataSources.map((s) => s.name))
  const isMissing = (source) => Boolean(source) && dataSources.length > 0 && !knownSources.has(source)

  // A workbook is data/<industry>/<source>.xlsx. Companies reference only the
  // filename, so the same one in two folders is one source twice — and no
  // simulation starts.
  const conflicts = dataSources.filter((s) => s.files.length > 1)
  const filesOf = (source) => dataSources.find((s) => s.name === source)?.files || []
  const isDuplicated = (source) => filesOf(source).length > 1

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="w-8 h-8 border-2 border-eco-400 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="font-serif text-2xl font-semibold text-gray-100">Companies</h2>
          <p className="text-sm font-mono text-gray-500 mt-1">
            {totals.total} configured · {totals.enabled} simulated · {totals.plotted} charted
          </p>
        </div>
        <button
          onClick={() => startEdit(null)}
          className="px-4 py-2 text-sm font-mono bg-eco-500 text-navy-950 rounded hover:bg-eco-400 transition-colors"
        >
          + Add Company
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded">
          <pre className="text-sm font-mono text-red-300 whitespace-pre-wrap">{error}</pre>
          <button onClick={() => setError(null)} className="mt-2 text-xs font-mono text-red-400 underline">
            dismiss
          </button>
        </div>
      )}

      {conflicts.length > 0 && (
        <div className="mb-4 p-4 bg-amber-500/10 border border-amber-500/30 rounded text-sm font-mono text-amber-200">
          <p className="mb-2">
            {conflicts.length === 1 ? 'A workbook filename occurs' : `${conflicts.length} workbook filenames occur`} in
            more than one folder. No simulation will start until each is unique.
          </p>
          <ul className="space-y-1 text-amber-300/90">
            {conflicts.map((s) => (
              <li key={s.name}>{s.name}: {s.files.join(', ')}</li>
            ))}
          </ul>
          <p className="mt-2 text-xs text-amber-200/60">
            A data source is the workbook's filename and its folder is the industry, so a
            filename must be unique across folders. Remove one of the files, or rename it to
            add it as a separate source.
          </p>
        </div>
      )}

      <div className="bg-navy-900/80 rounded-lg border border-primary-800/50 overflow-hidden">
        <table className="w-full text-sm font-mono">
          <thead className="bg-navy-950/50 text-[10px] uppercase tracking-wider text-gray-500">
            <tr>
              <th className="text-left px-4 py-3">Company</th>
              <th className="text-left px-4 py-3">Data source</th>
              <th className="text-left px-4 py-3">Strategy</th>
              <th className="text-center px-4 py-3">Simulated</th>
              <th className="text-center px-4 py-3">Charted</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {companies.map((company) => (
              <tr key={company.id} className="border-t border-primary-800/30 hover:bg-navy-950/30">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    <span
                      className="w-3 h-3 rounded-sm shrink-0"
                      style={{ backgroundColor: company.effectiveColor }}
                      title={company.color ? 'colour from config' : 'colour assigned automatically'}
                    />
                    <span className={company.enabled ? 'text-gray-200' : 'text-gray-600 line-through'}>
                      {company.name}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 text-gray-400">
                  {company.dataSource}
                  {isMissing(company.dataSource) && (
                    <span className="ml-2 text-[10px] uppercase text-red-400/80" title="Not found in the workbooks">
                      missing
                    </span>
                  )}
                  {isDuplicated(company.dataSource) && (
                    <span className="ml-2 text-[10px] uppercase text-amber-400/80" title={filesOf(company.dataSource).join(', ')}>
                      duplicate
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 text-gray-400">{company.strategyName || company.strategy}</td>
                <td className="px-4 py-3 text-center">
                  <Toggle
                    on={company.enabled}
                    busy={busy === company.name}
                    onClick={() => toggle(company, 'enabled')}
                  />
                </td>
                <td className="px-4 py-3 text-center">
                  <Toggle
                    on={company.plot}
                    busy={busy === company.name}
                    onClick={() => toggle(company, 'plot')}
                  />
                </td>
                <td className="px-4 py-3 text-right whitespace-nowrap">
                  <button onClick={() => startEdit(company)} className="text-primary-400 hover:text-primary-300 mr-4">
                    edit
                  </button>
                  <button onClick={() => remove(company)} className="text-red-400 hover:text-red-300">
                    delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="mt-4 text-xs font-mono text-gray-600">
        Disabling a company removes its agent entirely, which changes the quota market for
        every other company. Un-charting one only hides it from the plots.
      </p>

      {form && (
        <div className="fixed inset-0 z-50 bg-navy-950/80 flex items-start justify-center overflow-y-auto py-12">
          <div className="bg-navy-900 border border-primary-800/50 rounded-lg w-full max-w-2xl p-6 space-y-5">
            <h3 className="font-serif text-xl text-gray-100">
              {editing === '__new__' ? 'Add company' : `Edit ${editing}`}
            </h3>

            <Field label="Name">
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className={inputClass}
              />
            </Field>

            {dataSources.length > 0 ? (
              <Field label="Data source" hint="The workbook (by filename) whose start-year data seeds this agent, grouped by its folder under data/ — the industry. Several companies may share one.">
                <DataSourceSelect
                  value={form.dataSource}
                  sources={dataSources}
                  companies={companies}
                  editing={editing}
                  missing={isMissing(form.dataSource)}
                  onChange={(v) => setForm({ ...form, dataSource: v })}
                />
                {isDuplicated(form.dataSource) && (
                  <p className="text-[11px] font-mono text-red-400">
                    Several workbooks have this filename: {filesOf(form.dataSource).join(', ')}.
                    No simulation will run until one is removed or renamed.
                  </p>
                )}
              </Field>
            ) : (
              <Field
                label="Data source"
                hint={sourceError
                  ? `The workbook list could not be read: ${sourceError}`
                  : 'No workbooks found under data/, so the name cannot be offered from a list; it is checked when a simulation next runs.'}
              >
                <input
                  value={form.dataSource}
                  onChange={(e) => setForm({ ...form, dataSource: e.target.value })}
                  className={inputClass}
                />
              </Field>
            )}

            <Field label="Strategy">
              <select
                value={form.strategy}
                onChange={(e) => setForm({ ...form, strategy: e.target.value })}
                className={inputClass}
              >
                {strategies.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </Field>

            <div className="grid grid-cols-2 gap-4">
              {PARAMETERS.map(([key, label]) => (
                <Field key={key} label={label}>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    value={form.parameters[key]}
                    onChange={(e) => setForm({
                      ...form,
                      parameters: { ...form.parameters, [key]: e.target.value },
                    })}
                    className={inputClass}
                  />
                </Field>
              ))}
            </div>

            <div className="flex gap-6">
              <Checkbox
                label="Simulated"
                checked={form.enabled}
                onChange={(v) => setForm({ ...form, enabled: v })}
              />
              <Checkbox
                label="Charted"
                checked={form.plot}
                onChange={(v) => setForm({ ...form, plot: v })}
              />
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => { setEditing(null); setForm(null) }}
                className="px-4 py-2 text-sm font-mono bg-navy-800 text-gray-300 rounded hover:bg-navy-700"
              >
                Cancel
              </button>
              <button
                onClick={save}
                className="px-4 py-2 text-sm font-mono bg-eco-500 text-navy-950 rounded hover:bg-eco-400"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

const inputClass =
  'w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm'

function Field({ label, hint, children }) {
  return (
    <div className="space-y-1">
      <label className="text-xs font-mono uppercase tracking-wider text-gray-400">{label}</label>
      {children}
      {hint && <p className="text-[11px] font-mono text-gray-600">{hint}</p>}
    </div>
  )
}

// Grouped by industry (the workbook's folder), since quota allocation is scoped
// per industry. A value
// not in the workbooks is kept as an option rather than silently replaced, so
// opening the editor never changes a company's data source by itself.
function DataSourceSelect({ value, sources, companies, editing, missing, onChange }) {
  const usage = {}
  for (const c of companies) {
    if (c.name !== editing) usage[c.dataSource] = (usage[c.dataSource] || 0) + 1
  }

  const byIndustry = {}
  for (const s of sources) (byIndustry[s.industry] ||= []).push(s)

  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} className={inputClass}>
      {missing && <option value={value}>{value} — not in workbooks</option>}
      {Object.entries(byIndustry).map(([industry, names]) => (
        <optgroup key={industry} label={industry}>
          {names.map(({ name, files }) => (
            <option key={name} value={name}>
              {name}
              {usage[name] ? ` · used by ${usage[name]}` : ''}
              {files.length > 1 ? ` · ${files.length} files ⚠` : ''}
            </option>
          ))}
        </optgroup>
      ))}
    </select>
  )
}

function Checkbox({ label, checked, onChange }) {
  return (
    <label className="flex items-center gap-2 text-sm font-mono text-gray-300 cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="accent-eco-500"
      />
      {label}
    </label>
  )
}

function Toggle({ on, busy, onClick }) {
  return (
    <button
      onClick={onClick}
      disabled={busy}
      className={`w-10 h-5 rounded-full relative transition-colors border disabled:opacity-40 ${
        on ? 'bg-eco-500 border-eco-500' : 'bg-navy-700 border-primary-700/70'
      }`}
      aria-pressed={on}
    >
      <span
        className={`absolute top-0.5 w-3.5 h-3.5 rounded-full transition-all ${
          on ? 'left-[21px] bg-navy-950' : 'left-0.5 bg-gray-500'
        }`}
      />
    </button>
  )
}

export default Companies

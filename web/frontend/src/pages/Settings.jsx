import { useState, useEffect } from 'react'
import { api } from '../api/client'

// Run-wide settings from config/simulation.json — currently chart output. Every
// run re-reads the file, so a saved change applies to the next simulation.
// resultsFolder is shown but not editable: the backend lists runs from it and
// fixes it at startup, so changing it here would hide every existing run.

const DPI_PRESETS = [
  [150, 'Draft'],
  [300, 'Standard'],
  [600, 'Print'],
]

// Every chart is saved once per ticked format. The results page previews the
// first viewable one (png, jpg, svg) and links every copy for download.
const FORMATS = [
  ['jpg', 'JPG', 'small files'],
  ['png', 'PNG', 'lossless, larger'],
  ['svg', 'SVG', 'vector, scales without loss'],
  ['pdf', 'PDF', 'vector, for documents'],
]
const ORDER = FORMATS.map(([f]) => f)

const inputClass =
  'w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm'

function Settings() {
  const [plots, setPlots] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  useEffect(() => { load() }, [])

  const load = async () => {
    try {
      setLoading(true)
      setPlots((await api.getSettings()).plots)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const flash = (message) => {
    setSuccess(message)
    setTimeout(() => setSuccess(null), 3000)
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setError(null)
      setSuccess(null)
      setPlots((await api.updateSettings({ plots })).plots)
      flash('Settings saved — they apply to the next simulation run')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const handleReload = async () => {
    if (!confirm('Reload settings from disk? Unsaved changes will be lost.')) return
    await load()
    flash('Settings reloaded from disk')
  }

  const set = (field, value) => setPlots({ ...plots, [field]: value })
  const setSide = (i, value) => {
    const figsize = [...plots.figsize]
    figsize[i] = value
    set('figsize', figsize)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="w-8 h-8 border-2 border-eco-400 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!plots) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-8 text-sm font-mono text-red-400">
        Could not load settings: {error}
      </div>
    )
  }

  const [w, h] = plots.figsize.map(Number)
  const dpi = Number(plots.dpi)
  const formats = plots.format
  const toggleFormat = (f) => set('format', formats.includes(f)
    ? formats.filter((x) => x !== f)
    : ORDER.filter((x) => x === f || formats.includes(x)))
  const raster = formats.some((f) => f === 'jpg' || f === 'png')
  const pixels = raster
    ? `${w} × ${h} in at ${dpi} dpi = ${Math.round(w * dpi)} × ${Math.round(h * dpi)} px`
    : `${w} × ${h} in, vector — dpi applies only to embedded raster parts`

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-mono font-semibold text-gray-100">Settings</h1>
          <p className="text-sm text-gray-500 mt-1">Run-wide settings — config/simulation.json</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 text-sm font-mono bg-eco-500 text-navy-950 rounded hover:bg-eco-400 transition-colors disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
          <button
            onClick={handleReload}
            disabled={saving}
            className="px-4 py-2 text-sm font-mono bg-navy-800 text-gray-300 rounded hover:bg-navy-700 transition-colors disabled:opacity-50"
          >
            Reload from Disk
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded text-red-400 text-sm font-mono whitespace-pre-wrap">
          {error}
          <button onClick={() => setError(null)} className="ml-4 underline">Dismiss</button>
        </div>
      )}
      {success && (
        <div className="mb-6 p-4 bg-eco-500/10 border border-eco-500/30 rounded text-eco-400 text-sm font-mono">
          {success}
        </div>
      )}

      <div className="bg-navy-900/80 rounded-lg border border-primary-800/50 p-6 space-y-6">
        <h2 className="font-mono text-gray-200">Chart output</h2>

        <div className="space-y-2">
          <label className="block text-xs font-mono uppercase tracking-wider text-gray-400">
            Quality (dpi)
          </label>
          <div className="flex flex-wrap items-center gap-2">
            {DPI_PRESETS.map(([value, label]) => (
              <button
                key={value}
                onClick={() => set('dpi', value)}
                className={`px-3 py-2 text-sm font-mono rounded border transition-colors ${
                  dpi === value
                    ? 'bg-primary-400/10 border-primary-400/40 text-primary-300'
                    : 'bg-navy-800 border-primary-800/50 text-gray-400 hover:text-gray-200'
                }`}
              >
                {label} · {value}
              </button>
            ))}
            <input
              type="number"
              min="10"
              max="2400"
              step="10"
              value={plots.dpi}
              onChange={(e) => set('dpi', e.target.value === '' ? '' : parseInt(e.target.value, 10))}
              className={`${inputClass} w-28`}
              aria-label="Custom dpi"
            />
          </div>
          <p className="text-[11px] font-mono text-gray-600">
            Higher dpi gives sharper images but larger files and slower plotting. 10–2400.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {['Width', 'Height'].map((label, i) => (
            <div key={label} className="space-y-1">
              <label className="block text-xs font-mono uppercase tracking-wider text-gray-400">
                {label} (inches)
              </label>
              <input
                type="number"
                min="1"
                step="0.5"
                value={plots.figsize[i]}
                onChange={(e) => setSide(i, e.target.value === '' ? '' : parseFloat(e.target.value))}
                className={inputClass}
              />
            </div>
          ))}
        </div>

        <div className="space-y-1">
          <label className="block text-xs font-mono uppercase tracking-wider text-gray-400">Formats</label>
          <div className="flex flex-wrap gap-2">
            {FORMATS.map(([value, label, note]) => {
              const on = formats.includes(value)
              return (
                <label
                  key={value}
                  className={`flex items-center gap-2 px-3 py-2 rounded border cursor-pointer text-sm font-mono transition-colors ${
                    on
                      ? 'bg-primary-400/10 border-primary-400/40 text-primary-300'
                      : 'bg-navy-800 border-primary-800/50 text-gray-400 hover:text-gray-200'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={on}
                    onChange={() => toggleFormat(value)}
                    className="accent-eco-500"
                  />
                  {label}
                  <span className="text-[11px] text-gray-500">{note}</span>
                </label>
              )
            })}
          </div>
          <p className={`text-[11px] font-mono ${formats.length ? 'text-gray-600' : 'text-red-400'}`}>
            {formats.length === 0
              ? 'Choose at least one format.'
              : formats.length === 1 && formats[0] === 'pdf'
                ? 'PDF only: the results page lists the charts to open or download, without inline previews.'
                : 'Every chart is saved once per ticked format; each extra format adds plotting time.'}
          </p>
        </div>

        <p className="text-sm font-mono text-gray-300 bg-navy-950/50 rounded px-3 py-2">{pixels}</p>

        <div className="space-y-1">
          <label className="block text-xs font-mono uppercase tracking-wider text-gray-400">Results folder</label>
          <input value={plots.resultsFolder} disabled className={`${inputClass} opacity-50`} />
          <p className="text-[11px] font-mono text-gray-600">
            Fixed while the server runs, because existing runs are listed from it. To change it,
            edit config/simulation.json and restart.
          </p>
        </div>
      </div>

      <div className="mt-8 p-4 bg-navy-900/40 rounded-lg border border-primary-800/30">
        <p className="text-xs font-mono text-gray-500">
          Changes apply to the next simulation run. Charts of earlier runs keep the quality and
          format they were made with.
        </p>
      </div>
    </div>
  )
}

export default Settings

import { useState, useEffect } from 'react'
import { api } from '../api/client'

// A run's name with its favourite star and inline rename, shared by the
// Dashboard list and the results page.
//
// Renaming renames the run's folder under results/ (the timestamp suffix is
// kept), so the run comes back with a new run_id; `onUpdated` receives the
// whole updated run and the caller decides what to do with the new id.

function Star({ on }) {
  return (
    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill={on ? 'currentColor' : 'none'} stroke="currentColor">
      <path strokeLinejoin="round" strokeWidth={2}
        d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9L12 3z" />
    </svg>
  )
}

function RunName({ run, onUpdated, size = 'sm', revealOnHover = true }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(run.name)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => { if (!editing) setDraft(run.name) }, [run.name, editing])

  const locked = run.status === 'running'
  const hover = revealOnHover ? 'opacity-0 group-hover:opacity-100 focus:opacity-100' : ''

  const update = async (changes) => {
    setBusy(true)
    setError(null)
    try {
      onUpdated(await api.updateSimulation(run.run_id, changes))
      return true
    } catch (err) {
      setError(err.message)
      return false
    } finally {
      setBusy(false)
    }
  }

  const commit = async () => {
    const name = draft.trim()
    if (!name || name === run.name) {
      setEditing(false)
      setDraft(run.name)
      return
    }
    if (await update({ name })) setEditing(false)
  }

  // Only the controls swallow clicks; a click on the name itself still reaches
  // the row, which opens the run.
  const stop = (e) => e.stopPropagation()
  const text = size === 'lg' ? 'text-2xl font-semibold' : 'text-sm'

  return (
    <div className="min-w-0">
      <div className="flex items-center gap-1.5 min-w-0">
        {editing ? (
          <input
            autoFocus
            value={draft}
            maxLength={80}
            disabled={busy}
            onClick={stop}
            onChange={(e) => setDraft(e.target.value)}
            onBlur={commit}
            onKeyDown={(e) => {
              if (e.key === 'Enter') { e.preventDefault(); commit() }
              if (e.key === 'Escape') { setEditing(false); setDraft(run.name); setError(null) }
            }}
            className={`${text} font-mono min-w-0 flex-1 px-2 py-0.5 bg-navy-800 border border-primary-600 rounded text-gray-100`}
            aria-label="Run name"
          />
        ) : (
          <span className={`${text} font-mono text-gray-300 truncate group-hover:text-eco-400 transition-colors`}>
            {run.name}
          </span>
        )}

        <button
          onClick={(e) => { stop(e); update({ favorite: !run.favorite }) }}
          disabled={busy}
          title={run.favorite ? 'Remove from favourites' : 'Mark as favourite'}
          aria-pressed={run.favorite}
          className={`p-1 shrink-0 transition-colors ${
            run.favorite ? 'text-amber-400 hover:text-amber-300' : `text-gray-600 hover:text-amber-400 ${hover}`
          }`}
        >
          <Star on={run.favorite} />
        </button>

        {!editing && (
          <button
            onClick={(e) => { stop(e); setEditing(true); setError(null) }}
            disabled={busy || locked}
            title={locked ? 'Cannot rename a run in progress' : 'Rename (renames the results folder too)'}
            className={`p-1 shrink-0 text-gray-600 hover:text-primary-300 transition-colors disabled:opacity-30 ${hover}`}
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M15.2 5.2l3.6 3.6M4 20l4.5-1 10.3-10.3a2.5 2.5 0 00-3.5-3.5L5 15.5 4 20z" />
            </svg>
          </button>
        )}
      </div>
      {error && (
        <p onClick={stop} className="mt-1 text-[11px] font-mono text-red-400 whitespace-normal">{error}</p>
      )}
    </div>
  )
}

export default RunName

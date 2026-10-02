import { useEffect, useState } from 'react'
import { useBlocker } from 'react-router-dom'

// Stops navigation away from a page with unsaved edits and asks what to do.
//
// Two ways out are covered: moving to another tab of the app (intercepted with
// `useBlocker`, so our own dialog appears), and reloading or closing the
// browser tab (`beforeunload` — browsers only allow their generic prompt there).
//
// `when` is the page's own notion of dirty. `onSave`, if given, is the page's
// save action returning true on success; it adds a "Save and leave" button and
// the navigation proceeds only if the save succeeded.
function UnsavedChangesGuard({ when, onSave }) {
  const blocker = useBlocker(({ currentLocation, nextLocation }) =>
    when && currentLocation.pathname !== nextLocation.pathname)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!when) return
    const warn = (e) => {
      e.preventDefault()
      e.returnValue = ''
    }
    window.addEventListener('beforeunload', warn)
    return () => window.removeEventListener('beforeunload', warn)
  }, [when])

  // Edits undone or saved while the dialog was open: nothing left to guard.
  useEffect(() => {
    if (blocker.state === 'blocked' && !when) blocker.proceed()
  }, [blocker, when])

  if (blocker.state !== 'blocked') return null

  const saveAndLeave = async () => {
    setSaving(true)
    const ok = await onSave()
    setSaving(false)
    if (ok) blocker.proceed()
    else blocker.reset()
  }

  return (
    <div className="fixed inset-0 z-[60] bg-navy-950/80 flex items-center justify-center p-4">
      <div
        role="alertdialog"
        aria-labelledby="unsaved-title"
        className="bg-navy-900 border border-amber-500/40 rounded-lg w-full max-w-md p-6 space-y-4"
      >
        <h3 id="unsaved-title" className="font-serif text-xl text-gray-100">Unsaved changes</h3>
        <p className="text-sm font-mono text-gray-400">
          You have changes on this page that are not saved. Leaving now will lose them.
        </p>
        <div className="flex flex-wrap justify-end gap-3 pt-2">
          <button
            onClick={() => blocker.reset()}
            disabled={saving}
            className="px-4 py-2 text-sm font-mono bg-navy-800 text-gray-300 rounded hover:bg-navy-700 disabled:opacity-50"
            autoFocus
          >
            Stay on page
          </button>
          <button
            onClick={() => blocker.proceed()}
            disabled={saving}
            className="px-4 py-2 text-sm font-mono bg-red-500/15 text-red-300 border border-red-500/30 rounded hover:bg-red-500/25 disabled:opacity-50"
          >
            Discard and leave
          </button>
          {onSave && (
            <button
              onClick={saveAndLeave}
              disabled={saving}
              className="px-4 py-2 text-sm font-mono bg-eco-500 text-navy-950 rounded hover:bg-eco-400 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save and leave'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default UnsavedChangesGuard

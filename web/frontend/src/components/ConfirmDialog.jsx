// A modal yes/no question, styled like the unsaved-changes dialog. `danger`
// colours the confirm button for destructive actions. Rendered only when open.
function ConfirmDialog({ open, title, children, confirmLabel = 'Confirm', danger = false,
                         busy = false, onConfirm, onCancel }) {
  if (!open) return null
  return (
    <div
      className="fixed inset-0 z-[60] bg-navy-950/80 flex items-center justify-center p-4"
      onClick={busy ? undefined : onCancel}
    >
      <div
        role="alertdialog"
        aria-labelledby="confirm-title"
        onClick={(e) => e.stopPropagation()}
        className={`bg-navy-900 border rounded-lg w-full max-w-md p-6 space-y-4 ${
          danger ? 'border-red-500/40' : 'border-primary-800/50'
        }`}
      >
        <h3 id="confirm-title" className="font-serif text-xl text-gray-100">{title}</h3>
        <div className="text-sm font-mono text-gray-400 space-y-2">{children}</div>
        <div className="flex justify-end gap-3 pt-2">
          <button
            onClick={onCancel}
            disabled={busy}
            autoFocus
            className="px-4 py-2 text-sm font-mono bg-navy-800 text-gray-300 rounded hover:bg-navy-700 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={busy}
            className={`px-4 py-2 text-sm font-mono rounded disabled:opacity-50 ${
              danger
                ? 'bg-red-500/15 text-red-300 border border-red-500/30 hover:bg-red-500/25'
                : 'bg-eco-500 text-navy-950 hover:bg-eco-400'
            }`}
          >
            {busy ? 'Working...' : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ConfirmDialog

// Two shares of one whole — they must sum to 1, which the loader enforces.
// Editing either sets the other to the remainder, so the pair can never be
// saved inconsistently. A file edited by hand into an invalid pair is shown
// as such until one value is touched.

const inputClass =
  'w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50'

// Two decimals is the form's precision; rounding keeps 1 - 0.7 from showing
// as 0.30000000000000004.
const remainder = (v) => Math.round((1 - v) * 10000) / 10000

function SharePair({ left, right, disabled, onUpdateField }) {
  const set = (changed, other, raw) => {
    const v = parseFloat(raw)
    if (Number.isNaN(v)) return
    const clamped = Math.min(1, Math.max(0, v))
    onUpdateField(changed.path, clamped)
    onUpdateField(other.path, remainder(clamped))
  }

  const total = (left.value ?? 0) + (right.value ?? 0)
  const valid = Math.abs(total - 1) < 1e-6

  return (
    <div>
      <div className="grid grid-cols-2 gap-4">
        {[[left, right], [right, left]].map(([field, other]) => (
          <div key={field.path}>
            <label className="block text-xs font-mono text-gray-500 mb-1">{field.label}</label>
            <input
              type="number"
              min="0"
              max="1"
              step={field.step ?? '0.05'}
              value={field.value ?? 0.5}
              onChange={(e) => set(field, other, e.target.value)}
              disabled={disabled}
              className={inputClass}
            />
          </div>
        ))}
      </div>
      <p className={`mt-1 text-[11px] font-mono ${valid ? 'text-gray-600' : 'text-red-400'}`}>
        {valid
          ? 'Together they make 1 — changing one sets the other.'
          : `They must sum to 1 (now ${Math.round(total * 10000) / 10000}); edit either to fix.`}
      </p>
    </div>
  )
}

export default SharePair

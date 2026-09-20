function ExpensesReEstimationSection({ estimators, disabled, onUpdateField }) {
  return (
    <div className="mb-4 bg-navy-900/60 border border-primary-800/30 rounded-lg p-4">
      <h4 className="text-sm font-mono text-gray-400 mb-3">Expenses Re-Estimation</h4>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Expenses Re-Estimation</label>
          <select
            value={estimators?.expenses_re_estimation?.approach ?? 'none'}
            onChange={(e) => onUpdateField('estimators.expenses_re_estimation.approach', e.target.value)}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          >
            <option value="none">None</option>
            <option value="gap_proportional">Gap Proportional</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Max Reduction Rate</label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.05"
            value={estimators?.expenses_re_estimation?.maxReductionRate ?? 0}
            onChange={(e) => onUpdateField('estimators.expenses_re_estimation.maxReductionRate', parseFloat(e.target.value))}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          />
        </div>
      </div>
    </div>
  )
}

export default ExpensesReEstimationSection

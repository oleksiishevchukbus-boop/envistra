import SharePair from './SharePair'

function ExpensesEstimatorSection({ estimators, disabled, onUpdateField }) {
  return (
    <div className="mb-4 bg-navy-900/60 border border-primary-800/30 rounded-lg p-4">
      <h4 className="text-sm font-mono text-gray-400 mb-3">Expenses Estimator</h4>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Expenses Approach</label>
          <select
            value={estimators?.expenses?.approach ?? 'performance_based'}
            onChange={(e) => onUpdateField('estimators.expenses.approach', e.target.value)}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          >
            <option value="general">General</option>
            <option value="performance_based">Performance Based</option>
            <option value="performance_based_relative">Performance Based Relative</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Smoothing Alpha</label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.05"
            value={estimators?.expenses?.smoothingAlpha ?? 0.7}
            onChange={(e) => onUpdateField('estimators.expenses.smoothingAlpha', parseFloat(e.target.value))}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Change Threshold Upper</label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={estimators?.expenses?.changeThreshold_Upper ?? 0.15}
            onChange={(e) => onUpdateField('estimators.expenses.changeThreshold_Upper', parseFloat(e.target.value))}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          />
        </div>
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Change Threshold Lower</label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={estimators?.expenses?.changeThreshold_Lower ?? 0.05}
            onChange={(e) => onUpdateField('estimators.expenses.changeThreshold_Lower', parseFloat(e.target.value))}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          />
        </div>
      </div>
      <SharePair
        left={{ path: 'estimators.expenses.featuresImpact.netRevenue',
                label: 'Net Revenue Impact', value: estimators?.expenses?.featuresImpact?.netRevenue }}
        right={{ path: 'estimators.expenses.featuresImpact.quotaExceedance',
                 label: 'Quota Exceedance Impact', value: estimators?.expenses?.featuresImpact?.quotaExceedance }}
        disabled={disabled}
        onUpdateField={onUpdateField}
      />
    </div>
  )
}

export default ExpensesEstimatorSection

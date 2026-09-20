function PollutionEstimatorSection({ estimators, disabled, onUpdateField }) {
  return (
    <div className="mb-4 bg-navy-900/60 border border-primary-800/30 rounded-lg p-4">
      <h4 className="text-sm font-mono text-gray-400 mb-3">Pollution Estimator</h4>
      <div>
        <label className="block text-xs font-mono text-gray-500 mb-1">Pollution Estimator</label>
        <select
          value={estimators?.pollution?.approach ?? 'MLP_based'}
          onChange={(e) => onUpdateField('estimators.pollution.approach', e.target.value)}
          disabled={disabled}
          className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
        >
          <option value="MLP_based">MLP Based</option>
          <option value="general">General</option>
        </select>
      </div>
    </div>
  )
}

export default PollutionEstimatorSection

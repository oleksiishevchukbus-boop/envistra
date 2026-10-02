import SharePair from './SharePair'

function InvestmentSection({ approach, investmentRatios, disabled, onUpdateField }) {
  return (
    <div className="mb-4 bg-navy-900/60 border border-primary-800/30 rounded-lg p-4">
      <h4 className="text-sm font-mono text-gray-400 mb-3">Investment Configuration</h4>
      <div className="mb-4">
        <label className="block text-xs font-mono text-gray-500 mb-1">Approach</label>
        <select
          value={approach ?? 'revenue_based'}
          onChange={(e) => onUpdateField('estimators.investment.approach', e.target.value)}
          disabled={disabled}
          className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
        >
          <option value="revenue_based">Revenue Based</option>
          <option value="performance_based">Performance Based</option>
        </select>
      </div>
      <div className="mb-4">
        <SharePair
          left={{ path: 'estimators.investment.investmentRatios.finInvestment',
                  label: 'Financial Investment Share', value: investmentRatios?.finInvestment, step: '0.1' }}
          right={{ path: 'estimators.investment.investmentRatios.ecoInvestment',
                   label: 'Ecological Investment Share', value: investmentRatios?.ecoInvestment, step: '0.1' }}
          disabled={disabled}
          onUpdateField={onUpdateField}
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Revenue to Investment Ratio</label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={investmentRatios?.revenueToInvestmentRatio ?? 0.075}
            onChange={(e) => onUpdateField('estimators.investment.investmentRatios.revenueToInvestmentRatio', parseFloat(e.target.value))}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          />
        </div>
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Minimal Investment</label>
          <input
            type="number"
            min="0"
            max="0.1"
            step="0.001"
            value={investmentRatios?.minimalInvestment ?? 0.002}
            onChange={(e) => onUpdateField('estimators.investment.investmentRatios.minimalInvestment', parseFloat(e.target.value))}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          />
        </div>
      </div>
    </div>
  )
}

export default InvestmentSection

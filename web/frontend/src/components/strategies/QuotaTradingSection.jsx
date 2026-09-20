function QuotaTradingSection({ calculators, disabled, onUpdateField }) {
  return (
    <div className="mb-4 bg-navy-900/60 border border-primary-800/30 rounded-lg p-4">
      <h4 className="text-sm font-mono text-gray-400 mb-3">Quota Buying</h4>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Buy Price Approach</label>
          <select
            value={calculators?.quota_to_buy_price?.approach ?? 'ignorance'}
            onChange={(e) => onUpdateField('calculators.quota_to_buy_price.approach', e.target.value)}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          >
            <option value="ignorance">Ignorance</option>
            <option value="economically_efficient">Economically Efficient</option>
            <option value="gap_full_cover">Gap Full Cover</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Quota Reserve (Buy)</label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={calculators?.quota_to_buy_amount?.quotaReserve ?? 0}
            onChange={(e) => onUpdateField('calculators.quota_to_buy_amount.quotaReserve', parseFloat(e.target.value))}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          />
        </div>
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Assets for Trading</label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.05"
            value={calculators?.quota_to_buy_price?.assetsPartForTrading ?? 0.1}
            onChange={(e) => onUpdateField('calculators.quota_to_buy_price.assetsPartForTrading', parseFloat(e.target.value))}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          />
        </div>
      </div>
    </div>
  )
}

export default QuotaTradingSection

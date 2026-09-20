function SellPriceSection({ sellPriceConfig, sellAmountConfig, disabled, onUpdateField }) {
  return (
    <div className="bg-navy-900/60 border border-primary-800/30 rounded-lg p-4">
      <h4 className="text-sm font-mono text-gray-400 mb-3">Quota Selling</h4>
      <div className="grid grid-cols-5 gap-4">
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Sell Price Approach</label>
          <select
            value={sellPriceConfig?.approach ?? 'general'}
            onChange={(e) => onUpdateField('calculators.quota_to_sell_price.approach', e.target.value)}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          >
            <option value="general">General</option>
            <option value="history_based">History Based</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Unit Price</label>
          <input
            type="number"
            min="0"
            max="10"
            step="0.25"
            value={sellPriceConfig?.unitPrice ?? 2.5}
            onChange={(e) => onUpdateField('calculators.quota_to_sell_price.unitPrice', parseFloat(e.target.value))}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          />
        </div>
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Change Threshold</label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.1"
            value={sellPriceConfig?.changeThreshold ?? 0}
            onChange={(e) => onUpdateField('calculators.quota_to_sell_price.changeThreshold', parseFloat(e.target.value))}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          />
        </div>
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Sales Target</label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.1"
            value={sellPriceConfig?.salesTarget ?? 0.5}
            onChange={(e) => onUpdateField('calculators.quota_to_sell_price.salesTarget', parseFloat(e.target.value))}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          />
        </div>
        <div>
          <label className="block text-xs font-mono text-gray-500 mb-1">Quota Reserve (Sell)</label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={sellAmountConfig?.quotaReserve ?? 0}
            onChange={(e) => onUpdateField('calculators.quota_to_sell_amount.quotaReserve', parseFloat(e.target.value))}
            disabled={disabled}
            className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          />
        </div>
      </div>
    </div>
  )
}

export default SellPriceSection

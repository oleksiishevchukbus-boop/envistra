import BasicInfoSection from './BasicInfoSection'
import InvestmentSection from './InvestmentSection'
import PollutionEstimatorSection from './PollutionEstimatorSection'
import ExpensesEstimatorSection from './ExpensesEstimatorSection'
import ExpensesReEstimationSection from './ExpensesReEstimationSection'
import QuotaTradingSection from './QuotaTradingSection'
import SellPriceSection from './SellPriceSection'

function StrategyCard({
  strategy,
  isExpanded,
  isEditing,
  editForm,
  saving,
  onExpand,
  onEdit,
  onCancelEdit,
  onSave,
  onDelete,
  onClone,
  onUpdateField,
}) {
  const disabled = !isEditing

  return (
    <div className="relative bg-navy-900/80 rounded-lg border border-primary-800/50 overflow-hidden">
      {/* Card Header */}
      <div
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-navy-800/50 transition-colors"
        onClick={() => onExpand(strategy.name)}
      >
        <div className="flex items-center gap-4">
          <div
            className="w-4 h-4 rounded-full"
            style={{ backgroundColor: strategy.color }}
          />
          <div>
            <h3 className="font-mono text-gray-200">{strategy.name}</h3>
            <p className="text-xs text-gray-500">{strategy.description}</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-xs font-mono text-gray-500">
            {strategy.summary?.investment_split}
          </div>
          <svg
            className={`w-5 h-5 text-gray-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && editForm && (
        <div className="border-t border-primary-800/50 p-6 bg-navy-950/50">
          {/* Action buttons */}
          <div className="flex gap-3 mb-6">
            {isEditing ? (
              <>
                <button
                  onClick={onSave}
                  disabled={saving}
                  className="px-4 py-2 text-sm font-mono bg-eco-500 text-navy-950 rounded hover:bg-eco-400 transition-colors disabled:opacity-50"
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  onClick={onCancelEdit}
                  className="px-4 py-2 text-sm font-mono bg-navy-800 text-gray-300 rounded hover:bg-navy-700 transition-colors"
                >
                  Cancel
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => onEdit(strategy.name)}
                  className="px-4 py-2 text-sm font-mono bg-primary-600 text-white rounded hover:bg-primary-500 transition-colors"
                >
                  Edit
                </button>
                <button
                  onClick={() => onClone(strategy.name)}
                  className="px-4 py-2 text-sm font-mono bg-navy-800 text-gray-300 rounded hover:bg-navy-700 transition-colors"
                >
                  Clone
                </button>
                <button
                  onClick={() => onDelete(strategy.name)}
                  className="px-4 py-2 text-sm font-mono bg-red-500/20 text-red-400 rounded hover:bg-red-500/30 transition-colors"
                >
                  Delete
                </button>
              </>
            )}
          </div>

          <BasicInfoSection editForm={editForm} disabled={disabled} onUpdateField={onUpdateField} />
          <InvestmentSection
            approach={editForm.estimators?.investment?.approach}
            investmentRatios={editForm.estimators?.investment?.investmentRatios}
            disabled={disabled}
            onUpdateField={onUpdateField}
          />
          <PollutionEstimatorSection estimators={editForm.estimators} disabled={disabled} onUpdateField={onUpdateField} />
          <ExpensesEstimatorSection estimators={editForm.estimators} disabled={disabled} onUpdateField={onUpdateField} />
          <ExpensesReEstimationSection estimators={editForm.estimators} disabled={disabled} onUpdateField={onUpdateField} />
          <QuotaTradingSection calculators={editForm.calculators} disabled={disabled} onUpdateField={onUpdateField} />
          <SellPriceSection
            sellPriceConfig={editForm.calculators?.quota_to_sell_price}
            sellAmountConfig={editForm.calculators?.quota_to_sell_amount}
            disabled={disabled}
            onUpdateField={onUpdateField}
          />
        </div>
      )}
    </div>
  )
}

export default StrategyCard

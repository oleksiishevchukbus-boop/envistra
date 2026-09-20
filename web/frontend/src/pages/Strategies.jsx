import { useState, useEffect } from 'react'
import { api } from '../api/client'
import StrategyCard from '../components/strategies/StrategyCard'

function Strategies() {
  const [strategies, setStrategies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [expandedStrategy, setExpandedStrategy] = useState(null)
  const [editingStrategy, setEditingStrategy] = useState(null)
  const [editForm, setEditForm] = useState(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadStrategies()
  }, [])

  const loadStrategies = async () => {
    try {
      setLoading(true)
      const data = await api.listStrategies()
      setStrategies(data.strategies || [])
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleExpand = async (name) => {
    if (expandedStrategy === name) {
      setExpandedStrategy(null)
      setEditingStrategy(null)
      setEditForm(null)
      return
    }

    try {
      const fullStrategy = await api.getStrategy(name)
      setExpandedStrategy(name)
      setEditForm(fullStrategy)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleEdit = (name) => {
    setEditingStrategy(name)
  }

  const handleCancelEdit = () => {
    setEditingStrategy(null)
    if (expandedStrategy) {
      api.getStrategy(expandedStrategy).then(setEditForm)
    }
  }

  const handleSave = async () => {
    if (!editForm || !editingStrategy) return

    try {
      setSaving(true)
      await api.updateStrategy(editingStrategy, editForm)
      setEditingStrategy(null)
      await loadStrategies()
      // Reload expanded strategy
      if (expandedStrategy) {
        const updated = await api.getStrategy(editForm.name)
        setEditForm(updated)
        setExpandedStrategy(editForm.name)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (name) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return

    try {
      await api.deleteStrategy(name)
      setExpandedStrategy(null)
      setEditingStrategy(null)
      await loadStrategies()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleClone = async (sourceName) => {
    const newName = prompt('Enter name for the cloned strategy:', `${sourceName} Copy`)
    if (!newName) return

    try {
      await api.cloneStrategy(sourceName, newName)
      await loadStrategies()
    } catch (err) {
      setError(err.message)
    }
  }

  // Each strategy is its own file under config/strategies/. Reload re-reads the
  // directory; there is no reset, because the Python defaults it restored were
  // deliberately removed.
  const handleReload = async () => {
    if (!confirm('Reload strategies from disk? Unsaved changes will be lost.')) return

    try {
      await api.reloadStrategies()
      setExpandedStrategy(null)
      setEditingStrategy(null)
      setEditForm(null)
      await loadStrategies()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleAddStrategy = async () => {
    const name = prompt('Enter name for new strategy:')
    if (!name) return

    try {
      await api.createStrategy({
        name,
        description: 'Custom strategy',
        color: '#888888',
        estimators: {
          expenses: {
            approach: 'performance_based',
            changeThreshold_Upper: 0.15,
            changeThreshold_Lower: 0.05,
            featuresImpact: { netRevenue: 0.5, quotaExceedance: 0.5 }
          },
          investment: {
            approach: 'revenue_based',
            investmentRatios: {
              revenueToInvestmentRatio: 0.075,
              minimalInvestment: 0.002,
              finInvestment: 0.5,
              ecoInvestment: 0.5
            }
          },
          pollution: { approach: 'MLP_based' },
          expenses_re_estimation: { approach: 'none', maxReductionRate: 0 }
        },
        calculators: {
          quota_to_sell_amount: { approach: 'reserve_based', quotaReserve: 0.02 },
          quota_to_sell_price: { approach: 'general', unitPrice: 2.5, changeThreshold: 0, salesTarget: 0.5 },
          quota_to_buy_amount: { approach: 'reserve_based', quotaReserve: 0.02 },
          quota_to_buy_price: { approach: 'economically_efficient', assetsPartForTrading: 0.1 }
        }
      })
      await loadStrategies()
    } catch (err) {
      setError(err.message)
    }
  }

  const updateEditForm = (path, value) => {
    setEditForm(prev => {
      const newForm = JSON.parse(JSON.stringify(prev))
      const parts = path.split('.')
      let obj = newForm
      for (let i = 0; i < parts.length - 1; i++) {
        obj = obj[parts[i]]
      }
      obj[parts[parts.length - 1]] = value
      return newForm
    })
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-mono font-semibold text-gray-100">Strategy Configuration</h1>
          <p className="text-sm text-gray-500 mt-1">Manage agent behavior strategies for simulations</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleAddStrategy}
            className="px-4 py-2 text-sm font-mono bg-eco-500 text-navy-950 rounded hover:bg-eco-400 transition-colors"
          >
            + Add Strategy
          </button>
          <button
            onClick={handleReload}
            className="px-4 py-2 text-sm font-mono bg-navy-800 text-gray-300 rounded hover:bg-navy-700 transition-colors"
          >
            Reload from Disk
          </button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded text-red-400 text-sm font-mono">
          {error}
          <button onClick={() => setError(null)} className="ml-4 underline">Dismiss</button>
        </div>
      )}

      {/* Strategy Cards */}
      <div className="space-y-4">
        {strategies.map((strategy) => (
          <StrategyCard
            key={strategy.name}
            strategy={strategy}
            isExpanded={expandedStrategy === strategy.name}
            isEditing={editingStrategy === strategy.name}
            editForm={expandedStrategy === strategy.name ? editForm : null}
            saving={saving}
            onExpand={handleExpand}
            onEdit={handleEdit}
            onCancelEdit={handleCancelEdit}
            onSave={handleSave}
            onDelete={handleDelete}
            onClone={handleClone}
            onUpdateField={updateEditForm}
          />
        ))}
      </div>

      {/* Empty state */}
      {strategies.length === 0 && (
        <div className="text-center py-20 text-gray-500 font-mono">
          No strategies configured. Click "Add Strategy" to create one.
        </div>
      )}
    </div>
  )
}

export default Strategies

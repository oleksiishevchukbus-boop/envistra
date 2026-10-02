import { useState, useEffect } from 'react'
import { api } from '../api/client'

function Environment() {
  const [config, setConfig] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [expandedSection, setExpandedSection] = useState('revenue')

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      setLoading(true)
      const data = await api.getEnvironment()
      setConfig(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setError(null)
      setSuccess(null)
      await api.updateEnvironment(config)
      setSuccess('Configuration saved successfully')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  // Reload re-reads config/environment.json from disk, discarding unsaved edits.
  // It replaces the old "Reset Defaults": there are no Python defaults any more,
  // the JSON file is the only source.
  const handleReload = async () => {
    if (!confirm('Reload configuration from disk? Unsaved changes will be lost.')) return

    try {
      setSaving(true)
      setError(null)
      await api.reloadEnvironment()
      await loadConfig()
      setSuccess('Configuration reloaded from disk')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const updateConfig = (section, key, value) => {
    setConfig(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }))
  }

  const updatePenaltyTier = (index, key, value) => {
    setConfig(prev => ({
      ...prev,
      quota_manager: {
        ...prev.quota_manager,
        penalty_tiers: prev.quota_manager.penalty_tiers.map((tier, i) =>
          i === index ? { ...tier, [key]: value } : tier
        )
      }
    }))
  }

  const addPenaltyTier = () => {
    setConfig(prev => ({
      ...prev,
      quota_manager: {
        ...prev.quota_manager,
        penalty_tiers: [
          ...prev.quota_manager.penalty_tiers.slice(0, -1),
          { until_step: prev.quota_manager.penalty_tiers.length * 5, price: 3.0, description: 'New tier' },
          prev.quota_manager.penalty_tiers[prev.quota_manager.penalty_tiers.length - 1]
        ]
      }
    }))
  }

  const removePenaltyTier = (index) => {
    if (config.quota_manager.penalty_tiers.length <= 1) return
    setConfig(prev => ({
      ...prev,
      quota_manager: {
        ...prev.quota_manager,
        penalty_tiers: prev.quota_manager.penalty_tiers.filter((_, i) => i !== index)
      }
    }))
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
    )
  }

  if (!config) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="text-center py-20 text-red-400">Failed to load configuration</div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-mono font-semibold text-gray-100">Environment</h1>
          <p className="text-sm text-gray-500 mt-1">The regulatory regime every company operates in — config/environment.json</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 text-sm font-mono bg-eco-500 text-navy-950 rounded hover:bg-eco-400 transition-colors disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
          <button
            onClick={handleReload}
            disabled={saving}
            className="px-4 py-2 text-sm font-mono bg-navy-800 text-gray-300 rounded hover:bg-navy-700 transition-colors disabled:opacity-50"
          >
            Reload from Disk
          </button>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded text-red-400 text-sm font-mono">
          {error}
          <button onClick={() => setError(null)} className="ml-4 underline">Dismiss</button>
        </div>
      )}
      {success && (
        <div className="mb-6 p-4 bg-eco-500/10 border border-eco-500/30 rounded text-eco-400 text-sm font-mono">
          {success}
        </div>
      )}

      {/* Configuration Sections */}
      <div className="space-y-4">
        {/* Revenue Calculator */}
        <div className="bg-navy-900/80 rounded-lg border border-primary-800/50 overflow-hidden">
          <button
            onClick={() => setExpandedSection(expandedSection === 'revenue' ? null : 'revenue')}
            className="w-full flex items-center justify-between p-4 hover:bg-navy-800/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-fin-400" />
              <h3 className="font-mono text-gray-200">Revenue Calculator</h3>
            </div>
            <svg
              className={`w-5 h-5 text-gray-500 transition-transform ${expandedSection === 'revenue' ? 'rotate-180' : ''}`}
              fill="none" viewBox="0 0 24 24" stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {expandedSection === 'revenue' && (
            <div className="p-6 border-t border-primary-800/50 bg-navy-950/50">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-mono text-gray-500 mb-1">Approach</label>
                  <select
                    value={config.revenue_calculator.approach}
                    onChange={(e) => updateConfig('revenue_calculator', 'approach', e.target.value)}
                    className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm"
                  >
                    <option value="industry_based">Industry Based</option>
                    <option value="competitive_industry_based">Competitive Industry Based</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-mono text-gray-500 mb-1">Competition Influence</label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.05"
                    value={config.revenue_calculator.competition_influence}
                    onChange={(e) => updateConfig('revenue_calculator', 'competition_influence', parseFloat(e.target.value))}
                    className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm"
                  />
                  <p className="text-[10px] text-gray-600 mt-1">0 = no effect, 1 = fully competitive</p>
                </div>
                <div>
                  <label className="block text-xs font-mono text-gray-500 mb-1">Fin. Efficiency Impact Multiplier</label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    value={config.revenue_calculator.fin_eff_impact_multiplier}
                    onChange={(e) => updateConfig('revenue_calculator', 'fin_eff_impact_multiplier', parseFloat(e.target.value))}
                    className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Pollution Calculator */}
        <div className="bg-navy-900/80 rounded-lg border border-primary-800/50 overflow-hidden">
          <button
            onClick={() => setExpandedSection(expandedSection === 'pollution' ? null : 'pollution')}
            className="w-full flex items-center justify-between p-4 hover:bg-navy-800/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-eco-400" />
              <h3 className="font-mono text-gray-200">Pollution Calculator</h3>
            </div>
            <svg
              className={`w-5 h-5 text-gray-500 transition-transform ${expandedSection === 'pollution' ? 'rotate-180' : ''}`}
              fill="none" viewBox="0 0 24 24" stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {expandedSection === 'pollution' && (
            <div className="p-6 border-t border-primary-800/50 bg-navy-950/50">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-mono text-gray-500 mb-1">Approach</label>
                  <select
                    value={config.pollution_calculator.approach}
                    onChange={(e) => updateConfig('pollution_calculator', 'approach', e.target.value)}
                    className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm"
                  >
                    <option value="industry_based">Industry Based</option>
                    <option value="company_based">Company Based</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-mono text-gray-500 mb-1">Env. Efficiency Impact Multiplier</label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    value={config.pollution_calculator.env_eff_impact_multiplier}
                    onChange={(e) => updateConfig('pollution_calculator', 'env_eff_impact_multiplier', parseFloat(e.target.value))}
                    className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm"
                  />
                  <p className="text-[10px] text-gray-600 mt-1">At 1.0, eco-efficiency investments directly reduce pollution</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Quota Manager */}
        <div className="bg-navy-900/80 rounded-lg border border-primary-800/50 overflow-hidden">
          <button
            onClick={() => setExpandedSection(expandedSection === 'quota' ? null : 'quota')}
            className="w-full flex items-center justify-between p-4 hover:bg-navy-800/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-primary-400" />
              <h3 className="font-mono text-gray-200">Quota Manager</h3>
            </div>
            <svg
              className={`w-5 h-5 text-gray-500 transition-transform ${expandedSection === 'quota' ? 'rotate-180' : ''}`}
              fill="none" viewBox="0 0 24 24" stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {expandedSection === 'quota' && (
            <div className="p-6 border-t border-primary-800/50 bg-navy-950/50 space-y-6">
              {/* Basic params */}
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-mono text-gray-500 mb-1">Approach</label>
                  <select
                    value={config.quota_manager.approach}
                    onChange={(e) => updateConfig('quota_manager', 'approach', e.target.value)}
                    className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm"
                  >
                    <option value="expenses_based">Expenses Based</option>
                    <option value="historical_pollution_based">Historical Pollution Based</option>
                    <option value="improvement_rewarding">Improvement Rewarding</option>
                    <option value="grandfathered_with_tightening">Grandfathered with Tightening</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-mono text-gray-500 mb-1">Quota Cap Decreaser</label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.005"
                    value={config.quota_manager.quota_cap_decreaser}
                    onChange={(e) => updateConfig('quota_manager', 'quota_cap_decreaser', parseFloat(e.target.value))}
                    className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm"
                  />
                  <p className="text-[10px] text-gray-600 mt-1">Cap is multiplied by this each year</p>
                </div>
                <div>
                  <label className="block text-xs font-mono text-gray-500 mb-1">Linear Reduction Factor</label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.0025"
                    value={config.quota_manager.linear_reduction_factor}
                    onChange={(e) => updateConfig('quota_manager', 'linear_reduction_factor', parseFloat(e.target.value))}
                    className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm"
                  />
                  <p className="text-[10px] text-gray-600 mt-1">Annual linear reduction in total cap</p>
                </div>
              </div>

              {/* Approach-specific params */}
              {config.quota_manager.approach === 'improvement_rewarding' && (
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-mono text-gray-500 mb-1">Reward Pool Share</label>
                    <input
                      type="number"
                      min="0"
                      max="1"
                      step="0.05"
                      value={config.quota_manager.reward_pool_share ?? 0.3}
                      onChange={(e) => updateConfig('quota_manager', 'reward_pool_share', parseFloat(e.target.value))}
                      className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm"
                    />
                    <p className="text-[10px] text-gray-600 mt-1">0 = all equal base, 1 = all reward-based</p>
                  </div>
                </div>
              )}

              {config.quota_manager.approach === 'grandfathered_with_tightening' && (
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-mono text-gray-500 mb-1">Tightening Strength</label>
                    <input
                      type="number"
                      min="0"
                      max="1"
                      step="0.05"
                      value={config.quota_manager.tightening_strength ?? 0.5}
                      onChange={(e) => updateConfig('quota_manager', 'tightening_strength', parseFloat(e.target.value))}
                      className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm"
                    />
                    <p className="text-[10px] text-gray-600 mt-1">0 = no intensity adjustment, 1 = full adjustment</p>
                  </div>
                </div>
              )}

              {/* Penalty Tiers */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-mono text-gray-400">Penalty Tiers</h4>
                  <button
                    onClick={addPenaltyTier}
                    className="px-3 py-1 text-xs font-mono bg-navy-800 text-gray-300 rounded hover:bg-navy-700 transition-colors"
                  >
                    + Add Tier
                  </button>
                </div>
                <div className="space-y-2">
                  {config.quota_manager.penalty_tiers.map((tier, index) => (
                    <div key={index} className="flex items-center gap-3 p-3 bg-navy-800/50 rounded">
                      <div className="flex-1 grid grid-cols-3 gap-3">
                        <div>
                          <label className="block text-[10px] font-mono text-gray-600 mb-1">Until Step</label>
                          <input
                            type={tier.until_step === 'inf' ? 'text' : 'number'}
                            value={tier.until_step}
                            onChange={(e) => {
                              const val = e.target.value === 'inf' ? 'inf' : parseInt(e.target.value) || 0
                              updatePenaltyTier(index, 'until_step', val)
                            }}
                            className="w-full px-2 py-1 bg-navy-900 border border-primary-800/50 rounded text-gray-200 font-mono text-sm"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] font-mono text-gray-600 mb-1">Price per Unit</label>
                          <input
                            type="number"
                            min="0"
                            step="0.25"
                            value={tier.price}
                            onChange={(e) => updatePenaltyTier(index, 'price', parseFloat(e.target.value))}
                            className="w-full px-2 py-1 bg-navy-900 border border-primary-800/50 rounded text-gray-200 font-mono text-sm"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] font-mono text-gray-600 mb-1">Description</label>
                          <input
                            type="text"
                            value={tier.description}
                            onChange={(e) => updatePenaltyTier(index, 'description', e.target.value)}
                            className="w-full px-2 py-1 bg-navy-900 border border-primary-800/50 rounded text-gray-200 font-mono text-sm"
                          />
                        </div>
                      </div>
                      {config.quota_manager.penalty_tiers.length > 1 && (
                        <button
                          onClick={() => removePenaltyTier(index)}
                          className="p-1 text-red-400 hover:text-red-300 transition-colors"
                        >
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Info panel */}
      <div className="mt-8 p-4 bg-navy-900/40 rounded-lg border border-primary-800/30">
        <p className="text-xs font-mono text-gray-500">
          Changes take effect on the next simulation run. Environment settings control how revenue, pollution, and quota penalties are calculated for all agents.
        </p>
      </div>
    </div>
  )
}

export default Environment

import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api } from '../api/client'
import { useSimulationWebSocket } from '../api/websocket'

function Dashboard() {
  const navigate = useNavigate()
  const [steps, setSteps] = useState(20)
  const [isLoading, setIsLoading] = useState(false)
  const [simulations, setSimulations] = useState([])
  const [loadingSimulations, setLoadingSimulations] = useState(true)
  const [activeRunId, setActiveRunId] = useState(null)
  const [strategies, setStrategies] = useState([])
  const [companies, setCompanies] = useState(null)
  const [seed, setSeed] = useState('')

  const { progress, status, plots, actualRunId } = useSimulationWebSocket(activeRunId)

  // Load simulations and strategies
  useEffect(() => {
    loadSimulations()
    loadStrategies()
    loadCompanies()
  }, [])

  // The run list is stale the moment a run finishes, so refresh it then.
  useEffect(() => {
    if (status === 'completed') {
      setIsLoading(false)
      loadSimulations()
    }
  }, [status])

  const loadSimulations = async () => {
    try {
      const data = await api.listSimulations()
      setSimulations(data.simulations || [])
    } catch (error) {
      console.error('Failed to load simulations:', error)
    } finally {
      setLoadingSimulations(false)
    }
  }

  const loadCompanies = async () => {
    try {
      setCompanies(await api.listCompanies())
    } catch (error) {
      console.error('Failed to load companies:', error)
    }
  }

  const loadStrategies = async () => {
    try {
      const data = await api.listStrategies()
      setStrategies(data.strategies || [])
    } catch (error) {
      console.error('Failed to load strategies:', error)
    }
  }

  const handleDeleteSimulation = async (e, runId) => {
    e.stopPropagation()
    try {
      await api.deleteSimulation(runId)
      setSimulations(prev => prev.filter(s => s.run_id !== runId))
    } catch (error) {
      console.error('Failed to delete simulation:', error)
    }
  }

  const handleRunSimulation = async () => {
    setIsLoading(true)
    try {
      const parsedSeed = seed.trim() === '' ? null : Number(seed)
      const response = await api.createSimulation(steps, parsedSeed)
      setActiveRunId(response.run_id)
    } catch (error) {
      console.error('Failed to start simulation:', error)
      setIsLoading(false)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const isRunning = activeRunId && (status === 'running' || status === 'connected')

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Simulation Launcher */}
        <div className="lg:col-span-2">
          <div className="relative">
            {/* Panel frame */}
            <div className="absolute -inset-px bg-gradient-to-b from-primary-700/30 to-transparent rounded-lg" />

            <div className="relative bg-navy-900/80 backdrop-blur rounded-lg border border-primary-800/50 overflow-hidden">
              {/* Panel header */}
              <div className="px-6 py-4 border-b border-primary-800/50 bg-navy-900/50">
                <div className="flex items-center gap-3">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-eco-400/80" />
                    <div className="w-3 h-3 rounded-full bg-fin-400/80" />
                    <div className="w-3 h-3 rounded-full bg-primary-400/80" />
                  </div>
                  <h2 className="font-mono text-sm uppercase tracking-wider text-gray-300">
                    Simulation Control
                  </h2>
                </div>
              </div>

              <div className="p-6 space-y-8">
                {/* Steps Configuration */}
                <div className="space-y-4">
                  <div className="flex items-baseline justify-between">
                    <label className="text-xs font-mono uppercase tracking-wider text-gray-400">
                      Simulation Steps
                    </label>
                    <div className="flex items-baseline gap-2">
                      <span className="text-4xl font-mono font-semibold text-eco-400 tabular-nums">
                        {steps}
                      </span>
                      <span className="text-sm text-gray-500 font-mono">steps</span>
                    </div>
                  </div>

                  {/* Custom slider */}
                  <div className="relative h-12 flex items-center">
                    <div className="absolute inset-x-0 h-2 bg-navy-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-eco-400/80 to-eco-500 transition-all duration-150"
                        style={{ width: `${((steps - 1) / 49) * 100}%` }}
                      />
                    </div>
                    <input
                      type="range"
                      min="1"
                      max="50"
                      value={steps}
                      onChange={(e) => setSteps(Number(e.target.value))}
                      disabled={isRunning}
                      className="absolute inset-x-0 w-full h-12 opacity-0 cursor-pointer disabled:cursor-not-allowed"
                    />
                    {/* Slider thumb indicator */}
                    <div
                      className="absolute w-5 h-5 bg-eco-400 rounded-full shadow-lg shadow-eco-400/30 border-2 border-navy-950 transition-all duration-150 pointer-events-none"
                      style={{ left: `calc(${((steps - 1) / 49) * 100}% - 10px)` }}
                    />
                  </div>

                  {/* Scale markers */}
                  <div className="flex justify-between text-[10px] font-mono text-gray-600 px-1">
                    <span>1</span>
                    <span>10</span>
                    <span>20</span>
                    <span>30</span>
                    <span>40</span>
                    <span>50</span>
                  </div>
                </div>

                {/* Seed */}
                <div className="space-y-2">
                  <label className="text-xs font-mono uppercase tracking-wider text-gray-400">
                    Random Seed
                  </label>
                  <input
                    type="number"
                    value={seed}
                    onChange={(e) => setSeed(e.target.value)}
                    disabled={isRunning}
                    placeholder="leave empty for an unrepeatable run"
                    className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
                  />
                  <p className="text-[11px] font-mono text-gray-500">
                    A seed makes the run reproducible; it is recorded in run_config.json.
                  </p>
                </div>

                {/* Info grid */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-navy-950/50 rounded p-4 border border-primary-900/30">
                    <div className="text-[10px] font-mono uppercase tracking-wider text-gray-500 mb-1">
                      Year Range
                    </div>
                    <div className="font-mono text-gray-200">
                      2010 — {2010 + steps - 1}
                    </div>
                  </div>
                  <div className="bg-navy-950/50 rounded p-4 border border-primary-900/30">
                    <div className="text-[10px] font-mono uppercase tracking-wider text-gray-500 mb-1">
                      Agents
                    </div>
                    <div className="font-mono text-gray-200">
                      {companies ? `${companies.enabled} simulated` : '—'}
                    </div>
                  </div>
                  <div className="bg-navy-950/50 rounded p-4 border border-primary-900/30">
                    <div className="text-[10px] font-mono uppercase tracking-wider text-gray-500 mb-1">
                      Charted
                    </div>
                    <div className="font-mono text-gray-200">
                      {companies ? `${companies.plotted} of ${companies.total}` : '—'}
                    </div>
                  </div>
                </div>

                {/* Progress display */}
                {isRunning && progress && (
                  <div className="space-y-3 animate-slide-up">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-mono text-gray-400">{progress.message}</span>
                      {progress.progress != null && (
                        <span className="font-mono text-eco-400">
                          {Math.round(progress.progress)}%
                        </span>
                      )}
                    </div>
                    {progress.progress != null && (
                      <div className="h-2 bg-navy-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-eco-400 to-eco-500 transition-all duration-300"
                          style={{ width: `${progress.progress}%` }}
                        />
                      </div>
                    )}
                    {plots.length > 0 && (
                      <div className="text-xs font-mono text-gray-500">
                        Generated: {plots.length} plots
                      </div>
                    )}
                  </div>
                )}

                {/* Completion message */}
                {status === 'completed' && actualRunId && (
                  <div className="p-4 bg-eco-400/10 border border-eco-400/30 rounded animate-slide-up">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <svg className="w-5 h-5 text-eco-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="font-mono text-eco-400">
                          Simulation complete!
                        </span>
                      </div>
                      <Link
                        to={`/simulations/${actualRunId}`}
                        className="px-4 py-2 text-xs font-mono uppercase tracking-wider bg-eco-400 text-navy-950 rounded hover:bg-eco-300 transition-colors"
                      >
                        View Results
                      </Link>
                    </div>
                  </div>
                )}

                {/* Run button */}
                <button
                  onClick={handleRunSimulation}
                  disabled={isRunning || isLoading}
                  className={`
                    w-full py-4 px-6 rounded font-mono uppercase tracking-wider text-sm
                    transition-all duration-300 relative overflow-hidden group
                    ${isRunning
                      ? 'bg-navy-800 text-gray-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-eco-500 to-eco-600 text-navy-950 hover:from-eco-400 hover:to-eco-500 hover:shadow-lg hover:shadow-eco-500/25'
                    }
                  `}
                >
                  {isRunning ? (
                    <span className="flex items-center justify-center gap-3">
                      <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Running Simulation...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-3">
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Run Strategy Comparison
                    </span>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Runs */}
        <div className="lg:col-span-1">
          <div className="relative">
            <div className="absolute -inset-px bg-gradient-to-b from-primary-700/20 to-transparent rounded-lg" />

            <div className="relative bg-navy-900/60 backdrop-blur rounded-lg border border-primary-800/50 overflow-hidden">
              <div className="px-5 py-4 border-b border-primary-800/50 bg-navy-900/50">
                <h2 className="font-mono text-sm uppercase tracking-wider text-gray-300">
                  Recent Runs
                </h2>
              </div>

              <div className="p-4 max-h-[520px] overflow-y-auto">
                {loadingSimulations ? (
                  <div className="py-8 text-center">
                    <div className="w-6 h-6 border-2 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto" />
                  </div>
                ) : simulations.length === 0 ? (
                  <div className="py-8 text-center text-gray-500 font-mono text-sm">
                    No simulations yet
                  </div>
                ) : (
                  <div className="space-y-2">
                    {simulations.map((sim, index) => (
                      <button
                        key={sim.run_id}
                        onClick={() => navigate(`/simulations/${sim.run_id}`)}
                        className="w-full text-left p-3 rounded bg-navy-950/50 border border-primary-900/30 hover:border-primary-700/50 hover:bg-navy-900/50 transition-all group"
                        style={{ animationDelay: `${index * 50}ms` }}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0 flex-1">
                            <div className="text-sm font-mono text-gray-300 truncate group-hover:text-eco-400 transition-colors">
                              {sim.run_id.split('_').slice(0, 1).join('_')}
                            </div>
                            <div className="text-[10px] font-mono text-gray-600 mt-1">
                              {formatDate(sim.created_at)}
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {sim.steps && (
                              <span className="text-[10px] font-mono text-gray-500 bg-navy-800 px-2 py-0.5 rounded">
                                {sim.steps}s
                              </span>
                            )}
                            <span className={`w-2 h-2 rounded-full ${
                              sim.status === 'completed' ? 'bg-eco-400' :
                              sim.status === 'running' ? 'bg-fin-400 animate-pulse' :
                              'bg-gray-600'
                            }`} />
                            <button
                              onClick={(e) => handleDeleteSimulation(e, sim.run_id)}
                              className="p-1 text-gray-600 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                            >
                              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            </button>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Strategy info panel */}
      <div className="mt-8">
        <div className="relative">
          <div className="absolute -inset-px bg-gradient-to-r from-eco-400/10 via-transparent to-fin-400/10 rounded-lg" />

          <div className="relative bg-navy-900/40 backdrop-blur rounded-lg border border-primary-800/30 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-mono text-xs uppercase tracking-wider text-gray-500">
                Comparing Strategies
              </h3>
              <Link
                to="/strategies"
                className="text-xs font-mono text-primary-400 hover:text-primary-300 transition-colors"
              >
                Edit Strategies &rarr;
              </Link>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {strategies.map((strategy) => (
                <div key={strategy.name} className="flex items-start gap-3">
                  <div
                    className="w-3 h-3 rounded-full mt-1 flex-shrink-0"
                    style={{ backgroundColor: strategy.color }}
                  />
                  <div>
                    <div className="font-mono text-sm text-gray-300">{strategy.name}</div>
                    <div className="text-[10px] text-gray-600 mt-0.5">{strategy.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api/client'

const CATEGORY_ORDER = ['basics', 'pollution', 'quota', 'quota_trade', 'ratios', 'efficiency', 'other']

const CATEGORY_LABELS = {
  basics: 'Basic Metrics',
  pollution: 'Pollution',
  quota: 'Quota',
  quota_trade: 'Quota Trading',
  ratios: 'Ratios',
  efficiency: 'Efficiency',
  other: 'Other'
}

const CATEGORY_COLORS = {
  basics: 'eco',
  pollution: 'red',
  quota: 'blue',
  quota_trade: 'purple',
  ratios: 'amber',
  efficiency: 'teal',
  other: 'gray'
}

function SimulationResults() {
  const { runId } = useParams()
  const [simulation, setSimulation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeCategory, setActiveCategory] = useState(null)
  const [lightboxImage, setLightboxImage] = useState(null)

  useEffect(() => {
    loadSimulation()
  }, [runId])

  const loadSimulation = async () => {
    try {
      setLoading(true)
      const data = await api.getSimulation(runId)
      setSimulation(data)
      // Set first category with images as active
      const categories = getCategories(data.images)
      if (categories.length > 0) {
        setActiveCategory(categories[0])
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getCategories = (images) => {
    const cats = [...new Set(images.map(img => img.category))]
    return CATEGORY_ORDER.filter(c => cats.includes(c))
  }

  const getImagesByCategory = (category) => {
    if (!simulation) return []
    return simulation.images.filter(img => img.category === category)
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="flex flex-col items-center justify-center gap-4">
          <div className="w-12 h-12 border-3 border-primary-600 border-t-eco-400 rounded-full animate-spin" />
          <p className="font-mono text-gray-500">Loading simulation data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6 text-center">
          <p className="font-mono text-red-400">{error}</p>
          <Link to="/" className="mt-4 inline-block text-sm font-mono text-gray-400 hover:text-gray-200">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  if (!simulation) return null

  const categories = getCategories(simulation.images)

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-sm font-mono text-gray-500 hover:text-eco-400 transition-colors mb-4"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Dashboard
        </Link>

        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <h1 className="font-serif text-2xl font-semibold text-gray-100 mb-2">
              {runId.split('_').slice(0, 1).join(' ')}
            </h1>
            <p className="font-mono text-sm text-gray-500">
              {formatDate(simulation.created_at)}
            </p>
          </div>

          {/* Downloads */}
          <div className="flex items-center gap-3">
            {simulation.config_available && (
              <a
                href={api.getConfigUrl(runId)}
                download
                className="px-4 py-2 text-xs font-mono uppercase tracking-wider text-gray-400 border border-primary-800 hover:border-eco-400/50 hover:text-eco-400 rounded transition-all"
              >
                Config JSON
              </a>
            )}
            {simulation.history_available && (
              <a
                href={api.getHistoryUrl(runId)}
                download
                className="px-4 py-2 text-xs font-mono uppercase tracking-wider text-gray-400 border border-primary-800 hover:border-eco-400/50 hover:text-eco-400 rounded transition-all"
              >
                History CSV
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-navy-900/60 rounded-lg border border-primary-800/50 p-4">
          <div className="text-[10px] font-mono uppercase tracking-wider text-gray-500 mb-1">Status</div>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${
              simulation.status === 'completed' ? 'bg-eco-400' : 'bg-fin-400'
            }`} />
            <span className="font-mono text-gray-200 capitalize">{simulation.status}</span>
          </div>
        </div>
        <div className="bg-navy-900/60 rounded-lg border border-primary-800/50 p-4">
          <div className="text-[10px] font-mono uppercase tracking-wider text-gray-500 mb-1">Steps</div>
          <div className="font-mono text-gray-200">{simulation.steps || 'N/A'}</div>
        </div>
        <div className="bg-navy-900/60 rounded-lg border border-primary-800/50 p-4">
          <div className="text-[10px] font-mono uppercase tracking-wider text-gray-500 mb-1">Images</div>
          <div className="font-mono text-gray-200">{simulation.images.length}</div>
        </div>
        <div className="bg-navy-900/60 rounded-lg border border-primary-800/50 p-4">
          <div className="text-[10px] font-mono uppercase tracking-wider text-gray-500 mb-1">Year Range</div>
          <div className="font-mono text-gray-200">
            {simulation.start_year} — {simulation.start_year + (simulation.steps || 20) - 1}
          </div>
        </div>
      </div>

      {/* Category tabs */}
      <div className="mb-6 overflow-x-auto">
        <div className="flex gap-2 min-w-max pb-2">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setActiveCategory(category)}
              className={`px-4 py-2 text-xs font-mono uppercase tracking-wider rounded transition-all ${
                activeCategory === category
                  ? 'bg-eco-400/20 text-eco-400 border border-eco-400/30'
                  : 'text-gray-500 border border-primary-800/50 hover:border-primary-700 hover:text-gray-300'
              }`}
            >
              {CATEGORY_LABELS[category]} ({getImagesByCategory(category).length})
            </button>
          ))}
        </div>
      </div>

      {/* Image grid */}
      {activeCategory && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {getImagesByCategory(activeCategory).map((image, index) => (
            <button
              key={image.filename}
              onClick={() => setLightboxImage(image)}
              className="group relative bg-navy-900/60 rounded-lg border border-primary-800/50 overflow-hidden image-card text-left"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="aspect-[12/5] bg-navy-950 overflow-hidden">
                {image.previewable === false ? (
                  <div className="w-full h-full flex flex-col items-center justify-center gap-2 text-gray-500">
                    <span className="px-2 py-1 text-xs font-mono border border-primary-800 rounded">PDF</span>
                    <span className="text-[11px] font-mono">click to open</span>
                  </div>
                ) : (
                  <img
                    src={image.path}
                    alt={image.name}
                    className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500"
                    loading="lazy"
                  />
                )}
              </div>
              <div className="p-4 border-t border-primary-800/50">
                <h3 className="font-mono text-sm text-gray-300 group-hover:text-eco-400 transition-colors">
                  {image.name}
                </h3>
                {Object.keys(image.formats || {}).length > 1 && (
                  <p className="mt-1 text-[10px] font-mono uppercase text-gray-600">
                    {Object.keys(image.formats).join(' · ')}
                  </p>
                )}
              </div>
              {/* Hover overlay */}
              <div className="absolute inset-0 bg-eco-400/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
            </button>
          ))}
        </div>
      )}

      {/* Lightbox */}
      {lightboxImage && (
        <div
          className="fixed inset-0 z-50 bg-navy-950/95 backdrop-blur-sm flex items-center justify-center p-4 md:p-8"
          onClick={() => setLightboxImage(null)}
        >
          <div className="relative max-w-6xl w-full animate-slide-up" onClick={e => e.stopPropagation()}>
            {/* Close button */}
            <button
              onClick={() => setLightboxImage(null)}
              className="absolute -top-12 right-0 p-2 text-gray-500 hover:text-white transition-colors"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Image */}
            <div className="bg-navy-900 rounded-lg border border-primary-800/50 overflow-hidden">
              <div className="bg-white">
                {lightboxImage.previewable === false ? (
                  <iframe
                    src={lightboxImage.path}
                    title={lightboxImage.name}
                    className="w-full h-[70vh]"
                  />
                ) : (
                  <img
                    src={lightboxImage.path}
                    alt={lightboxImage.name}
                    className="w-full h-auto"
                  />
                )}
              </div>
              <div className="p-4 border-t border-primary-800/50 flex items-center justify-between">
                <h3 className="font-mono text-gray-300">{lightboxImage.name}</h3>
                {/* One link per format the chart was written in; older
                    responses without `formats` fall back to the preview file. */}
                <div className="flex gap-2">
                  {Object.entries(
                    lightboxImage.formats && Object.keys(lightboxImage.formats).length
                      ? lightboxImage.formats
                      : { [lightboxImage.filename.split('.').pop()]: lightboxImage.path }
                  ).map(([ext, url]) => (
                    <a
                      key={ext}
                      href={url}
                      download={`${lightboxImage.name}.${ext}`}
                      className="px-3 py-1.5 text-xs font-mono uppercase tracking-wider text-gray-400 border border-primary-800 hover:border-eco-400/50 hover:text-eco-400 rounded transition-all"
                      onClick={e => e.stopPropagation()}
                    >
                      {ext}
                    </a>
                  ))}
                </div>
              </div>
            </div>

            {/* Navigation hint */}
            <p className="text-center mt-4 text-xs font-mono text-gray-600">
              Click outside to close
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default SimulationResults

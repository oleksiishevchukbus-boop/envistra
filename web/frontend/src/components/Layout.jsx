import { Outlet, Link, useLocation } from 'react-router-dom'

function Layout() {
  const location = useLocation()
  const isHome = location.pathname === '/'
  const isStrategies = location.pathname === '/strategies'
  const isCompanies = location.pathname === '/companies'
  const isEnvironment = location.pathname === '/environment'
  const isSettings = location.pathname === '/settings'
  const isAbout = location.pathname === '/about'

  return (
    <div className="min-h-screen bg-navy-950 relative overflow-hidden flex flex-col">
      {/* Scan line overlay */}
      <div
        className="fixed inset-0 pointer-events-none z-50 opacity-[0.015]"
        style={{
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.03) 2px, rgba(255,255,255,0.03) 4px)',
        }}
      />

      {/* Subtle grid pattern */}
      <div
        className="fixed inset-0 pointer-events-none opacity-[0.02]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(45, 212, 191, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(45, 212, 191, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
        }}
      />

      {/* Header */}
      <header className="relative z-10 border-b border-primary-900/30">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo/Title */}
            <Link to="/" className="flex items-center gap-4 group">
              <div className="relative">
                <div className="w-10 h-10 rounded bg-gradient-to-br from-eco-400 to-eco-600 flex items-center justify-center">
                  <svg className="w-6 h-6 text-navy-950" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M12 3v18M3 12h18M7 7l10 10M17 7L7 17" strokeLinecap="round"/>
                  </svg>
                </div>
                <div className="absolute -inset-1 rounded bg-eco-400/20 blur-sm group-hover:bg-eco-400/30 transition-colors -z-10" />
              </div>
              <div>
                <h1 className="font-serif text-xl font-semibold text-gray-100 tracking-tight">
                  ENVISTRA
                </h1>
                <p className="text-[10px] uppercase tracking-[0.2em] text-primary-400 font-mono">
                  Strategy Comparison System
                </p>
              </div>
            </Link>

            {/* Nav */}
            <nav className="flex items-center gap-1">
              <Link
                to="/"
                className={`px-4 py-2 text-sm font-mono uppercase tracking-wider transition-all ${
                  isHome
                    ? 'text-eco-400 bg-eco-400/10 border border-eco-400/30'
                    : 'text-gray-400 hover:text-gray-200 border border-transparent hover:border-primary-800'
                }`}
              >
                Dashboard
              </Link>
              <Link
                to="/strategies"
                className={`px-4 py-2 text-sm font-mono uppercase tracking-wider transition-all ${
                  isStrategies
                    ? 'text-fin-400 bg-fin-400/10 border border-fin-400/30'
                    : 'text-gray-400 hover:text-gray-200 border border-transparent hover:border-primary-800'
                }`}
              >
                Strategies
              </Link>
              <Link
                to="/companies"
                className={`px-4 py-2 text-sm font-mono uppercase tracking-wider transition-all ${
                  isCompanies
                    ? 'text-amber-400 bg-amber-400/10 border border-amber-400/30'
                    : 'text-gray-400 hover:text-gray-200 border border-transparent hover:border-primary-800'
                }`}
              >
                Companies
              </Link>
              <Link
                to="/environment"
                className={`px-4 py-2 text-sm font-mono uppercase tracking-wider transition-all ${
                  isEnvironment
                    ? 'text-primary-400 bg-primary-400/10 border border-primary-400/30'
                    : 'text-gray-400 hover:text-gray-200 border border-transparent hover:border-primary-800'
                }`}
              >
                Environment
              </Link>
              <Link
                to="/settings"
                className={`px-4 py-2 text-sm font-mono uppercase tracking-wider transition-all ${
                  isSettings
                    ? 'text-primary-400 bg-primary-400/10 border border-primary-400/30'
                    : 'text-gray-400 hover:text-gray-200 border border-transparent hover:border-primary-800'
                }`}
              >
                Settings
              </Link>
              <Link
                to="/about"
                className={`px-4 py-2 text-sm font-mono uppercase tracking-wider transition-all ${
                  isAbout
                    ? 'text-eco-400 bg-eco-400/10 border border-eco-400/30'
                    : 'text-gray-400 hover:text-gray-200 border border-transparent hover:border-primary-800'
                }`}
              >
                About
              </Link>
              <a
                href="/api/simulations"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 text-sm font-mono uppercase tracking-wider text-gray-500 hover:text-gray-300 border border-transparent hover:border-primary-800 transition-all"
              >
                API
              </a>
            </nav>
          </div>
        </div>

        {/* Decorative line */}
        <div className="h-px bg-gradient-to-r from-transparent via-eco-400/40 to-transparent" />
      </header>

      {/* Main content */}
      <main className="relative z-10 flex-1">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-primary-900/30 mt-auto">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between text-xs font-mono text-gray-600">
            <span>ENVISTRA · Mesa Agent-Based Model · Environmental Economics Research</span>
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-eco-400 animate-pulse" />
              System Ready
            </span>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout

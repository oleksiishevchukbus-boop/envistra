import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import SimulationResults from './pages/SimulationResults'
import Strategies from './pages/Strategies'
import Companies from './pages/Companies'
import Environment from './pages/Environment'
import Settings from './pages/Settings'
import About from './pages/About'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="strategies" element={<Strategies />} />
        <Route path="companies" element={<Companies />} />
        <Route path="environment" element={<Environment />} />
        <Route path="settings" element={<Settings />} />
        <Route path="about" element={<About />} />
        <Route path="simulations/:runId" element={<SimulationResults />} />
      </Route>
    </Routes>
  )
}

export default App

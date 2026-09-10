import './App.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Dashboard } from './pages/Dashboard'
import { Jobs } from './pages/Jobs'
import { RunDetails } from './pages/RunDetails'

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <header className="app-header">
          <h1>Job Search System</h1>
          <nav className="app-nav">
            <a href="/">Dashboard</a>
            <a href="/jobs">Jobs</a>
          </nav>
        </header>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/runs/:runId" element={<RunDetails />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>Job Search System v0.0.1</p>
        </footer>
      </div>
    </BrowserRouter>
  )
}

export default App

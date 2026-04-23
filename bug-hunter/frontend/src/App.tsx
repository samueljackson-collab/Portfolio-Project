import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Navbar } from './components/Navbar'
import { Dashboard } from './pages/Dashboard'
import { Analyzer } from './pages/Analyzer'
import { ScanDetail } from './pages/ScanDetail'
import { Reports } from './pages/Reports'
import { ReportDetail } from './pages/ReportDetail'
import { Settings } from './pages/Settings'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analyze" element={<Analyzer />} />
            <Route path="/scan/:id" element={<ScanDetail />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/report/:id" element={<ReportDetail />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

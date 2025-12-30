import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import MissionIntake from './pages/MissionIntake';
import AnalysisResults from './pages/AnalysisResults';
import MissionHistory from './pages/MissionHistory';
import './index.css';

/**
 * CACI Mission Intake and Analysis Copilot
 * 
 * ESF-aligned accelerator for mission document analysis
 * with AI-assisted summarization, entity extraction, and risk classification.
 */
function App() {
  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<MissionIntake />} />
            <Route path="/analysis/:missionId" element={<AnalysisResults />} />
            <Route path="/history" element={<MissionHistory />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer style={{
          textAlign: 'center',
          padding: 'var(--spacing-lg)',
          borderTop: '1px solid var(--border-color)',
          background: 'var(--bg-primary)',
          color: 'var(--text-muted)',
          fontSize: '0.875rem'
        }}>
          <p>
            CACI Mission Intake and Analysis Copilot • ESF Accelerator Demo
          </p>
          <p style={{ fontSize: '0.75rem', marginTop: 'var(--spacing-sm)' }}>
            AI-assisted analysis powered by Hugging Face •
            Data persisted in PostgreSQL •
            Not for production use
          </p>
        </footer>
      </div>
    </Router>
  );
}

export default App;

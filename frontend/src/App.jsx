import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import MissionIntake from './pages/MissionIntake';
import AnalysisResults from './pages/AnalysisResults';
import MissionHistory from './pages/MissionHistory';
import KeyboardShortcutsModal from './components/KeyboardShortcutsModal';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import './index.css';

/**
 * Main app content with keyboard shortcuts enabled.
 */
function AppContent() {
  const [showShortcutsModal, setShowShortcutsModal] = useState(false);
  const location = useLocation();

  // Initialize keyboard shortcuts
  useKeyboardShortcuts({
    onShowHelp: () => setShowShortcutsModal(true),
  });

  // Close modal on ESC
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') {
        setShowShortcutsModal(false);
      }
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, []);

  return (
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
          Press <kbd style={{
            background: 'var(--bg-secondary)',
            padding: '0.125rem 0.375rem',
            borderRadius: '3px',
            border: '1px solid var(--border-color)',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.6875rem'
          }}>?</kbd> for shortcuts
        </p>
      </footer>

      {/* Keyboard Shortcuts Modal */}
      <KeyboardShortcutsModal
        isOpen={showShortcutsModal}
        onClose={() => setShowShortcutsModal(false)}
      />
    </div>
  );
}

/**
 * CACI Mission Intake and Analysis Copilot
 * 
 * ESF-aligned accelerator for mission document analysis
 * with AI-assisted summarization, entity extraction, and risk classification.
 */
function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;


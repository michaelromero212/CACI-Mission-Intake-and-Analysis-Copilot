import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUploader from '../components/FileUploader';
import TextInput from '../components/TextInput';
import { missionsApi, analysisApi } from '../api';

/**
 * Mission Intake page - upload files or submit text for analysis.
 */
export default function MissionIntake() {
    const navigate = useNavigate();
    const [selectedFile, setSelectedFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('file'); // 'file' or 'text'

    // Auto-analyze toggle with localStorage persistence
    const [autoAnalyze, setAutoAnalyze] = useState(() => {
        const saved = localStorage.getItem('autoAnalyze');
        return saved === 'true';
    });

    // Persist auto-analyze preference
    useEffect(() => {
        localStorage.setItem('autoAnalyze', autoAnalyze.toString());
    }, [autoAnalyze]);

    const handleFileSelect = (file) => {
        setSelectedFile(file);
        setError(null);
    };

    const handleFileUpload = async () => {
        if (!selectedFile) return;

        setIsLoading(true);
        setError(null);

        try {
            // Upload the file
            const mission = await missionsApi.uploadFile(selectedFile);

            // Auto-analyze if enabled
            if (autoAnalyze) {
                try {
                    await analysisApi.execute(mission.mission_id, true);
                } catch (analysisErr) {
                    console.warn('Auto-analysis failed:', analysisErr);
                    // Continue to navigation even if analysis fails
                }
            }

            // Navigate to analysis page
            navigate(`/analysis/${mission.mission_id}`);
        } catch (err) {
            console.error('Upload failed:', err);
            setError(err.response?.data?.detail || 'Failed to upload file. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleTextSubmit = async (content, sourceLabel) => {
        setIsLoading(true);
        setError(null);

        try {
            // Submit text
            const mission = await missionsApi.submitText(content, sourceLabel);

            // Auto-analyze if enabled
            if (autoAnalyze) {
                try {
                    await analysisApi.execute(mission.mission_id, true);
                } catch (analysisErr) {
                    console.warn('Auto-analysis failed:', analysisErr);
                    // Continue to navigation even if analysis fails
                }
            }

            // Navigate to analysis page
            navigate(`/analysis/${mission.mission_id}`);
        } catch (err) {
            console.error('Text submission failed:', err);
            setError(err.response?.data?.detail || 'Failed to submit text. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <div className="mb-lg">
                <h1>Mission Intake</h1>
                <p className="text-muted">
                    Upload mission documents or submit free-text for AI-assisted analysis.
                </p>
            </div>

            {/* Tab Navigation */}
            <div className="flex gap-md mb-lg">
                <button
                    className={`btn ${activeTab === 'file' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => setActiveTab('file')}
                >
                    📁 File Upload
                </button>
                <button
                    className={`btn ${activeTab === 'text' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => setActiveTab('text')}
                >
                    📝 Text Input
                </button>
            </div>

            {/* Auto-Analyze Toggle */}
            <div className="card mb-lg" style={{
                padding: 'var(--spacing-md)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: autoAnalyze ? 'rgba(46, 125, 50, 0.05)' : 'var(--bg-secondary)'
            }}>
                <div>
                    <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>
                        🚀 Auto-Analyze on Upload
                    </div>
                    <div className="text-muted" style={{ fontSize: '0.8125rem' }}>
                        Automatically run AI analysis after document upload
                    </div>
                </div>
                <label style={{
                    position: 'relative',
                    display: 'inline-block',
                    width: '48px',
                    height: '26px',
                    cursor: 'pointer'
                }}>
                    <input
                        type="checkbox"
                        checked={autoAnalyze}
                        onChange={(e) => setAutoAnalyze(e.target.checked)}
                        style={{ opacity: 0, width: 0, height: 0 }}
                    />
                    <span style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundColor: autoAnalyze ? 'var(--color-success)' : 'var(--border-color)',
                        borderRadius: '26px',
                        transition: 'background-color 0.2s'
                    }}>
                        <span style={{
                            position: 'absolute',
                            content: '""',
                            height: '20px',
                            width: '20px',
                            left: autoAnalyze ? '25px' : '3px',
                            bottom: '3px',
                            backgroundColor: 'white',
                            borderRadius: '50%',
                            transition: 'left 0.2s',
                            boxShadow: '0 1px 3px rgba(0,0,0,0.2)'
                        }} />
                    </span>
                </label>
            </div>

            {/* Error Display */}
            {error && (
                <div className="card mb-lg" style={{ borderColor: 'var(--color-error)', background: 'rgba(211, 47, 47, 0.05)' }}>
                    <div className="flex items-center gap-sm" style={{ color: 'var(--color-error)' }}>
                        <span>⚠️</span>
                        <span>{error}</span>
                    </div>
                </div>
            )}

            {/* Loading Overlay */}
            {isLoading && (
                <div className="card mb-lg text-center">
                    <div className="loading-spinner" style={{ margin: '0 auto' }}></div>
                    <p className="mt-md text-muted">Processing your submission...</p>
                </div>
            )}

            {/* File Upload Tab */}
            {activeTab === 'file' && !isLoading && (
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Upload Document</h3>
                    </div>

                    <FileUploader
                        onFileSelect={handleFileSelect}
                        disabled={isLoading}
                    />

                    {selectedFile && (
                        <div className="mt-lg">
                            <button
                                className="btn btn-accent btn-lg"
                                onClick={handleFileUpload}
                                disabled={isLoading}
                                style={{ width: '100%' }}
                            >
                                🚀 Upload and Analyze
                            </button>
                        </div>
                    )}
                </div>
            )}

            {/* Text Input Tab */}
            {activeTab === 'text' && !isLoading && (
                <TextInput
                    onSubmit={handleTextSubmit}
                    disabled={isLoading}
                />
            )}

            {/* Info Card */}
            <div className="card mt-lg" style={{ background: 'var(--bg-secondary)' }}>
                <h4 className="mb-sm">About AI Analysis</h4>
                <ul style={{ paddingLeft: '1.5rem', color: 'var(--text-secondary)' }}>
                    <li>Analysis includes summarization, entity extraction, and risk classification</li>
                    <li>All AI-generated content is clearly labeled</li>
                    <li>Token usage and cost estimates are displayed for transparency</li>
                    <li>Results can be reviewed and approved by analysts</li>
                </ul>
                <div className="badge badge-ai mt-md">
                    🤖 Powered by Hugging Face LLM
                </div>
            </div>
        </div>
    );
}

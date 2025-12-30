import { useState } from 'react';
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

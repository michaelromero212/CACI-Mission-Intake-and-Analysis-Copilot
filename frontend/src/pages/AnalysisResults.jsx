import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AnalysisCard from '../components/AnalysisCard';
import { missionsApi, analysisApi, reviewsApi } from '../api';
import { exportAnalysisToMarkdown } from '../utils/exportUtils';

/**
 * Analysis Results page - displays mission details and AI analysis.
 */
export default function AnalysisResults() {
    const { missionId } = useParams();
    const navigate = useNavigate();

    const [mission, setMission] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [review, setReview] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [error, setError] = useState(null);

    // Review form state
    const [reviewNotes, setReviewNotes] = useState('');
    const [isSubmittingReview, setIsSubmittingReview] = useState(false);

    useEffect(() => {
        loadMissionData();
    }, [missionId]);

    const loadMissionData = async () => {
        setIsLoading(true);
        setError(null);

        try {
            // Load mission details
            const missionData = await missionsApi.getById(missionId);
            setMission(missionData);

            // Try to load existing analysis
            try {
                const analysisData = await analysisApi.getResult(missionId);
                setAnalysis(analysisData);
            } catch (e) {
                // No analysis yet - that's okay
                console.log('No existing analysis found');
            }

            // Try to load existing review
            try {
                const reviewData = await reviewsApi.get(missionId);
                setReview(reviewData);
                setReviewNotes(reviewData.analyst_notes || '');
            } catch (e) {
                // No review yet - that's okay
            }
        } catch (err) {
            console.error('Failed to load mission:', err);
            setError('Failed to load mission data. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleRunAnalysis = async () => {
        setIsAnalyzing(true);
        setError(null);

        try {
            const result = await analysisApi.execute(missionId, true);
            setAnalysis(result);

            // Reload mission to get updated status
            const missionData = await missionsApi.getById(missionId);
            setMission(missionData);
        } catch (err) {
            console.error('Analysis failed:', err);
            setError(err.response?.data?.detail || 'Analysis failed. Please try again.');
        } finally {
            setIsAnalyzing(false);
        }
    };

    const handleSubmitReview = async (approved) => {
        setIsSubmittingReview(true);

        try {
            const result = await reviewsApi.submit(missionId, reviewNotes, approved);
            setReview(result);
        } catch (err) {
            console.error('Review submission failed:', err);
            setError('Failed to submit review. Please try again.');
        } finally {
            setIsSubmittingReview(false);
        }
    };

    const getStatusBadge = (status) => {
        const badges = {
            pending: { class: 'badge-warning', text: 'Pending' },
            ingested: { class: 'badge-success', text: 'Ingested' },
            analyzing: { class: 'badge-warning', text: 'Analyzing' },
            analyzed: { class: 'badge-success', text: 'Analyzed' },
            error: { class: 'badge-error', text: 'Error' }
        };
        return badges[status] || { class: '', text: status };
    };

    const getSourceIcon = (type) => {
        const icons = { pdf: '📄', csv: '📊', text: '📝' };
        return icons[type] || '📁';
    };

    if (isLoading) {
        return (
            <div className="card text-center">
                <div className="loading-spinner" style={{ margin: '0 auto' }}></div>
                <p className="mt-md text-muted">Loading mission data...</p>
            </div>
        );
    }

    if (!mission) {
        return (
            <div className="card text-center">
                <h2>Mission Not Found</h2>
                <p className="text-muted">The requested mission could not be found.</p>
                <button className="btn btn-primary mt-md" onClick={() => navigate('/')}>
                    Back to Intake
                </button>
            </div>
        );
    }

    const statusBadge = getStatusBadge(mission.status);

    return (
        <div>
            {/* Header */}
            <div className="flex justify-between items-center mb-lg">
                <div>
                    <div className="flex items-center gap-sm mb-sm">
                        <span style={{ fontSize: '2rem' }}>{getSourceIcon(mission.source_type)}</span>
                        <h1>{mission.filename || mission.source_label || 'Mission Analysis'}</h1>
                    </div>
                    <div className="flex items-center gap-md">
                        <span className={`badge ${statusBadge.class}`}>{statusBadge.text}</span>
                        <span className="text-muted">
                            {new Date(mission.ingestion_timestamp).toLocaleString()}
                        </span>
                    </div>
                </div>
                <div className="flex gap-sm">
                    {analysis && (
                        <button
                            className="btn btn-secondary"
                            onClick={() => exportAnalysisToMarkdown(mission, analysis, review)}
                            title="Download analysis report as Markdown"
                        >
                            📥 Export
                        </button>
                    )}
                    <button className="btn btn-secondary" onClick={() => navigate('/history')}>
                        View All Missions
                    </button>
                </div>
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

            <div className="grid grid-2">
                {/* Left Column - Mission Content */}
                <div>
                    <div className="card mb-lg">
                        <div className="card-header">
                            <h3 className="card-title">Mission Content</h3>
                        </div>
                        <div style={{
                            maxHeight: '400px',
                            overflow: 'auto',
                            background: 'var(--bg-secondary)',
                            padding: 'var(--spacing-md)',
                            borderRadius: 'var(--radius-md)',
                            fontFamily: 'var(--font-mono)',
                            fontSize: '0.875rem',
                            whiteSpace: 'pre-wrap'
                        }}>
                            {mission.normalized_content || 'No content available'}
                        </div>
                    </div>

                    {/* Run Analysis Button */}
                    {!analysis && !isAnalyzing && (
                        <button
                            className="btn btn-accent btn-lg"
                            onClick={handleRunAnalysis}
                            style={{ width: '100%' }}
                        >
                            🚀 Run AI Analysis
                        </button>
                    )}

                    {isAnalyzing && (
                        <div className="card text-center">
                            <div className="loading-spinner" style={{ margin: '0 auto' }}></div>
                            <p className="mt-md text-muted">Running AI analysis...</p>
                            <p className="text-muted" style={{ fontSize: '0.75rem' }}>
                                This may take a moment
                            </p>
                        </div>
                    )}

                    {/* Re-analyze Button */}
                    {analysis && !isAnalyzing && (
                        <button
                            className="btn btn-secondary mt-md"
                            onClick={handleRunAnalysis}
                            style={{ width: '100%' }}
                        >
                            🔄 Re-run Analysis
                        </button>
                    )}
                </div>

                {/* Right Column - Analysis Results & Review */}
                <div>
                    {analysis ? (
                        <>
                            <AnalysisCard analysis={analysis} />

                            {/* Analyst Review Section */}
                            <div className="card mt-lg">
                                <div className="card-header">
                                    <h3 className="card-title">Analyst Review</h3>
                                    {review?.approved && (
                                        <span className="badge badge-success">✓ Approved</span>
                                    )}
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Analyst Notes</label>
                                    <textarea
                                        className="form-textarea"
                                        value={reviewNotes}
                                        onChange={(e) => setReviewNotes(e.target.value)}
                                        placeholder="Add your notes, corrections, or observations..."
                                        rows={4}
                                    />
                                </div>

                                <div className="flex gap-md">
                                    <button
                                        className="btn btn-primary"
                                        onClick={() => handleSubmitReview(true)}
                                        disabled={isSubmittingReview}
                                    >
                                        ✓ Approve
                                    </button>
                                    <button
                                        className="btn btn-secondary"
                                        onClick={() => handleSubmitReview(false)}
                                        disabled={isSubmittingReview}
                                    >
                                        Save Notes
                                    </button>
                                </div>

                                {review && (
                                    <div className="text-muted mt-md" style={{ fontSize: '0.75rem' }}>
                                        Last reviewed: {new Date(review.reviewed_at).toLocaleString()}
                                    </div>
                                )}
                            </div>
                        </>
                    ) : (
                        <div className="card text-center" style={{ background: 'var(--bg-secondary)' }}>
                            <div style={{ fontSize: '3rem', marginBottom: 'var(--spacing-md)' }}>🔍</div>
                            <h3>No Analysis Yet</h3>
                            <p className="text-muted">
                                Click "Run AI Analysis" to generate insights for this mission.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

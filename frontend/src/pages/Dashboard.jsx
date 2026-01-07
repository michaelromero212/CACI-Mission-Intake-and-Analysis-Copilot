import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyticsApi, missionsApi } from '../api';

/**
 * Executive Dashboard - Clean, scannable view for senior leadership.
 * Focus: Key metrics at a glance, items needing attention.
 */
export default function Dashboard() {
    const navigate = useNavigate();
    const [summary, setSummary] = useState(null);
    const [recentMissions, setRecentMissions] = useState([]);
    const [highRiskMissions, setHighRiskMissions] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadDashboardData = useCallback(async () => {
        setIsLoading(true);
        setError(null);

        try {
            const [summaryData, highRiskData, missionsData] = await Promise.all([
                analyticsApi.getSummary(),
                analyticsApi.getHighRiskMissions(5),
                missionsApi.getAll()
            ]);

            setSummary(summaryData);
            setHighRiskMissions(highRiskData.missions || []);

            // Get 5 most recent missions - handle both array and object responses
            const missionsList = Array.isArray(missionsData)
                ? missionsData
                : (missionsData?.missions || []);
            const sorted = missionsList
                .sort((a, b) => new Date(b.ingestion_timestamp) - new Date(a.ingestion_timestamp))
                .slice(0, 5);
            setRecentMissions(sorted);
        } catch (err) {
            console.error('Failed to load dashboard:', err);
            setError('Failed to load dashboard data');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        loadDashboardData();
    }, [loadDashboardData]);

    const getStatusBadge = (status) => {
        const statusMap = {
            'analyzed': { label: 'Analyzed', class: 'badge-success' },
            'ingested': { label: 'Pending', class: 'badge-warning' },
            'error': { label: 'Error', class: 'badge-error' },
        };
        const s = statusMap[status] || { label: status, class: 'badge-default' };
        return <span className={`badge ${s.class}`}>{s.label}</span>;
    };

    const getRiskBadge = (level) => {
        const riskClass = `risk-badge risk-${(level || 'unknown').toLowerCase()}`;
        return <span className={riskClass}>{level || 'Unknown'}</span>;
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    };

    if (isLoading) {
        return (
            <div className="dashboard-loading">
                <div className="loading-spinner"></div>
                <p>Loading dashboard...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card" style={{ textAlign: 'center', padding: 'var(--space-xl)' }}>
                <p style={{ color: 'var(--color-error)' }}>⚠️ {error}</p>
                <button className="btn btn-primary mt-md" onClick={loadDashboardData}>
                    Retry
                </button>
            </div>
        );
    }

    const isEmpty = !summary || summary.total_missions === 0;
    const pendingCount = summary ? (summary.total_missions - summary.total_analyzed) : 0;
    const needsAttention = highRiskMissions.length > 0 || pendingCount > 0;

    return (
        <div className="executive-dashboard">
            {/* Header */}
            <div className="dashboard-header">
                <div>
                    <h1>📊 Dashboard</h1>
                    <p className="text-muted">Mission analysis overview</p>
                </div>
                <button className="btn btn-secondary" onClick={loadDashboardData}>
                    🔄 Refresh
                </button>
            </div>

            {isEmpty ? (
                <div className="empty-state-card">
                    <div className="empty-icon">📋</div>
                    <h2>No Missions Yet</h2>
                    <p>Start by uploading a mission document for analysis.</p>
                    <button className="btn btn-accent" onClick={() => navigate('/')}>
                        🚀 Create First Mission
                    </button>
                </div>
            ) : (
                <>
                    {/* Key Metrics */}
                    <div className="metrics-row">
                        <div className="metric-card">
                            <div className="metric-value">{summary.total_missions}</div>
                            <div className="metric-label">Total Missions</div>
                        </div>
                        <div className="metric-card metric-success">
                            <div className="metric-value">{summary.total_analyzed}</div>
                            <div className="metric-label">Analyzed</div>
                        </div>
                        <div className="metric-card metric-warning">
                            <div className="metric-value">{pendingCount}</div>
                            <div className="metric-label">Pending Review</div>
                        </div>
                    </div>

                    {/* System Status */}
                    <div className="status-banner">
                        {needsAttention ? (
                            <>
                                <span className="status-dot status-warning"></span>
                                <span>{highRiskMissions.length} high-risk item{highRiskMissions.length !== 1 ? 's' : ''} • {pendingCount} pending review</span>
                            </>
                        ) : (
                            <>
                                <span className="status-dot status-good"></span>
                                <span>All systems operational • No items require attention</span>
                            </>
                        )}
                    </div>

                    {/* Two Column Layout */}
                    <div className="dashboard-grid">
                        {/* Needs Attention */}
                        <div className="dashboard-section">
                            <h3 className="section-title">⚠️ Needs Attention</h3>
                            {highRiskMissions.length > 0 ? (
                                <ul className="attention-list">
                                    {highRiskMissions.map((mission) => (
                                        <li key={mission.mission_id} className="attention-item">
                                            <div className="attention-content">
                                                <span className="attention-source">{mission.source_label}</span>
                                                {getRiskBadge(mission.risk_level)}
                                            </div>
                                            <button
                                                className="btn btn-sm btn-primary"
                                                onClick={() => navigate(`/analysis/${mission.mission_id}`)}
                                            >
                                                Review
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <div className="empty-section">
                                    <span className="success-icon">✓</span>
                                    <span>No high-risk items</span>
                                </div>
                            )}
                        </div>

                        {/* Recent Activity */}
                        <div className="dashboard-section">
                            <h3 className="section-title">🕐 Recent Activity</h3>
                            {recentMissions.length > 0 ? (
                                <ul className="activity-list">
                                    {recentMissions.map((mission) => (
                                        <li
                                            key={mission.mission_id}
                                            className="activity-item"
                                            onClick={() => navigate(`/analysis/${mission.mission_id}`)}
                                        >
                                            <div className="activity-info">
                                                <span className="activity-source">{mission.source_label || mission.filename || 'Untitled'}</span>
                                                <span className="activity-date">{formatDate(mission.ingestion_timestamp)}</span>
                                            </div>
                                            {getStatusBadge(mission.status)}
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <div className="empty-section">
                                    <span>No recent activity</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Quick Stats Footer */}
                    <div className="quick-stats">
                        <div className="quick-stat">
                            <span className="quick-label">Avg Confidence</span>
                            <span className="quick-value">
                                {summary.avg_confidence_score
                                    ? `${(summary.avg_confidence_score * 100).toFixed(0)}%`
                                    : 'N/A'}
                            </span>
                        </div>
                        <div className="quick-stat">
                            <span className="quick-label">Total Tokens</span>
                            <span className="quick-value">{summary.total_tokens_used.toLocaleString()}</span>
                        </div>
                        <div className="quick-stat">
                            <span className="quick-label">Est. Cost</span>
                            <span className="quick-value">${summary.total_estimated_cost.toFixed(4)}</span>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}

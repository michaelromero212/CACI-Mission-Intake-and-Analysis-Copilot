import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Plot from 'react-plotly.js';
import { analyticsApi } from '../api';

/**
 * Mission Command Center Dashboard
 * Provides actionable intelligence for CACI analysts.
 */
export default function Dashboard() {
    const navigate = useNavigate();
    const [summary, setSummary] = useState(null);
    const [entityBreakdown, setEntityBreakdown] = useState(null);
    const [reviewStatus, setReviewStatus] = useState(null);
    const [highRiskMissions, setHighRiskMissions] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadAnalytics();
    }, []);

    const loadAnalytics = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const [summaryData, entityData, reviewData, highRiskData] = await Promise.all([
                analyticsApi.getSummary(),
                analyticsApi.getEntityBreakdown(),
                analyticsApi.getReviewStatus(),
                analyticsApi.getHighRiskMissions(5)
            ]);

            setSummary(summaryData);
            setEntityBreakdown(entityData);
            setReviewStatus(reviewData);
            setHighRiskMissions(highRiskData);
        } catch (err) {
            console.error('Failed to load analytics:', err);
            setError('Failed to load analytics data');
        } finally {
            setIsLoading(false);
        }
    };

    // CACI branding colors
    const colors = {
        navy: '#003366',
        blue: '#4A90D9',
        red: '#C41230',
        success: '#2E7D32',
        warning: '#ED6C02',
        purple: '#7B1FA2',
    };

    // Entity type colors for consistency
    const entityColors = {
        'PERSON': '#5C6BC0',
        'ORGANIZATION': '#26A69A',
        'SYSTEM': '#7E57C2',
        'RISK': colors.red,
        'LOCATION': '#42A5F5',
        'DATE': '#FFA726',
        'TECHNOLOGY': '#66BB6A',
    };

    const defaultLayout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { family: 'Inter, system-ui, sans-serif', color: '#1A2642' },
        margin: { t: 30, r: 20, b: 40, l: 40 },
    };

    if (isLoading) {
        return (
            <div style={{ textAlign: 'center', padding: 'var(--space-xl)' }}>
                <div className="loading-spinner" style={{ margin: '0 auto' }}></div>
                <p className="text-muted mt-md">Loading command center...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card" style={{ textAlign: 'center', padding: 'var(--space-xl)' }}>
                <p style={{ color: 'var(--color-error)' }}>⚠️ {error}</p>
                <button className="btn btn-primary mt-md" onClick={loadAnalytics}>
                    Retry
                </button>
            </div>
        );
    }

    const isEmpty = !summary || summary.total_missions === 0;

    if (isEmpty) {
        return (
            <div>
                <div className="mb-lg">
                    <h1>🎯 Mission Command Center</h1>
                    <p className="text-muted">Real-time intelligence for mission analysts.</p>
                </div>
                <div className="card" style={{
                    textAlign: 'center',
                    padding: 'var(--space-xl)',
                    background: 'linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%)'
                }}>
                    <div style={{ fontSize: '4rem', marginBottom: 'var(--space-md)', opacity: 0.6 }}>🎯</div>
                    <h2 style={{ color: 'var(--caci-navy)' }}>Ready for Intelligence</h2>
                    <p className="text-muted" style={{ maxWidth: '400px', margin: '0 auto var(--space-lg)' }}>
                        Analyze some missions to see actionable insights here.
                    </p>
                    <button className="btn btn-accent" onClick={() => navigate('/')}>
                        🚀 Create First Mission
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div>
            {/* Header */}
            <div className="flex justify-between items-center mb-lg">
                <div>
                    <h1>🎯 Mission Command Center</h1>
                    <p className="text-muted">Real-time intelligence for mission analysts.</p>
                </div>
                <button className="btn btn-secondary" onClick={loadAnalytics}>
                    🔄 Refresh
                </button>
            </div>

            {/* Key Metrics */}
            <div className="stats-grid mb-lg">
                <div className="stat-card">
                    <div className="stat-value">{summary.total_missions}</div>
                    <div className="stat-label">Total Missions</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ color: colors.warning }}>
                        {reviewStatus?.not_reviewed || 0}
                    </div>
                    <div className="stat-label">Pending Review</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ color: colors.success }}>
                        {reviewStatus?.approved || 0}
                    </div>
                    <div className="stat-label">Approved</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ color: colors.red }}>
                        {highRiskMissions?.total_high_risk || 0}
                    </div>
                    <div className="stat-label">High Risk</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{entityBreakdown?.total_entities || 0}</div>
                    <div className="stat-label">Entities Found</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">
                        {summary.avg_confidence_score
                            ? `${(summary.avg_confidence_score * 100).toFixed(0)}%`
                            : 'N/A'}
                    </div>
                    <div className="stat-label">Avg Confidence</div>
                </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-2 gap-lg mb-lg">
                {/* Entity Type Breakdown */}
                <div className="card chart-card">
                    <div className="card-header">
                        <h3 className="card-title">🏷️ Entity Breakdown</h3>
                    </div>
                    {entityBreakdown?.entities?.length > 0 ? (
                        <Plot
                            data={[{
                                x: entityBreakdown.entities.map(e => e.count),
                                y: entityBreakdown.entities.map(e => e.entity_type),
                                type: 'bar',
                                orientation: 'h',
                                marker: {
                                    color: entityBreakdown.entities.map(e =>
                                        entityColors[e.entity_type] || colors.navy
                                    )
                                },
                                text: entityBreakdown.entities.map(e => e.count),
                                textposition: 'outside',
                                hovertemplate: '%{y}: %{x}<extra></extra>'
                            }]}
                            layout={{
                                ...defaultLayout,
                                height: 300,
                                margin: { t: 10, r: 40, b: 40, l: 120 },
                                xaxis: {
                                    title: 'Count',
                                    tickfont: { size: 12 }
                                },
                                yaxis: {
                                    autorange: 'reversed',
                                    tickfont: { size: 13, color: '#1A2642' }
                                },
                                bargap: 0.25
                            }}
                            config={{ displayModeBar: false, responsive: true }}
                            style={{ width: '100%' }}
                        />
                    ) : (
                        <div style={{ textAlign: 'center', padding: 'var(--space-xl)', color: 'var(--text-muted)' }}>
                            No entities extracted yet
                        </div>
                    )}
                </div>

                {/* Review Status */}
                <div className="card chart-card">
                    <div className="card-header">
                        <h3 className="card-title">📋 Review Status</h3>
                    </div>
                    {reviewStatus && reviewStatus.total > 0 ? (
                        <Plot
                            data={[{
                                values: [
                                    reviewStatus.approved,
                                    reviewStatus.pending_review,
                                    reviewStatus.not_reviewed
                                ],
                                labels: ['Approved', 'Rejected', 'Pending Review'],
                                type: 'pie',
                                hole: 0.45,
                                marker: {
                                    colors: [colors.success, colors.red, '#BDBDBD'],
                                    line: { color: '#fff', width: 2 }
                                },
                                textinfo: 'percent',
                                textfont: { size: 14, color: '#fff' },
                                hovertemplate: '%{label}<br>%{value} missions<br>%{percent}<extra></extra>'
                            }]}
                            layout={{
                                ...defaultLayout,
                                height: 300,
                                margin: { t: 10, r: 10, b: 10, l: 10 },
                                showlegend: true,
                                legend: {
                                    orientation: 'h',
                                    y: -0.1,
                                    x: 0.5,
                                    xanchor: 'center',
                                    font: { size: 12 }
                                },
                                annotations: [{
                                    text: `<b>${reviewStatus.total}</b><br>total`,
                                    showarrow: false,
                                    font: { size: 18, color: colors.navy }
                                }]
                            }}
                            config={{ displayModeBar: false, responsive: true }}
                            style={{ width: '100%' }}
                        />
                    ) : (
                        <div style={{ textAlign: 'center', padding: 'var(--space-xl)', color: 'var(--text-muted)' }}>
                            No review data yet
                        </div>
                    )}
                </div>
            </div>

            {/* High Risk Missions Table */}
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">⚠️ High-Risk Missions</h3>
                    {highRiskMissions?.total_high_risk > 0 && (
                        <span className="badge badge-error">
                            {highRiskMissions.total_high_risk} flagged
                        </span>
                    )}
                </div>
                {highRiskMissions?.missions?.length > 0 ? (
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{
                                    borderBottom: '2px solid var(--border-color)',
                                    textAlign: 'left'
                                }}>
                                    <th style={{ padding: 'var(--space-sm)', fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Source</th>
                                    <th style={{ padding: 'var(--space-sm)', fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Risk</th>
                                    <th style={{ padding: 'var(--space-sm)', fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Summary</th>
                                    <th style={{ padding: 'var(--space-sm)', fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Confidence</th>
                                    <th style={{ padding: 'var(--space-sm)', fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Date</th>
                                    <th style={{ padding: 'var(--space-sm)' }}></th>
                                </tr>
                            </thead>
                            <tbody>
                                {highRiskMissions.missions.map((mission, idx) => (
                                    <tr
                                        key={mission.mission_id}
                                        style={{
                                            borderBottom: '1px solid var(--border-color)',
                                            background: idx % 2 === 0 ? 'transparent' : 'var(--bg-secondary)'
                                        }}
                                    >
                                        <td style={{ padding: 'var(--space-sm)', fontFamily: 'var(--font-mono)', fontSize: '0.8125rem' }}>
                                            {mission.source_label}
                                        </td>
                                        <td style={{ padding: 'var(--space-sm)' }}>
                                            <span className={`risk-badge risk-${mission.risk_level.toLowerCase()}`}>
                                                {mission.risk_level}
                                            </span>
                                        </td>
                                        <td style={{ padding: 'var(--space-sm)', fontSize: '0.8125rem', maxWidth: '300px' }}>
                                            {mission.summary || 'No summary'}
                                        </td>
                                        <td style={{ padding: 'var(--space-sm)', fontFamily: 'var(--font-mono)', fontSize: '0.8125rem' }}>
                                            {mission.confidence_score
                                                ? `${(mission.confidence_score * 100).toFixed(0)}%`
                                                : 'N/A'}
                                        </td>
                                        <td style={{ padding: 'var(--space-sm)', fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                            {mission.ingestion_timestamp}
                                        </td>
                                        <td style={{ padding: 'var(--space-sm)' }}>
                                            <button
                                                className="btn btn-sm btn-primary"
                                                onClick={() => navigate(`/analysis/${mission.mission_id}`)}
                                            >
                                                View
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div style={{
                        textAlign: 'center',
                        padding: 'var(--space-xl)',
                        color: 'var(--text-muted)'
                    }}>
                        <div style={{ fontSize: '2rem', marginBottom: 'var(--space-sm)' }}>✅</div>
                        No high-risk missions detected
                    </div>
                )}
            </div>
        </div>
    );
}

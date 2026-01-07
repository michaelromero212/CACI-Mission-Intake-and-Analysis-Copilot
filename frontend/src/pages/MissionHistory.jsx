import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import MissionCard from '../components/MissionCard';
import { missionsApi } from '../api';

/**
 * Mission Registry page - lists all missions with compact layout.
 */
export default function MissionHistory() {
    const navigate = useNavigate();
    const [missions, setMissions] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadMissions = useCallback(async () => {
        setIsLoading(true);
        setError(null);

        try {
            const data = await missionsApi.getAll();
            setMissions(data.missions || []);
        } catch (err) {
            console.error('Failed to load missions:', err);
            setError('Failed to load mission history. Please try again.');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        loadMissions();
    }, [loadMissions]);

    const handleDelete = async (missionId) => {
        try {
            await missionsApi.delete(missionId);
            setMissions(missions.filter(m => m.mission_id !== missionId));
        } catch (err) {
            console.error('Failed to delete mission:', err);
            setError('Failed to delete mission. Please try again.');
        }
    };

    // Group missions by status
    const groupedMissions = {
        analyzed: missions.filter(m => m.status === 'analyzed'),
        analyzing: missions.filter(m => m.status === 'analyzing'),
        ingested: missions.filter(m => m.status === 'ingested'),
        pending: missions.filter(m => m.status === 'pending'),
        error: missions.filter(m => m.status === 'error')
    };

    const stats = {
        total: missions.length,
        analyzed: groupedMissions.analyzed.length,
        pending: groupedMissions.pending.length + groupedMissions.ingested.length,
        errors: groupedMissions.error.length
    };

    return (
        <div>
            {/* Compact Header with Inline Stats */}
            <div className="page-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                    <h1 style={{ marginBottom: '0.25rem' }}>Mission Registry</h1>
                    <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.8125rem', fontFamily: 'var(--font-mono)' }}>
                        <span style={{ color: 'var(--text-muted)' }}>
                            <strong style={{ color: 'var(--text-primary)' }}>{stats.total}</strong> Total
                        </span>
                        <span style={{ color: 'var(--color-success)' }}>
                            <strong>{stats.analyzed}</strong> Analyzed
                        </span>
                        <span style={{ color: 'var(--color-warning)' }}>
                            <strong>{stats.pending}</strong> Pending
                        </span>
                        {stats.errors > 0 && (
                            <span style={{ color: 'var(--color-error)' }}>
                                <strong>{stats.errors}</strong> Errors
                            </span>
                        )}
                    </div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button className="btn btn-secondary btn-sm" onClick={loadMissions}>
                        ↻ Refresh
                    </button>
                    <button className="btn btn-primary btn-sm" onClick={() => navigate('/')}>
                        + New Mission
                    </button>
                </div>
            </div>

            {/* Error Display */}
            {error && (
                <div className="alert alert-error" style={{ marginBottom: '1rem' }}>
                    ⚠️ {error}
                </div>
            )}

            {/* Loading State */}
            {isLoading && (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                    <div className="spinner" style={{ margin: '0 auto 0.5rem' }}></div>
                    Loading missions...
                </div>
            )}

            {/* Empty State */}
            {!isLoading && missions.length === 0 && (
                <div className="card" style={{
                    textAlign: 'center',
                    padding: 'var(--space-xl)',
                    background: 'linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%)'
                }}>
                    <div style={{
                        fontSize: '4rem',
                        marginBottom: 'var(--space-md)',
                        opacity: 0.8
                    }}>🎯</div>
                    <h2 style={{ marginBottom: 'var(--space-sm)', color: 'var(--caci-navy)' }}>
                        Ready to Analyze
                    </h2>
                    <p className="text-muted" style={{
                        marginBottom: 'var(--space-lg)',
                        maxWidth: '400px',
                        margin: '0 auto var(--space-lg)'
                    }}>
                        Upload mission documents (PDF, CSV, TXT) or submit free text
                        for AI-assisted analysis, entity extraction, and risk classification.
                    </p>
                    <button
                        className="btn btn-accent btn-lg"
                        onClick={() => navigate('/')}
                        style={{ padding: 'var(--space-sm) var(--space-xl)' }}
                    >
                        🚀 Create First Mission
                    </button>
                    <div style={{
                        marginTop: 'var(--space-xl)',
                        display: 'flex',
                        justifyContent: 'center',
                        gap: 'var(--space-lg)',
                        flexWrap: 'wrap'
                    }}>
                        <div style={{ textAlign: 'center', opacity: 0.7 }}>
                            <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>📄</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>PDF</div>
                        </div>
                        <div style={{ textAlign: 'center', opacity: 0.7 }}>
                            <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>📊</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>CSV</div>
                        </div>
                        <div style={{ textAlign: 'center', opacity: 0.7 }}>
                            <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>📝</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>TXT</div>
                        </div>
                        <div style={{ textAlign: 'center', opacity: 0.7 }}>
                            <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>💬</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Free Text</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Mission List - Compact Table-like Layout */}
            {!isLoading && missions.length > 0 && (
                <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                    {/* Table Header */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 100px 120px 140px',
                        gap: '1rem',
                        padding: '0.75rem 1rem',
                        background: 'var(--bg-secondary)',
                        borderBottom: '1px solid var(--border-color)',
                        fontSize: '0.6875rem',
                        fontWeight: '600',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        color: 'var(--text-muted)'
                    }}>
                        <div>Mission</div>
                        <div>Type</div>
                        <div>Status</div>
                        <div style={{ textAlign: 'right' }}>Actions</div>
                    </div>

                    {/* Mission Rows */}
                    {missions.map((mission, index) => (
                        <div
                            key={mission.mission_id}
                            style={{
                                display: 'grid',
                                gridTemplateColumns: '1fr 100px 120px 140px',
                                gap: '1rem',
                                padding: '0.75rem 1rem',
                                alignItems: 'center',
                                borderBottom: index < missions.length - 1 ? '1px solid var(--border-color)' : 'none',
                                fontSize: '0.875rem'
                            }}
                        >
                            {/* Mission Name */}
                            <div>
                                <div style={{ fontWeight: '500', color: 'var(--text-primary)', marginBottom: '0.125rem' }}>
                                    {mission.filename || mission.source_label || 'Untitled'}
                                </div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                                    {new Date(mission.ingestion_timestamp).toLocaleDateString()} {new Date(mission.ingestion_timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </div>
                            </div>

                            {/* Type Badge */}
                            <div>
                                <span className="badge" style={{
                                    background: 'var(--bg-secondary)',
                                    color: 'var(--text-secondary)',
                                    border: '1px solid var(--border-color)'
                                }}>
                                    {mission.source_type.toUpperCase()}
                                </span>
                            </div>

                            {/* Status Badge */}
                            <div>
                                <span className={`badge badge-${mission.status}`}>
                                    {mission.status === 'analyzed' && '✓ '}
                                    {mission.status === 'analyzing' && '⏳ '}
                                    {mission.status === 'error' && '⚠ '}
                                    {mission.status.charAt(0).toUpperCase() + mission.status.slice(1)}
                                </span>
                            </div>

                            {/* Actions */}
                            <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                                <button
                                    className="btn btn-primary btn-sm"
                                    onClick={() => navigate(`/analysis/${mission.mission_id}`)}
                                >
                                    View
                                </button>
                                <button
                                    className="btn btn-secondary btn-sm"
                                    onClick={() => {
                                        if (window.confirm('Delete this mission?')) {
                                            handleDelete(mission.mission_id);
                                        }
                                    }}
                                    style={{ color: 'var(--color-error)' }}
                                >
                                    ✕
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

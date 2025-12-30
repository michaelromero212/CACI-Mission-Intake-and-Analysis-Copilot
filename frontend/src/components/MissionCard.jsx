import { useNavigate } from 'react-router-dom';

/**
 * Mission summary card for history view.
 */
export default function MissionCard({ mission, onDelete }) {
    const navigate = useNavigate();

    const {
        mission_id,
        source_type,
        filename,
        source_label,
        status,
        ingestion_timestamp,
        error_message
    } = mission;

    const getStatusClass = (status) => {
        return `status-dot ${status}`;
    };

    const getStatusLabel = (status) => {
        const labels = {
            pending: 'Pending',
            ingested: 'Ingested',
            analyzing: 'Analyzing...',
            analyzed: 'Analyzed',
            error: 'Error'
        };
        return labels[status] || status;
    };

    const getSourceIcon = (type) => {
        const icons = {
            pdf: '📄',
            csv: '📊',
            text: '📝'
        };
        return icons[type] || '📁';
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return '';
        return new Date(dateStr).toLocaleString();
    };

    const handleViewDetails = () => {
        navigate(`/analysis/${mission_id}`);
    };

    const handleDelete = (e) => {
        e.stopPropagation();
        if (window.confirm('Are you sure you want to delete this mission?')) {
            onDelete?.(mission_id);
        }
    };

    return (
        <div className="card" style={{ cursor: 'pointer' }} onClick={handleViewDetails}>
            <div className="flex justify-between items-center mb-md">
                <div className="flex items-center gap-sm">
                    <span style={{ fontSize: '1.5rem' }}>{getSourceIcon(source_type)}</span>
                    <div>
                        <div style={{ fontWeight: 600 }}>
                            {filename || source_label || 'Untitled Mission'}
                        </div>
                        <div className="text-muted" style={{ fontSize: '0.75rem' }}>
                            {source_type?.toUpperCase()}
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-sm">
                    <span className={getStatusClass(status)}></span>
                    <span style={{ fontSize: '0.875rem' }}>
                        {getStatusLabel(status)}
                    </span>
                </div>
            </div>

            {error_message && (
                <div className="badge badge-error mb-md" style={{ display: 'block', textAlign: 'left' }}>
                    ⚠️ {error_message}
                </div>
            )}

            <div className="flex justify-between items-center">
                <div className="text-muted" style={{ fontSize: '0.75rem' }}>
                    {formatDate(ingestion_timestamp)}
                </div>

                <div className="flex gap-sm">
                    <button
                        className="btn btn-primary"
                        onClick={handleViewDetails}
                    >
                        View Details
                    </button>
                    <button
                        className="btn btn-secondary"
                        onClick={handleDelete}
                        style={{ color: 'var(--color-error)' }}
                    >
                        Delete
                    </button>
                </div>
            </div>
        </div>
    );
}

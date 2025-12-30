import CostDisplay from './CostDisplay';
import ConfidenceIndicator from './ConfidenceIndicator';

/**
 * Analysis result card component.
 * Displays AI-generated analysis with clear labeling.
 */
export default function AnalysisCard({ analysis }) {
    if (!analysis) return null;

    const {
        summary_text,
        extracted_entities,
        risk_level,
        explanation,
        confidence_score,
        total_tokens,
        estimated_cost,
        llm_model_used,
        created_at
    } = analysis;

    const getRiskBadgeClass = (level) => {
        const classes = {
            low: 'badge-risk-low',
            medium: 'badge-risk-medium',
            high: 'badge-risk-high',
            critical: 'badge-risk-critical'
        };
        return classes[level] || 'badge-risk-medium';
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return '';
        return new Date(dateStr).toLocaleString();
    };

    return (
        <div className="card">
            <div className="card-header">
                <h3 className="card-title">Analysis Results</h3>
                <span className="badge badge-ai">
                    🤖 AI-Generated
                </span>
            </div>

            {/* Summary */}
            <div className="analysis-section">
                <div className="analysis-section-title">Summary</div>
                <p style={{ color: 'var(--text-primary)', marginBottom: 0 }}>
                    {summary_text || 'No summary available'}
                </p>
            </div>

            {/* Risk Level */}
            <div className="analysis-section">
                <div className="analysis-section-title">Risk Classification</div>
                <span className={`badge ${getRiskBadgeClass(risk_level)}`}>
                    {risk_level?.toUpperCase() || 'UNKNOWN'}
                </span>
            </div>

            {/* Entities */}
            {extracted_entities && extracted_entities.length > 0 && (
                <div className="analysis-section">
                    <div className="analysis-section-title">Extracted Entities</div>
                    <div className="entity-list">
                        {extracted_entities.map((entity, idx) => (
                            <div key={idx} className="entity-chip">
                                <span className="entity-type">{entity.type}</span>
                                <span>{entity.name}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Explanation */}
            <div className="analysis-section">
                <div className="analysis-section-title">AI Explanation</div>
                <p style={{ color: 'var(--text-secondary)', marginBottom: 0, fontStyle: 'italic' }}>
                    {explanation || 'No explanation available'}
                </p>
            </div>

            {/* Confidence */}
            <div className="analysis-section">
                <ConfidenceIndicator score={confidence_score} />
            </div>

            {/* Cost Transparency */}
            <div className="analysis-section">
                <div className="analysis-section-title">Cost Transparency</div>
                <CostDisplay
                    costInfo={{
                        input_tokens: analysis.input_tokens || 0,
                        output_tokens: analysis.output_tokens || 0,
                        total_tokens: total_tokens,
                        estimated_cost: estimated_cost,
                        model: llm_model_used
                    }}
                />
            </div>

            {/* Timestamp */}
            {created_at && (
                <div className="text-muted text-right mt-md" style={{ fontSize: '0.75rem' }}>
                    Analyzed at: {formatDate(created_at)}
                </div>
            )}
        </div>
    );
}

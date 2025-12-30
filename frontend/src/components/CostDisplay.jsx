/**
 * Cost transparency display component.
 * Shows token usage and estimated cost.
 */
export default function CostDisplay({ costInfo }) {
    if (!costInfo) return null;

    const { input_tokens, output_tokens, total_tokens, estimated_cost, model } = costInfo;

    return (
        <div className="cost-display">
            <div className="cost-item">
                <span className="cost-value">{input_tokens?.toLocaleString() || 0}</span>
                <span className="cost-label">Input Tokens</span>
            </div>

            <div className="cost-item">
                <span className="cost-value">{output_tokens?.toLocaleString() || 0}</span>
                <span className="cost-label">Output Tokens</span>
            </div>

            <div className="cost-item">
                <span className="cost-value">{total_tokens?.toLocaleString() || 0}</span>
                <span className="cost-label">Total Tokens</span>
            </div>

            <div className="cost-item">
                <span className="cost-value">
                    ${estimated_cost?.toFixed(4) || '0.0000'}
                </span>
                <span className="cost-label">Est. Cost</span>
            </div>

            {model && (
                <div className="cost-item">
                    <span className="cost-value" style={{ fontSize: '0.875rem' }}>
                        {model.split('/').pop()}
                    </span>
                    <span className="cost-label">Model</span>
                </div>
            )}
        </div>
    );
}

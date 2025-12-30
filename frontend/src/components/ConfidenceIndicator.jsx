/**
 * Heuristic-based confidence indicator.
 * Displays AI confidence as a visual bar.
 */
export default function ConfidenceIndicator({ score, showLabel = true }) {
    const percentage = Math.round((score || 0) * 100);

    // Determine confidence level
    let level = 'low';
    let levelText = 'Low';

    if (percentage >= 80) {
        level = 'high';
        levelText = 'High';
    } else if (percentage >= 60) {
        level = 'medium';
        levelText = 'Medium';
    }

    return (
        <div className="confidence-container">
            {showLabel && (
                <div className="flex justify-between mb-sm" style={{ fontSize: '0.875rem' }}>
                    <span className="text-muted">AI Confidence</span>
                    <span style={{ fontWeight: 600 }}>
                        {percentage}% ({levelText})
                    </span>
                </div>
            )}
            <div className="confidence-bar">
                <div
                    className={`confidence-fill ${level}`}
                    style={{ width: `${percentage}%` }}
                />
            </div>
            <p className="text-muted mt-sm" style={{ fontSize: '0.75rem' }}>
                ⚠️ This is a heuristic estimate, not a true ML confidence score.
            </p>
        </div>
    );
}

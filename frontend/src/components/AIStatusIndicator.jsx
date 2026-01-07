import { useState, useEffect, useCallback } from 'react';
import { aiApi } from '../api';

/**
 * AI Status Indicator Component
 * 
 * Displays the connection status of the Hugging Face LLM in the navbar.
 * Shows a color-coded status dot with model info and latency.
 */
export default function AIStatusIndicator() {
    const [status, setStatus] = useState({
        connected: null, // null = checking, true = connected, false = disconnected
        model: null,
        responseTime: null,
        error: null,
        loading: false,
    });
    const [isExpanded, setIsExpanded] = useState(false);
    const [lastChecked, setLastChecked] = useState(null);

    const checkStatus = useCallback(async () => {
        try {
            const result = await aiApi.getStatus();
            setStatus({
                connected: result.connected,
                model: result.model,
                responseTime: result.response_time_ms,
                error: result.error,
                loading: result.loading || false,
            });
            setLastChecked(new Date());
        } catch (err) {
            setStatus({
                connected: false,
                model: null,
                responseTime: null,
                error: err.message || 'Failed to check AI status',
                loading: false,
            });
            setLastChecked(new Date());
        }
    }, []);

    // Check status on mount and every 30 seconds
    useEffect(() => {
        checkStatus();
        const interval = setInterval(checkStatus, 30000);
        return () => clearInterval(interval);
    }, [checkStatus]);

    // Get status display info
    const getStatusInfo = () => {
        if (status.connected === null) {
            return {
                className: 'ai-status--checking',
                label: 'Checking...',
                icon: '○',
            };
        }
        if (status.loading) {
            return {
                className: 'ai-status--loading',
                label: 'Loading',
                icon: '◐',
            };
        }
        if (status.connected) {
            return {
                className: 'ai-status--connected',
                label: 'Connected',
                icon: '●',
            };
        }
        return {
            className: 'ai-status--disconnected',
            label: 'Disconnected',
            icon: '●',
        };
    };

    const statusInfo = getStatusInfo();
    const modelShortName = status.model?.split('/').pop() || 'Unknown';

    return (
        <div className="ai-status-container">
            <button
                className={`ai-status-indicator ${statusInfo.className}`}
                onClick={() => setIsExpanded(!isExpanded)}
                title={`AI Status: ${statusInfo.label}${status.error ? ` - ${status.error}` : ''}`}
            >
                <span className="ai-status-dot">{statusInfo.icon}</span>
                <span className="ai-status-label">AI</span>
            </button>

            {isExpanded && (
                <div className="ai-status-dropdown">
                    <div className="ai-status-header">
                        <span className={`ai-status-dot-large ${statusInfo.className}`}>
                            {statusInfo.icon}
                        </span>
                        <div className="ai-status-title">
                            <strong>AI Model Status</strong>
                            <span className="ai-status-state">{statusInfo.label}</span>
                        </div>
                    </div>

                    <div className="ai-status-details">
                        <div className="ai-status-row">
                            <span className="ai-status-label-detail">Model:</span>
                            <span className="ai-status-value" title={status.model || 'Not configured'}>
                                {modelShortName}
                            </span>
                        </div>

                        {status.responseTime !== null && (
                            <div className="ai-status-row">
                                <span className="ai-status-label-detail">Latency:</span>
                                <span className="ai-status-value">
                                    {status.responseTime}ms
                                </span>
                            </div>
                        )}

                        {status.error && (
                            <div className="ai-status-row ai-status-error">
                                <span className="ai-status-label-detail">Error:</span>
                                <span className="ai-status-value">{status.error}</span>
                            </div>
                        )}

                        {lastChecked && (
                            <div className="ai-status-row ai-status-muted">
                                <span className="ai-status-label-detail">Last checked:</span>
                                <span className="ai-status-value">
                                    {lastChecked.toLocaleTimeString()}
                                </span>
                            </div>
                        )}
                    </div>

                    <button className="ai-status-refresh" onClick={checkStatus}>
                        ↻ Refresh Status
                    </button>
                </div>
            )}
        </div>
    );
}

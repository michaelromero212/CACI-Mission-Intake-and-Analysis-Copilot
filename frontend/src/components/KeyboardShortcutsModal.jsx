import { SHORTCUTS } from '../hooks/useKeyboardShortcuts';

/**
 * Modal showing available keyboard shortcuts.
 */
export default function KeyboardShortcutsModal({ isOpen, onClose }) {
    if (!isOpen) return null;

    // All shortcuts including page-specific ones
    const allShortcuts = [
        ...SHORTCUTS,
        { key: 'a', description: 'Run Analysis (on detail page)', pageSpecific: true },
    ];

    return (
        <>
            {/* Backdrop */}
            <div
                style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    zIndex: 999,
                    backdropFilter: 'blur(2px)'
                }}
                onClick={onClose}
            />

            {/* Modal */}
            <div style={{
                position: 'fixed',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                backgroundColor: 'var(--bg-primary)',
                borderRadius: 'var(--radius-lg)',
                boxShadow: 'var(--shadow-lg)',
                padding: 'var(--spacing-xl)',
                minWidth: '320px',
                maxWidth: '90vw',
                zIndex: 1000,
                border: '1px solid var(--border-color)'
            }}>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: 'var(--spacing-lg)'
                }}>
                    <h2 style={{ margin: 0 }}>⌨️ Keyboard Shortcuts</h2>
                    <button
                        onClick={onClose}
                        style={{
                            background: 'none',
                            border: 'none',
                            fontSize: '1.5rem',
                            cursor: 'pointer',
                            color: 'var(--text-muted)',
                            padding: '0.25rem'
                        }}
                    >
                        ×
                    </button>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
                    {allShortcuts.map((shortcut) => (
                        <div
                            key={shortcut.key}
                            style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                padding: 'var(--spacing-sm) 0',
                                borderBottom: '1px solid var(--border-color)'
                            }}
                        >
                            <span style={{
                                color: shortcut.pageSpecific ? 'var(--text-muted)' : 'var(--text-primary)'
                            }}>
                                {shortcut.description}
                                {shortcut.pageSpecific && (
                                    <span style={{
                                        fontSize: '0.75rem',
                                        color: 'var(--text-muted)',
                                        marginLeft: '0.5rem'
                                    }}>
                                        (page-specific)
                                    </span>
                                )}
                            </span>
                            <kbd style={{
                                backgroundColor: 'var(--bg-secondary)',
                                border: '1px solid var(--border-color)',
                                borderRadius: 'var(--radius-sm)',
                                padding: '0.25rem 0.5rem',
                                fontFamily: 'var(--font-mono)',
                                fontSize: '0.875rem',
                                fontWeight: 600,
                                minWidth: '28px',
                                textAlign: 'center',
                                boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
                            }}>
                                {shortcut.key.toUpperCase()}
                            </kbd>
                        </div>
                    ))}
                </div>

                <div style={{
                    marginTop: 'var(--spacing-lg)',
                    textAlign: 'center',
                    color: 'var(--text-muted)',
                    fontSize: '0.8125rem'
                }}>
                    Press <kbd style={{
                        backgroundColor: 'var(--bg-secondary)',
                        border: '1px solid var(--border-color)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '0.125rem 0.375rem',
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.75rem'
                    }}>ESC</kbd> or click outside to close
                </div>
            </div>
        </>
    );
}

import { useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

/**
 * Keyboard shortcuts configuration.
 * Each shortcut has a key, description, and action.
 */
export const SHORTCUTS = [
    { key: 'n', description: 'New Mission', path: '/' },
    { key: 'h', description: 'Mission History', path: '/history' },
    { key: '?', description: 'Show Keyboard Shortcuts', action: 'showHelp' },
];

/**
 * Custom hook for global keyboard shortcuts.
 * Provides navigation shortcuts for power users.
 * 
 * @param {Object} options - Configuration options
 * @param {Function} options.onShowHelp - Callback when ? is pressed
 * @param {Function} options.onAnalyze - Callback when 'a' is pressed (on analysis page)
 * @returns {void}
 */
export function useKeyboardShortcuts({ onShowHelp, onAnalyze } = {}) {
    const navigate = useNavigate();
    const location = useLocation();

    const handleKeyDown = useCallback((event) => {
        // Don't trigger shortcuts when typing in inputs
        const activeElement = document.activeElement;
        const isInputElement =
            activeElement.tagName === 'INPUT' ||
            activeElement.tagName === 'TEXTAREA' ||
            activeElement.contentEditable === 'true';

        if (isInputElement) {
            return;
        }

        // Don't trigger if modifier keys are pressed (allow browser shortcuts)
        if (event.metaKey || event.ctrlKey || event.altKey) {
            return;
        }

        const key = event.key.toLowerCase();

        switch (key) {
            case 'n':
                event.preventDefault();
                navigate('/');
                break;
            case 'h':
                event.preventDefault();
                navigate('/history');
                break;
            case 'a':
                // Only trigger on analysis pages
                if (location.pathname.startsWith('/analysis/') && onAnalyze) {
                    event.preventDefault();
                    onAnalyze();
                }
                break;
            case '?':
                event.preventDefault();
                if (onShowHelp) {
                    onShowHelp();
                }
                break;
            default:
                break;
        }
    }, [navigate, location.pathname, onShowHelp, onAnalyze]);

    useEffect(() => {
        window.addEventListener('keydown', handleKeyDown);
        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, [handleKeyDown]);
}

export default useKeyboardShortcuts;

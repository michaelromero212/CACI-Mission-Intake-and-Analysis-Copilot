import { useState } from 'react';

/**
 * Free-text input component for mission submission.
 */
export default function TextInput({ onSubmit, disabled = false }) {
    const [content, setContent] = useState('');
    const [label, setLabel] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!content.trim()) {
            alert('Please enter some text content.');
            return;
        }

        if (onSubmit) {
            onSubmit(content, label || 'text_input');
        }
    };

    const handleClear = () => {
        setContent('');
        setLabel('');
    };

    return (
        <form onSubmit={handleSubmit} className="card">
            <div className="card-header">
                <h3 className="card-title">Free Text Input</h3>
            </div>

            <div className="form-group">
                <label className="form-label" htmlFor="source-label">
                    Source Label (optional)
                </label>
                <input
                    id="source-label"
                    type="text"
                    className="form-input"
                    placeholder="e.g., Analyst Notes, Email Summary..."
                    value={label}
                    onChange={(e) => setLabel(e.target.value)}
                    disabled={disabled}
                />
            </div>

            <div className="form-group">
                <label className="form-label" htmlFor="content">
                    Content
                </label>
                <textarea
                    id="content"
                    className="form-textarea"
                    placeholder="Paste or type mission-related content here..."
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    disabled={disabled}
                    rows={8}
                />
            </div>

            <div className="flex gap-md">
                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={disabled || !content.trim()}
                >
                    Submit Text
                </button>
                <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={handleClear}
                    disabled={disabled}
                >
                    Clear
                </button>
            </div>
        </form>
    );
}

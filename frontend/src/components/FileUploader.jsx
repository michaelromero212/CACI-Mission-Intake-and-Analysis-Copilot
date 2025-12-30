import { useState, useRef } from 'react';

/**
 * Drag-and-drop file upload component.
 * Supports PDF, CSV, and TXT files.
 */
export default function FileUploader({ onFileSelect, disabled = false }) {
    const [isDragOver, setIsDragOver] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const fileInputRef = useRef(null);

    const handleDragOver = (e) => {
        e.preventDefault();
        if (!disabled) setIsDragOver(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragOver(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragOver(false);

        if (disabled) return;

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    };

    const handleFileInput = (e) => {
        const files = e.target.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    };

    const handleFile = (file) => {
        const validTypes = [
            'application/pdf',
            'text/csv',
            'text/plain',
            'application/vnd.ms-excel',
        ];

        const isValidType = validTypes.includes(file.type) ||
            file.name.endsWith('.pdf') ||
            file.name.endsWith('.csv') ||
            file.name.endsWith('.txt');

        if (!isValidType) {
            alert('Please upload a PDF, CSV, or TXT file.');
            return;
        }

        setSelectedFile(file);
        if (onFileSelect) {
            onFileSelect(file);
        }
    };

    const handleClick = () => {
        if (!disabled && fileInputRef.current) {
            fileInputRef.current.click();
        }
    };

    const clearFile = (e) => {
        e.stopPropagation();
        setSelectedFile(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    return (
        <div
            className={`file-upload ${isDragOver ? 'drag-over' : ''} ${disabled ? 'disabled' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleClick}
            style={{ cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.6 : 1 }}
        >
            <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.csv,.txt"
                onChange={handleFileInput}
                style={{ display: 'none' }}
                disabled={disabled}
            />

            {selectedFile ? (
                <div className="flex flex-col items-center gap-sm">
                    <div className="file-upload-icon">📄</div>
                    <div className="text-primary" style={{ fontWeight: 600 }}>
                        {selectedFile.name}
                    </div>
                    <div className="text-muted" style={{ fontSize: '0.875rem' }}>
                        {(selectedFile.size / 1024).toFixed(1)} KB
                    </div>
                    <button
                        className="btn btn-secondary"
                        onClick={clearFile}
                        disabled={disabled}
                    >
                        Clear Selection
                    </button>
                </div>
            ) : (
                <>
                    <div className="file-upload-icon">📁</div>
                    <div className="file-upload-text">
                        <strong>Drop files here</strong> or click to browse
                    </div>
                    <div className="file-upload-hint">
                        Supports PDF, CSV, and TXT files
                    </div>
                </>
            )}
        </div>
    );
}

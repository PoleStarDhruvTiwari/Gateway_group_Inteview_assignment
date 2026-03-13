import React, { useState, useEffect } from 'react';
import { getFiles } from '../services/api';
import { formatDistanceToNow } from 'date-fns';

function FileList() {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchFiles();
        const interval = setInterval(fetchFiles, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);

    const fetchFiles = async () => {
        try {
            const data = await getFiles();
            setFiles(data);
            setError(null);
        } catch (err) {
            setError('Failed to load files');
        } finally {
            setLoading(false);
        }
    };

    const getStatusIcon = (status) => {
        switch(status) {
            case 'indexed': return '✅';
            case 'processing': return '⏳';
            case 'failed': return '❌';
            default: return '📄';
        }
    };

    if (loading) return <div className="card">Loading files...</div>;
    if (error) return <div className="card error-message">{error}</div>;

    return (
        <div className="card">
            <h2>📄 Your Documents</h2>
            {files.length === 0 ? (
                <div className="empty-state">
                    <p>No documents uploaded yet.</p>
                    <p className="hint">Upload PDF, DOCX, TXT, CSV, or JSON files above.</p>
                </div>
            ) : (
                <div className="file-list">
                    <ul className="file-items">
                        {files.map((file) => (
                            <li key={file.id} className="file-item">
                                <span className="file-icon">{getStatusIcon(file.status)}</span>
                                <span className="file-name">{file.filename}</span>
                                <span className="file-meta">
                                    ({file.file_type}, {file.total_chunks || 0} chunks)
                                </span>
                                <span className={`file-status status-${file.status}`}>
                                    {file.status}
                                </span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default FileList;
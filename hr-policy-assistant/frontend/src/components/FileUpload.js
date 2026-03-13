import React, { useState } from 'react';
import { uploadFile } from '../services/api';
import toast from 'react-hot-toast';

function FileUpload({ onUploadSuccess }) {
    const [file, setFile] = useState(null);
    const [fileType, setFileType] = useState('');
    const [docName, setDocName] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file || !fileType) return;

        setLoading(true);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('file_type', fileType);
        formData.append('document_name', docName);

        try {
            await uploadFile(formData);
            toast.success('File uploaded successfully! Processing started.');
            setFile(null);
            setFileType('');
            setDocName('');
            e.target.reset();
            onUploadSuccess();
        } catch (error) {
            toast.error('Upload failed: ' + (error.response?.data?.detail || 'Unknown error'));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card">
            <h2>📁 Upload HR Documents</h2>
            
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Select File:</label>
                    <input
                        type="file"
                        onChange={(e) => setFile(e.target.files[0])}
                        accept=".pdf,.docx,.txt,.csv,.json"
                        required
                    />
                </div>
                
                <div className="form-group">
                    <label>Document Type:</label>
                    <select value={fileType} onChange={(e) => setFileType(e.target.value)} required>
                        <option value="">Select type...</option>
                        <option value="pdf">📕 PDF (Policy Document)</option>
                        <option value="docx">📘 Word (Handbook)</option>
                        <option value="txt">📄 Text (Notes)</option>
                        <option value="csv">📊 CSV (Employee Data)</option>
                        <option value="json">🔧 JSON (Structured)</option>
                    </select>
                </div>
                
                <div className="form-group">
                    <label>Document Name (optional):</label>
                    <input
                        type="text"
                        value={docName}
                        onChange={(e) => setDocName(e.target.value)}
                        placeholder="e.g., Remote Work Policy 2024"
                    />
                </div>
                
                <button type="submit" className="btn btn-primary" disabled={loading || !file || !fileType}>
                    {loading ? <span className="loading-spinner">⏳</span> : 'Upload & Index'}
                </button>
            </form>
        </div>
    );
}

export default FileUpload;
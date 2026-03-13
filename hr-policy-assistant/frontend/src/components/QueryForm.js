import React, { useState } from 'react';
import { submitQuery } from '../services/api';
import toast from 'react-hot-toast';

function QueryForm({ onAnswerReceived }) {
    const [query, setQuery] = useState('');
    const [useCache, setUseCache] = useState(true);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('query', query);
            formData.append('use_cache', useCache);

            const response = await submitQuery(formData);
            onAnswerReceived(response);
        } catch (error) {
            toast.error('Failed to get answer: ' + (error.response?.data?.detail || 'Unknown error'));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card">
            <h2>🔍 Ask HR Questions</h2>
            
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Your Question:</label>
                    <textarea
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="e.g., What's the remote work policy for California? Or compare parental leave policies..."
                        rows="4"
                        required
                    />
                </div>
                
                <div className="checkbox-group">
                    <label>
                        <input
                            type="checkbox"
                            checked={useCache}
                            onChange={(e) => setUseCache(e.target.checked)}
                        />
                        Use cache (faster, cheaper)
                    </label>
                    <span className="hint">Cached answers expire after 7 days</span>
                </div>
                
                <button type="submit" className="btn btn-primary" disabled={loading || !query.trim()}>
                    {loading ? <span className="loading-spinner">🤔</span> : 'Ask Assistant'}
                </button>
            </form>
        </div>
    );
}

export default QueryForm;
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import Login from './components/Login';
import Register from './components/Register';
import Navbar from './components/Navbar';
import FileUpload from './components/FileUpload';
import FileList from './components/FileList';
import QueryForm from './components/QueryForm';
import AnswerDisplay from './components/AnswerDisplay';
import { getCurrentUser } from './services/auth';
import './App.css';

const queryClient = new QueryClient();

function Dashboard() {
    const [answer, setAnswer] = useState(null);
    const [refreshFiles, setRefreshFiles] = useState(0);

    return (
        <div className="app-container">
            <header>
                <h1>🏢 HR Policy Expert Assistant</h1>
                <p>Ask questions about HR policies, benefits, and procedures</p>
            </header>

            <div className="main-grid">
                <div className="left-column">
                    <FileUpload onUploadSuccess={() => setRefreshFiles(prev => prev + 1)} />
                    <FileList key={refreshFiles} />
                </div>

                <div className="right-column">
                    <QueryForm onAnswerReceived={setAnswer} />
                    {answer && <AnswerDisplay answer={answer} />}
                </div>
            </div>

            <div className="examples-section">
                <h3>📋 Try these example queries:</h3>
                <div className="example-chips">
                    <button className="chip" onClick={() => document.querySelector('textarea').value = 'What is the remote work policy for California employees?'}>
                        Remote work in CA
                    </button>
                    <button className="chip" onClick={() => document.querySelector('textarea').value = 'Compare maternity and paternity leave policies'}>
                        Parental leave
                    </button>
                    <button className="chip" onClick={() => document.querySelector('textarea').value = 'List all overtime approval requirements'}>
                        Overtime rules
                    </button>
                    <button className="chip" onClick={() => document.querySelector('textarea').value = 'What benefits are available for new parents?'}>
                        Benefits
                    </button>
                </div>
            </div>
        </div>
    );
}

function App() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            getCurrentUser()
                .then(userData => setUser(userData))
                .catch(() => localStorage.removeItem('token'))
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, []);

    if (loading) {
        return <div className="loading-screen">Loading...</div>;
    }

    return (
        <QueryClientProvider client={queryClient}>
            <Router>
                <div className="App">
                    <Navbar user={user} setUser={setUser} />
                    <Toaster position="top-right" />
                    <Routes>
                        <Route path="/login" element={!user ? <Login setUser={setUser} /> : <Navigate to="/" />} />
                        <Route path="/register" element={!user ? <Register /> : <Navigate to="/" />} />
                        <Route path="/" element={user ? <Dashboard /> : <Navigate to="/login" />} />
                    </Routes>
                </div>
            </Router>
        </QueryClientProvider>
    );
}

export default App;
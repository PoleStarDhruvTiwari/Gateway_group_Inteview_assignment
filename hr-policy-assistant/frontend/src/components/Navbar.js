import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { logout } from '../services/auth';

function Navbar({ user, setUser }) {
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        setUser(null);
        navigate('/login');
    };

    return (
        <nav className="navbar">
            <div className="nav-container">
                <Link to="/" className="nav-brand">
                    🏢 HR Policy Assistant
                </Link>
                <div className="nav-menu">
                    {user ? (
                        <>
                            <span className="nav-user">Hello, {user.full_name || user.email}</span>
                            <button onClick={handleLogout} className="logout-btn">
                                Logout
                            </button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="nav-link">Login</Link>
                            <Link to="/register" className="nav-link">Register</Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
}

export default Navbar;
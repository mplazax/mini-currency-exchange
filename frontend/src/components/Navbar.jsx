import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Navbar({ setActiveSection, isAuthenticated, setUserEmail }) {
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            const response = await fetch('http://localhost:5000/logout', {
                method: 'POST',
                credentials: 'include',
            });
            if (response.ok) {
                setUserEmail(null)
                navigate('/login');
            } else {
                console.error('Failed to logout');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <div id="Navbar">
            <button onClick={() => setActiveSection('Home')} className={'navButton'}>Home</button>
            <button onClick={() => navigate('/add_offer')} className={'navButton'}>Make offer</button>
            <button onClick={() => navigate('/get_offers')} className={'navButton'}>View offers</button>
            <button onClick={() => setActiveSection('ViewExchangeHistory')} className={'navButton'}>View exchange history</button>
            <button onClick={() => navigate('/wallet')} className={'navButton'}>My wallet</button>
            {isAuthenticated ? (
                <button onClick={handleLogout} className={'navButton'}>Logout</button>
            ) : (
                <button onClick={() => navigate('/login')} className={'navButton'}>Sign in</button>
            )}
        </div>
    );
}

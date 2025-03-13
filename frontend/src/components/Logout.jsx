import React from 'react';
import { useNavigate } from 'react-router-dom';

const LogoutButton = () => {
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            const response = await fetch('http://localhost:5000/logout', {
                method: 'POST',
                credentials: 'include', // Dodane, aby uwzględnić ciasteczka w żądaniu
            });
            if (response.ok) {
                navigate('/login');
            } else {
                console.error('Failed to logout');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <button onClick={handleLogout}>Logout</button>
    );
};

export default LogoutButton;

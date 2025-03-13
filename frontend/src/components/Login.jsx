import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';

function Login({setIsAuthenticated,setUserEmail}) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('http://localhost:5000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    email,
                    password,
                }),
            });
            const data = await response.json();
            if (response.ok) {
                if (data.redirect) {
                    setUserEmail(email)
                    setIsAuthenticated(true)
                    navigate('/wallet');
                } else {
                    setMessage(data.message);
                }
            } else {
                setMessage(data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            setMessage('Failed to fetch');
        }
    };

    return (
        <div className="container">
            <h2>Login</h2>
            <form onSubmit={handleSubmit}>
                <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                <button type="submit">Login</button>
            </form>
            {message && <p className="message">{message}</p>}
            <a href="/register">Register</a>
        </div>
    );
}

export default Login;

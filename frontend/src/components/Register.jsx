import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';


function Register() {
    const [fullname, setFullname] = useState('');
    const [email, setEmail] = useState('');
    const [password1, setPassword1] = useState('');
    const [password2, setPassword2] = useState('');
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('http://localhost:5000/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fullname,
                    email,
                    password1,
                    password2,
                }),
            });
            const data = await response.json();
            if (data.redirect) {
                navigate('/');
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
            <h2>Register</h2>
            <form onSubmit={handleSubmit}>
                <input type="text" placeholder="Full Name" value={fullname} onChange={(e) => setFullname(e.target.value)} required />
                <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                <input type="password" placeholder="Password" value={password1} onChange={(e) => setPassword1(e.target.value)} required />
                <input type="password" placeholder="Confirm Password" value={password2} onChange={(e) => setPassword2(e.target.value)} required />
                <button type="submit">Register</button>
            </form>
            {message && <p className="message">{message}</p>}
            <a href="/login">Login</a>
        </div>
    );
}

export default Register;

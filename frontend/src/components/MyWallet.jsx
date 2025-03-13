import React, { useState, useEffect } from 'react';
import {useNavigate} from "react-router-dom";
import MyTransactions from "./MyTransactions";
function MyWallet({setMyWallet}) {
    const [wallet, setWallet] = useState([]);
    const [transactions, setTransactions] = useState([]);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    useEffect(() => {
        fetch('http://localhost:5000/wallet', {
            method: 'GET',
            credentials: 'include', // Include credentials for session handling
        })
            .then(response => {
                if (response.status === 401 || response.status === 405) {
                    // If unauthorized or method not allowed, redirect to login
                    window.location.href = '/login';
                } else if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                setWallet(data.wallet)
                setMyWallet(data.wallet)
                setTransactions(data.transactions)
            }) // Update to setWallet(data.wallet)
            .catch(error => setError(error.toString()));
    }, []);

    if (error) {
        return <div>Error: {error}</div>;
    }
    return (
        <div className={'wallet'}>
            <button onClick={() => navigate('/')}><h1>Go to page</h1></button>
            <h1>My wallet</h1>
            <ul>
                {wallet.map((item, index) => (
                    <li key={index}>
                        <span>Currency: {item.currency}</span><span>Value: {item.value}</span>
                    </li>
                ))}
            </ul>
            <h1>My Transactions</h1>
            <MyTransactions/>
        </div>
    );
}

export default MyWallet;

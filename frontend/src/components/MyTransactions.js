import React, { useEffect, useState } from "react";

const MyTransactions = () => {
    const [transactions, setTransactions] = useState([]);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchTransactions = async () => {
            try {
                const response = await fetch("http://localhost:5000/my_transactions", {
                    method: 'GET',
                    headers: {
                        "Content-Type": "application/json",
                    },
                    credentials: 'include',
                });

                if (!response.ok) {
                    throw new Error("Failed to fetch transactions");
                }
                const data = await response.json();
                console.log(data);  // Debugging line to check fetched data
                setTransactions(data);
            } catch (error) {
                console.error("Error fetching transactions:", error);
                setError(error.message);
            }
        };

        fetchTransactions();
    }, []);

    return (
        <div className="tab">
            {error && <div className="error">{error}</div>}
            <table>
                <thead>
                <tr>
                    <th>From User</th>
                    <th>From Value</th>
                    <th>From Currency</th>
                    <th>To User</th>
                    <th>To Value</th>
                    <th>To Currency</th>
                    <th>Date</th>
                </tr>
                </thead>
                <tbody>
                {transactions.map((transaction, index) => (
                    <tr key={index}>
                        <td>{transaction.from_user}</td>
                        <td>{transaction.from_value}</td>
                        <td>{transaction.from_currency}</td>
                        <td>{transaction.to_user}</td>
                        <td>{transaction.to_value}</td>
                        <td>{transaction.to_currency}</td>
                        <td>{new Date(transaction.date).toLocaleString()}</td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
};

export default MyTransactions;

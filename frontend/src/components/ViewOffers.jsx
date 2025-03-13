import React, { useEffect, useState } from "react";

const ViewOffers = ({ userEmail }) => {
    const [offers, setOffers] = useState([]);

    useEffect(() => {
        const fetchOffers = async () => {
            try {
                const response = await fetch("http://localhost:5000/get_offers");
                if (!response.ok) {
                    throw new Error("Something went wrong");
                }
                const data = await response.json();
                setOffers(data);
            } catch (error) {
                console.error(error.message);
            }
        };

        fetchOffers();
    }, []);

    console.log(offers)
    const handleCancelOffer = async (offerId) => {
        try {
            const response = await fetch(`http://localhost:5000/cancel_offer/${offerId}`, {
                method: 'DELETE',
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                throw new Error("Failed to cancel offer");
            }

            const result = await response.json();
            alert(result.message);
            setOffers(offers.filter(offer => offer._id !== offerId));
        } catch (error) {
            console.error(error.message);
        }
    };

    const handleExchangeOffer = async (offerId) => {
        try {
            const response = await fetch(`http://localhost:5000/make_transaction/${offerId}`, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: 'include',
                body: JSON.stringify({ userEmail }), // Pass the user email to the backend
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || "Failed to exchange offer");
            }

            const result = await response.json();
            alert(result.message);
            setOffers(offers.filter(offer => offer._id !== offerId));
        } catch (error) {
            console.error(error.message);
        }
    };

    return (
        <div className="tab">
            <table>
                <thead>
                <tr>
                    <th>From User</th>
                    <th>From Value</th>
                    <th>From Currency</th>
                    <th>To Value</th>
                    <th>To Currency</th>
                    <th>Date</th>
                    <th>Action</th>
                </tr>
                </thead>
                <tbody>
                {offers.map((offer, index) => (
                    <tr key={index}>
                        <td>{offer.from_user}</td>
                        <td>{offer.from_value}</td>
                        <td>{offer.from_currency}</td>
                        <td>{offer.to_value}</td>
                        <td>{offer.to_currency}</td>
                        <td>{new Date(offer.date).toLocaleString()}</td>
                        <td>
                            {userEmail !== offer.from_user ?
                                <button className="navButton" onClick={() => handleExchangeOffer(offer._id)}>Exchange</button> :
                                <button className="navButton" onClick={() => handleCancelOffer(offer._id)}>Cancel</button>}
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
};

export default ViewOffers;

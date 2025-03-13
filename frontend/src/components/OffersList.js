import React, { useState, useEffect } from 'react';
import axios from 'axios';

const OfferList = () => {
    const [offers, setOffers] = useState([]);

    useEffect(() => {
        fetchOffers();
    }, []);

    const fetchOffers = () => {
        axios.get('/api/offers')
            .then(response => {
                setOffers(response.data);
            })
            .catch(error => {
                console.error('There was an error fetching the offers!', error);
            });
    };

    const handleCancel = (offerId) => {
        axios.post(`/api/offers/${offerId}/cancel`)
            .then(response => {
                alert('Offer cancelled successfully');
                fetchOffers();
            })
            .catch(error => {
                console.error('There was an error cancelling the offer!', error);
            });
    };

    const handleComplete = (offerId) => {
        axios.post(`/api/offers/${offerId}/complete`)
            .then(response => {
                alert('Offer completed successfully');
                fetchOffers();
            })
            .catch(error => {
                console.error('There was an error completing the offer!', error);
            });
    };

    return (
        <div>
            <h1>All Offers</h1>
            <ul>
                {offers.map(offer => (
                    <li key={offer._id}>
                        {offer.from_value} {offer.from_currency} for {offer.to_value} {offer.to_currency}
                        {offer.from_user === current_user._id ? (
                            <button onClick={() => handleCancel(offer._id)}>Cancel</button>
                        ) : (
                            <button onClick={() => handleComplete(offer._id)}>Complete</button>
                        )}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default OfferList;

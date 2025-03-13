import React, { useState } from "react";
import { Link } from "react-router-dom";

const MakeOffer = ({ userEmail, myWallet }) => {
    const currencies = ['USD', 'EUR', 'PLN', 'GBP', 'JPY', 'CZK'];
    const [value, setValue] = useState('');
    const [selectedCurrency, setSelectedCurrency] = useState('');
    const [toValue, setToValue] = useState('');
    const [toCurrency, setToCurrency] = useState('');

    const handleValueChange = (event) => {
        setValue(event.target.value);
    };

    const handleCurrencyChange = (event) => {
        setSelectedCurrency(event.target.value);
    };

    const handleToValueChange = (event) => {
        setToValue(event.target.value);
    };

    const handleToCurrencyChange = (event) => {
        setToCurrency(event.target.value);
    };

    const getWalletValue = (currency) => {
        const currencyObj = myWallet.find(item => item.currency === currency);
        return currencyObj ? currencyObj.value : 0;
    };

    const handleAddClick = async () => {
        if (value && selectedCurrency && toValue && toCurrency && userEmail != null) {
            const walletValue = getWalletValue(selectedCurrency);

            if (parseFloat(value) > walletValue) {
                alert(`You cannot offer more ${selectedCurrency} than you have in your wallet.`);
                return;
            }

            try {
                const response = await fetch("http://localhost:5000/add_offer", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        fromUser: userEmail,
                        fromValue: value,
                        fromCurrency: selectedCurrency,
                        toValue: toValue,
                        toCurrency: toCurrency
                    }),
                });

                if (!response.ok) {
                    throw new Error("Something went wrong");
                }

                const result = await response.json();
                alert(result.message);
                setValue('');
                setSelectedCurrency('');
                setToValue('');
                setToCurrency('');
            } catch (error) {
                alert(error.message);
            }
        } else {
            alert('Please fill in all fields.');
        }
    };

    return (
        <div>
            <h2>Make Offer</h2>
            {userEmail ?
                <div className={'MakeOffer'}>
                    <input type="number" value={value} onChange={handleValueChange} placeholder="Enter value to offer" />
                    <select value={selectedCurrency} onChange={handleCurrencyChange}>
                        <option value="">Select currency to offer</option>
                        {currencies.map((currency, index) => (
                            <option key={index} value={currency}>{currency}</option>
                        ))}
                    </select>
                    <input type="number" value={toValue} onChange={handleToValueChange} placeholder="Enter desired value" />
                    <select value={toCurrency} onChange={handleToCurrencyChange}>
                        <option value="">Select desired currency</option>
                        {currencies.map((currency, index) => (
                            <option key={index} value={currency}>{currency}</option>
                        ))}
                    </select>
                    <button onClick={handleAddClick}>Add</button>
                    <Link to="/get_offers">View Offers</Link>
                </div>
                : <h1>LOG IN</h1>}
        </div>
    );
};

export default MakeOffer;

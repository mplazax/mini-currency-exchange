import React, { useState, useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import 'chartjs-adapter-date-fns';

const ViewExchangeHistory = () => {
    const [transakcje, setTransakcje] = useState([]);
    const [fromCurrency, setFromCurrency] = useState('USD');
    const [toCurrency, setToCurrency] = useState('EUR');
    const chartRef = useRef(null);

    useEffect(() => {
        const pobierzTransakcje = async () => {
            try {
                const response = await fetch('http://localhost:5000/all_transactions', {
                    credentials: 'include' // To include cookies in the request
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                setTransakcje(data);
            } catch (error) {
                console.error('Błąd podczas pobierania transakcji:', error);
            }
        };

        pobierzTransakcje();
    }, []);

    useEffect(() => {
        if (chartRef.current) {
            chartRef.current.destroy();
        }

        const ctx = document.getElementById('wykres').getContext('2d');
        const filteredTransakcje = transakcje.filter(
            transakcja => transakcja.from_currency === fromCurrency && transakcja.to_currency === toCurrency
        );

        const daty = filteredTransakcje.map(transakcja => new Date(transakcja.date));
        const stosunki = filteredTransakcje.map(transakcja => transakcja.to_value / transakcja.from_value);

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: daty,
                datasets: [{
                    label: `Stosunek transakcji: ${fromCurrency}/${toCurrency}`,
                    data: stosunki,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        },
                        title: {
                            display: true,
                            text: 'Data transakcji'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: `Stosunek wartości (${fromCurrency} do ${toCurrency})`
                        }
                    }
                }
            }
        });

        chartRef.current = chart;
    }, [transakcje, fromCurrency, toCurrency]);

    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        if (name === 'fromCurrency') {
            setFromCurrency(value);
        } else if (name === 'toCurrency') {
            setToCurrency(value);
        }
    };

    return (
        <div className="view-exchange-history-container">
            <div className="select-container">
                <label>Waluta sprzedawana:</label>
                <select name="fromCurrency" value={fromCurrency} onChange={handleFilterChange}>
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                    <option value="PLN">PLN</option>
                    <option value="JPY">JPY</option>
                    <option value="CZK">CZK</option>
                </select>
            </div>
            <div className="select-container">
                <label>Waluta wymieniana:</label>
                <select name="toCurrency" value={toCurrency} onChange={handleFilterChange}>
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                    <option value="PLN">PLN</option>
                    <option value="JPY">JPY</option>
                    <option value="CZK">CZK</option>
                </select>
            </div>
            <div>
                <canvas id="wykres"></canvas>
            </div>
        </div>
    );
};

export default ViewExchangeHistory;


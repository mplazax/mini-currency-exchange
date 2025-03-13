import React, { useEffect, useRef } from 'react';
import { Line } from 'react-chartjs-2';
import 'chartjs-adapter-date-fns'; // Import the chartjs-adapter-date-fns adapter

const ExchangeChart = ({ data, paidCurrency, soldCurrency }) => {
    const chartRef = useRef(null);

    useEffect(() => {
        // Destroy the chart if it exists before re-rendering
        if (chartRef.current) {
            chartRef.current.chartInstance.destroy();
        }
    }, [data, paidCurrency, soldCurrency]);

    const chartData = {
        labels: data.map(transaction => transaction.date),
        datasets: [
            {
                label: `Amount Exchanged (${soldCurrency}/${paidCurrency})`,
                data: data.map(transaction => transaction.amount),
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }
        ]
    };

    const chartOptions = {
        scales: {
            x: {
                type: 'time'
            },
            y: {
                beginAtZero: true
            }
        }
    };

    return (
        <div>
            <h2>Exchange History</h2>
            <Line ref={chartRef} data={chartData} options={chartOptions} />
        </div>
    );
};

export default ExchangeChart;

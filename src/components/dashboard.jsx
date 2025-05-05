// File: dashboard.jsx

import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';

export default function AivestorDashboard() {
  const [ticker, setTicker] = useState('AAPL');
  const [hasBought, setHasBought] = useState(false);
  const [quantity, setQuantity] = useState(10);
  const [buyDate, setBuyDate] = useState('2023-10-10');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [chartData, setChartData] = useState(null);

  const apiBase = "https://bn9aw7f91d.execute-api.us-east-2.amazonaws.com";
  // const apiBase =  "http://localhost:5000";
 

  const analyzeStock = async () => {
    setLoading(true);
    try {
      const url = hasBought
        ? `${apiBase}/analyze?ticker=${ticker}&quantity=${quantity}&buy_date=${buyDate}`
        : `${apiBase}/analyze?ticker=${ticker}`;
      const res = await fetch(url);
      const data = await res.json();
      setResult(data);
      fetchChartData(ticker);
    } catch (err) {
      console.error(err);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchChartData = async (ticker) => {
    try {
      const res = await fetch(`${apiBase}/chart?ticker=${ticker}`);
      const data = await res.json();
      setChartData({
        x: data.dates.map(ts => new Date(ts)),
        y: data.prices,
      });
    } catch (error) {
      console.error("Chart fetch error:", error);
      setChartData(null);
    }
  };

  const resetState = () => {
    setTicker('AAPL');
    setHasBought(false);
    setQuantity(10);
    setBuyDate('2023-10-10');
    setResult(null);
    setChartData(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const gainLoss = () => {
    if (!result?.buy_price || !result?.current_price) return null;
    const gain = ((result.current_price - result.buy_price) / result.buy_price) * 100;
    return gain.toFixed(2);
  };

  const formatMultiline = (text) => {
    return text.split('\n').map((line, idx) => <div key={idx}>{line}</div>);
  };

  const getDecisionColor = () => {
    if (!result?.decision_result) return "from-gray-800 to-gray-900";
    const decisionLine = result.decision_result.split('\n')[0].toLowerCase();
    if (decisionLine.includes("buy") && !decisionLine.includes("don't")) return "from-green-900 via-green-700 to-green-500";
    if (decisionLine.includes("sell")) return "from-red-900 via-red-700 to-red-500";
    if (decisionLine.includes("hold")) return "from-yellow-700 via-yellow-600 to-yellow-500";
    return "from-gray-800 to-gray-900";
  };

  const getBadge = () => {
    if (!result?.decision_result) return null;
    const decision = result.decision_result.split('\n')[0].toUpperCase();
    if (decision.includes("BUY")) return <span className="bg-green-600 text-white text-xs px-3 py-1 rounded-full">{decision}</span>;
    if (decision.includes("SELL")) return <span className="bg-red-600 text-white text-xs px-3 py-1 rounded-full">{decision}</span>;
    if (decision.includes("HOLD")) return <span className="bg-yellow-500 text-black text-xs px-3 py-1 rounded-full">{decision}</span>;
    return null;
  };

  return (
    <div className={`relative min-h-screen text-white p-6 bg-gradient-to-br overflow-hidden transition-all duration-700 ease-in-out ${result ? getDecisionColor() : 'from-gray-900 to-black'}`}>
      {/* Background Particles */}
      <div className="absolute inset-0 z-0 overflow-hidden">
        <div className="w-full h-full animate-pulse bg-gradient-to-br from-white/5 via-white/10 to-white/5 blur-3xl opacity-20 rounded-full" style={{ filter: 'blur(120px)' }}></div>
      </div>

      <div className="relative z-10 max-w-screen-lg mx-auto">
      <h1 className="text-4xl font-extrabold mb-6 text-center tracking-tight">
      <span className="text-blue-400">AIvestor</span> Dashboard
</h1>

        <div className="flex flex-wrap gap-6 mb-6 items-end justify-center">
          <div>
            <label className="block text-sm mb-1">Stock Ticker</label>
            <input
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              className="p-2 rounded bg-gray-800 border border-gray-600"
              placeholder="AAPL"
            />
          </div>
          <div className="flex items-center space-x-2 mt-6">
            <input
              type="checkbox"
              checked={hasBought}
              onChange={(e) => setHasBought(e.target.checked)}
            />
            <label>Already Bought?</label>
          </div>
          {hasBought && (
            <>
              <div>
                <label className="block text-sm mb-1">Quantity</label>
                <input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(Number(e.target.value))}
                  className="p-2 rounded bg-gray-800 border border-gray-600"
                  placeholder="10"
                />
              </div>
              <div>
                <label className="block text-sm mb-1">Buy Date</label>
                <input
                  type="date"
                  value={buyDate}
                  onChange={(e) => setBuyDate(e.target.value)}
                  className="p-2 rounded bg-gray-800 border border-gray-600"
                />
              </div>
            </>
          )}
          <button
            onClick={analyzeStock}
            className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-700 mt-6"
          >
            Analyze
          </button>
          <button
            onClick={() => window.location.reload()}
            className="bg-gray-600 px-4 py-2 rounded hover:bg-gray-700 mt-6"
          >
            Reset
          </button>
        </div>

        {loading && <p className="text-center text-lg">⏳ Analyzing...</p>}

        {result && (
          <div className="bg-gray-800 p-4 rounded-lg w-full animate-fade-in">
            <h2 className="text-xl font-semibold mb-2 flex items-center gap-3">
              {result.ticker} Recommendation
              {getBadge()}
            </h2>
            <div className="whitespace-pre-wrap text-sm text-gray-100">
              {formatMultiline(result.decision_result)}
            </div>

            {hasBought && result.buy_price && result.current_price && (
              <div className="mt-4">
                <h3 className="font-semibold">Investment Summary</h3>
                <p>Buy Price: ${result.buy_price}</p>
                <p>Current Price: ${result.current_price}</p>
                <p>
                  Gain/Loss: <span className={gainLoss() >= 0 ? 'text-green-400' : 'text-red-400'}>
                    {gainLoss()}%
                  </span>
                </p>
              </div>
            )}

            {result.financials && (
              <div className="mt-4">
                <h3 className="font-semibold">Financials</h3>
                <p>Cash: ${result.financials.cash}</p>
                <p>Debt: ${result.financials.debt}</p>
                <p>Retained Earnings: ${result.financials.retained}</p>
              </div>
            )}

            {chartData && (
              <div className="mt-6 bg-black/40 p-4 rounded-xl shadow-lg">
                <h3 className="font-semibold mb-2">Price Chart (6 months)</h3>
                <Plot
                  data={[{
                    x: chartData.x,
                    y: chartData.y,
                    type: 'scatter',
                    mode: 'lines+markers',
                    marker: { color: 'cyan' },
                    line: { shape: 'spline', width: 2 }
                  }]}
                  layout={{
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'transparent',
                    font: { color: 'white' },
                    xaxis: {
                      title: 'Date',
                      showgrid: false,
                      zeroline: false
                    },
                    yaxis: {
                      title: 'Price (USD)',
                      showgrid: false,
                      zeroline: false
                    },
                    margin: { t: 10, l: 30, r: 10, b: 40 },
                    responsive: true,
                    displayModeBar: false
                  }}
                  useResizeHandler
                  style={{ width: '100%', height: '400px' }}
                />
              </div>
            )}
          </div>
        )}

<footer className="mt-12 text-center text-sm text-gray-400">
  <p className="text-sm">
    Made by <span className="font-semibold text-white">MANAV</span>, <span className="font-semibold text-white">ARYAN</span>, and <span className="font-semibold text-white">RAMYA</span>
  </p>

  <div className="mt-2">
    <a href="mailto:manav@ieee.org" className="text-blue-400 hover:underline flex items-center justify-center gap-1">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-4 h-4">
        <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25H4.5a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5H4.5a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.913l-7.5 4.5a2.25 2.25 0 01-2.28 0l-7.5-4.5A2.25 2.25 0 012.25 6.993V6.75" />
      </svg>
      Contact: manav@ieee.org
    </a>
  </div>
</footer>
      </div>
    </div>
  );
}

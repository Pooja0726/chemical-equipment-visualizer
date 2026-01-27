import React, { useState, useEffect } from 'react';
import './App.css';
import { Bar, Pie } from 'react-chartjs-2';
import ChartDataLabels from 'chartjs-plugin-datalabels'; // Needed for percentage labels
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

// Register standard elements PLUS the datalabels plugin
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  ChartDataLabels
);

// MODIFIED: This now reads your Railway Variable or defaults to localhost for development
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

function App() {
  const [datasets, setDatasets] = useState([]);
  const [currentDataset, setCurrentDataset] = useState(null);
  const [selectedDatasetId, setSelectedDatasetId] = useState('');
  const [currentPage, setCurrentPage] = useState(0);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/datasets/`);
      const data = await response.json();
      let datasetList = data.results || (Array.isArray(data) ? data : []);
      setDatasets(datasetList);
    } catch (error) {
      console.error('Error loading datasets:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || !file.name.endsWith('.csv')) {
      alert('Please select a valid CSV file');
      return;
    }
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/datasets/upload/`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        alert('✅ File uploaded successfully!');
        await loadDatasets();
        setCurrentDataset(data);
        setCurrentPage(1);
      } else {
        const errorData = await response.json();
        alert(`❌ Server Error: ${JSON.stringify(errorData)}`);
      }
    } catch (error) {
      alert(`❌ Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  };

  const handleDatasetSelect = async (event) => {
    const datasetId = event.target.value;
    setSelectedDatasetId(datasetId);
    if (!datasetId) {
      setCurrentDataset(null);
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/datasets/${datasetId}/`);
      if (response.ok) {
        const data = await response.json();
        setCurrentDataset(data);
        setCurrentPage(1);
      }
    } catch (error) {
      console.error('Error loading dataset:', error);
    }
  };

  const handleDownloadPDF = async () => {
    if (!currentDataset) return;
    try {
      const response = await fetch(`${API_BASE_URL}/datasets/${currentDataset.id}/download_pdf/`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `equipment_report_${currentDataset.id}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      alert(`❌ Download failed: ${error.message}`);
    }
  };

  // --- CHART LOGIC ---

  const getBarChartData = () => {
    if (!currentDataset || !currentDataset.summary) return null;
    const summary = currentDataset.summary;
    return {
      labels: ['Flowrate', 'Pressure', 'Temperature'],
      datasets: [{
        label: 'Average Values',
        data: [summary.avg_flowrate || 0, summary.avg_pressure || 0, summary.avg_temperature || 0],
        backgroundColor: ['#36A2EB', '#FF6384', '#FFCE56'],
      }],
    };
  };

  const getPieChartData = () => {
    if (!currentDataset || !currentDataset.summary || !currentDataset.summary.equipment_types) return null;
    const types = currentDataset.summary.equipment_types;
    return {
      labels: Object.keys(types),
      datasets: [{
        data: Object.values(types),
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'],
        borderWidth: 2,
        borderColor: '#ffffff',
        spacing: 5, 
        hoverOffset: 15 
      }],
    };
  };

  // Base options for shared styling
  const baseChartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: { position: 'top', labels: { font: { weight: 'bold' } } },
      title: {
        display: true,
        font: { size: 18, weight: 'bold' },
        padding: { top: 10, bottom: 20 },
        color: '#000000'
      }
    },
  };

  // Custom options for Bar Chart (Heading + Normal Values)
  const barOptions = {
    ...baseChartOptions,
    plugins: {
      ...baseChartOptions.plugins,
      title: { ...baseChartOptions.plugins.title, text: 'Average Parameter Values' },
      datalabels: {
        color: '#ffffff',
        font: { weight: 'bold', size: 14 },
        formatter: (value) => value.toFixed(1), // Normal values
      }
    }
  };

  // Custom options for Pie Chart (Heading + Percentages)
  const pieOptions = {
    ...baseChartOptions,
    plugins: {
      ...baseChartOptions.plugins,
      title: { ...baseChartOptions.plugins.title, text: 'Equipment Type Distribution' },
      datalabels: {
        color: '#ffffff',
        font: { weight: 'bold', size: 14 },
        formatter: (value, ctx) => {
          let sum = 0;
          let dataArr = ctx.chart.data.datasets[0].data;
          dataArr.forEach(data => sum += data);
          return sum > 0 ? (value * 100 / sum).toFixed(1) + "%" : "0%";
        },
      }
    }
  };

  return (
    <div className="app">
      <div className="sidebar">
        <div className="logo">🧪 Chemical Equipment<br />Parameter Visualizer</div>
        <button className={`nav-button ${currentPage === 0 ? 'active' : ''}`} onClick={() => setCurrentPage(0)}>📤 Upload Dataset</button>
        <button className={`nav-button ${currentPage === 1 ? 'active' : ''}`} onClick={() => setCurrentPage(1)}>📊 Analyze Report</button>
        <button className={`nav-button ${currentPage === 2 ? 'active' : ''}`} onClick={() => setCurrentPage(2)}>📋 Equipment Report</button>
        <div className="footer">Version 1.0<br />© 2026</div>
      </div>

      <div className="content">
        {currentPage === 0 && (
          <div className="page">
            <h1 className="page-title">Upload & Select Dataset</h1>
            <div className="card">
              <h2 className="card-title">📁 Upload New Dataset</h2>
              <button className="upload-button" onClick={() => document.getElementById('file-input').click()}>
                {uploading ? '⏳ Uploading...' : '📤 Choose CSV File'}
              </button>
              <input 
                id="file-input"
                type="file" 
                accept=".csv" 
                onChange={handleFileUpload} 
                disabled={uploading} 
                style={{ display: 'none' }} 
              />
            </div>
            <div className="card">
              <h2 className="card-title">📊 Select Existing Dataset</h2>
              <select className="dataset-select" value={selectedDatasetId} onChange={handleDatasetSelect}>
                <option value="">{datasets.length === 0 ? 'No datasets available' : 'Select a dataset...'}</option>
                {datasets.map((ds) => (
                  <option key={ds.id} value={ds.id}>{ds.filename} - {ds.upload_date?.substring(0, 10)}</option>
                ))}
              </select>
            </div>
          </div>
        )}

        {currentPage === 1 && (
          <div className="page">
            <h1 className="page-title">Data Analysis & Visualization</h1>
            {currentDataset?.summary ? (
              <>
                <div className="stats-grid">
                  <div className="stat-card stat-card-blue">
                    <div className="stat-title">Total Records</div>
                    <div className="stat-value">{currentDataset.row_count || 0}</div>
                  </div>
                  <div className="stat-card stat-card-purple">
                    <div className="stat-title">Avg Flowrate</div>
                    <div className="stat-value">{currentDataset.summary.avg_flowrate?.toFixed(1) || 0}</div>
                  </div>
                  <div className="stat-card stat-card-red">
                    <div className="stat-title">Avg Pressure</div>
                    <div className="stat-value">{currentDataset.summary.avg_pressure?.toFixed(1) || 0}</div>
                  </div>
                  <div className="stat-card stat-card-orange">
                    <div className="stat-title">Avg Temperature</div>
                    <div className="stat-value">{currentDataset.summary.avg_temperature?.toFixed(1) || 0}</div>
                  </div>
                </div>
                <div className="card">
                  <h2 className="card-title">📈 Visual Analytics</h2>
                  <div className="charts-container">
                    <div className="chart-wrapper">
                      {getBarChartData() && <Bar data={getBarChartData()} options={barOptions} />}
                    </div>
                    <div className="chart-wrapper">
                      {getPieChartData() && <Pie data={getPieChartData()} options={pieOptions} />}
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="card"><p className="empty-state">📊 No dataset selected.</p></div>
            )}
          </div>
        )}

        {currentPage === 2 && (
          <div className="page">
            <div className="page-header">
              <h1 className="page-title">Equipment Records</h1>
              <button className="download-button" onClick={handleDownloadPDF}>📄 Download PDF Report</button>
            </div>
            <div className="card">
              <h2 className="card-title">📋 Detailed Equipment Data</h2>
              {currentDataset?.records ? (
                <div className="table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Equipment Name</th>
                        <th>Type</th>
                        <th>Flowrate</th>
                        <th>Pressure</th>
                        <th>Temperature</th>
                      </tr>
                    </thead>
                    <tbody>
                      {currentDataset.records.map((record, index) => (
                        <tr key={index}>
                          <td>{record.equipment_name}</td>
                          <td>{record.equipment_type}</td>
                          <td>{record.flowrate}</td>
                          <td>{record.pressure}</td>
                          <td>{record.temperature}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="empty-state">📋 No dataset selected.</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
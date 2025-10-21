import React, { useState, useEffect } from 'react';
import { useExport } from '../hooks/useExport';

const SimpleExportButtons = ({ ringId }) => {
  const { downloadDemo, loading } = useExport();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Small delay for smooth appearance
    setTimeout(() => setIsVisible(true), 200);
  }, []);

  const handleDownload = (fileType) => {
    downloadDemo(ringId || 'demo', fileType);
  };

  if (!isVisible) return null;

  return (
    <div style={{
      marginTop: '20px',
      padding: '16px',
      background: '#1a1a1a',
      border: '1px solid #333',
      borderRadius: '8px',
      opacity: isVisible ? 1 : 0,
      transition: 'opacity 0.3s ease'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        marginBottom: '12px',
        color: '#10a37f',
        fontSize: '14px',
        fontWeight: '600'
      }}>
        <span>📊</span>
        <span>Export Analysis Report</span>
      </div>
      
      <div style={{
        fontSize: '12px',
        color: '#8e8ea0',
        marginBottom: '16px'
      }}>
        Ring ID: {ringId} • Generated: {new Date().toLocaleString()}
      </div>
      
      <div style={{
        display: 'flex',
        gap: '12px',
        flexWrap: 'wrap'
      }}>
        <button
          onClick={() => handleDownload('pdf')}
          disabled={loading}
          style={{
            background: '#dc2626',
            color: 'white',
            border: 'none',
            padding: '10px 16px',
            borderRadius: '6px',
            fontSize: '13px',
            fontWeight: '500',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1,
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => {
            if (!loading) e.target.style.background = '#b91c1c';
          }}
          onMouseOut={(e) => {
            if (!loading) e.target.style.background = '#dc2626';
          }}
        >
          📄 PDF Report
        </button>
        
        <button
          onClick={() => handleDownload('excel')}
          disabled={loading}
          style={{
            background: '#16a34a',
            color: 'white',
            border: 'none',
            padding: '10px 16px',
            borderRadius: '6px',
            fontSize: '13px',
            fontWeight: '500',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1,
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => {
            if (!loading) e.target.style.background = '#15803d';
          }}
          onMouseOut={(e) => {
            if (!loading) e.target.style.background = '#16a34a';
          }}
        >
          📊 Excel Data
        </button>
      </div>
      
      {loading && (
        <div style={{
          marginTop: '12px',
          fontSize: '12px',
          color: '#10a37f'
        }}>
          Preparing download...
        </div>
      )}
    </div>
  );
};

export default SimpleExportButtons;

import React, { useState, useEffect } from 'react';
import { useExport } from '../hooks/useExport';

const ExportDownload = ({ ringId, messageText }) => {
  const { generateExport, downloadDemo, loading } = useExport();
  const [exportData, setExportData] = useState(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (ringId) {
      generateExport(ringId, 'both')
        .then(setExportData)
        .catch(() => {
          setExportData({
            success: false,
            ring_id: ringId,
            error: 'Using demo data for testing',
            generated_at: new Date().toISOString()
          });
        });
      
      // Animate in after a short delay
      setTimeout(() => setIsVisible(true), 300);
    }
  }, [ringId, generateExport]);

  const handleDownload = (fileType) => {
    downloadDemo(ringId || 'demo', fileType);
  };

  if (!exportData) return null;

  return (
    <div 
      style={{
        ...styles.container,
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0)' : 'translateY(10px)',
        transition: 'all 0.3s ease-out'
      }}
    >
      {/* Header with icon */}
      <div style={styles.header}>
        <div style={styles.iconContainer}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14,2 14,8 20,8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10,9 9,9 8,9"/>
          </svg>
        </div>
        <div style={styles.titleContainer}>
          <h4 style={styles.title}>Export Analysis Report</h4>
          <p style={styles.subtitle}>Download comprehensive fraud ring analysis</p>
        </div>
        <div style={styles.badge}>
          Ready
        </div>
      </div>

      {/* Info section */}
      <div style={styles.infoSection}>
        <div style={styles.infoGrid}>
          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>Ring ID:</span>
            <span style={styles.infoValue}>{exportData.ring_id}</span>
          </div>
          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>Generated:</span>
            <span style={styles.infoValue}>
              {new Date(exportData.generated_at).toLocaleString()}
            </span>
          </div>
          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>Status:</span>
            <span style={styles.infoValue}>
              {exportData.success ? 'Production Data' : 'Demo Data'}
            </span>
          </div>
        </div>
        
        {exportData.error && (
          <div style={styles.noteContainer}>
            <div style={styles.noteIcon}>ℹ️</div>
            <span style={styles.noteText}>{exportData.error}</span>
          </div>
        )}
      </div>

      {/* Report contents preview */}
      <div style={styles.previewSection}>
        <h5 style={styles.previewTitle}>📋 Report Contents</h5>
        <div style={styles.previewGrid}>
          <div style={styles.previewItem}>
            <span style={styles.previewIcon}>📊</span>
            <span style={styles.previewText}>Executive Summary & Risk Analysis</span>
          </div>
          <div style={styles.previewItem}>
            <span style={styles.previewIcon}>🔍</span>
            <span style={styles.previewText}>Entity Relationships & Patterns</span>
          </div>
          <div style={styles.previewItem}>
            <span style={styles.previewIcon}>💰</span>
            <span style={styles.previewText}>Transaction Analysis & Monitoring</span>
          </div>
          <div style={styles.previewItem}>
            <span style={styles.previewIcon}>🎯</span>
            <span style={styles.previewText}>Actionable Recommendations</span>
          </div>
        </div>
      </div>

      {/* Download buttons */}
      <div style={styles.buttonContainer}>
        <button
          onClick={() => handleDownload('pdf')}
          disabled={loading}
          style={{
            ...styles.button,
            ...styles.pdfButton,
            opacity: loading ? 0.6 : 1
          }}
          onMouseOver={(e) => {
            if (!loading) {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 8px 25px rgba(220, 38, 38, 0.3)';
            }
          }}
          onMouseOut={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
          }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14,2 14,8 20,8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          <span>Download PDF Report</span>
        </button>
        
        <button
          onClick={() => handleDownload('excel')}
          disabled={loading}
          style={{
            ...styles.button,
            ...styles.excelButton,
            opacity: loading ? 0.6 : 1
          }}
          onMouseOver={(e) => {
            if (!loading) {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 8px 25px rgba(34, 197, 94, 0.3)';
            }
          }}
          onMouseOut={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
          }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14,2 14,8 20,8"/>
            <rect x="8" y="13" width="8" height="7"/>
            <line x1="8" y1="17" x2="16" y2="17"/>
            <line x1="12" y1="13" x2="12" y2="20"/>
          </svg>
          <span>Download Excel Data</span>
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: {
    background: 'linear-gradient(145deg, #1e1e1e 0%, #2a2a2a 100%)',
    border: '1px solid #404040',
    borderRadius: '12px',
    padding: '24px',
    marginTop: '24px',
    fontFamily: '"Söhne", ui-sans-serif, system-ui, -apple-system, sans-serif',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)',
    position: 'relative',
    overflow: 'hidden'
  },
  header: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '16px',
    marginBottom: '20px',
    paddingBottom: '16px',
    borderBottom: '1px solid #333333'
  },
  iconContainer: {
    width: '40px',
    height: '40px',
    borderRadius: '8px',
    background: 'linear-gradient(135deg, #10a37f, #0d8f72)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    flexShrink: 0
  },
  titleContainer: {
    flex: 1
  },
  title: {
    margin: 0,
    fontSize: '18px',
    fontWeight: '600',
    color: '#ececec',
    marginBottom: '4px'
  },
  subtitle: {
    margin: 0,
    fontSize: '14px',
    color: '#8e8ea0'
  },
  badge: {
    background: 'linear-gradient(135deg, #10a37f, #0d8f72)',
    color: 'white',
    padding: '4px 12px',
    borderRadius: '16px',
    fontSize: '12px',
    fontWeight: '500'
  },
  infoSection: {
    marginBottom: '20px'
  },
  infoGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '12px',
    marginBottom: '16px'
  },
  infoItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '8px 12px',
    background: '#262626',
    borderRadius: '6px',
    border: '1px solid #333333'
  },
  infoLabel: {
    fontSize: '13px',
    color: '#8e8ea0',
    fontWeight: '500'
  },
  infoValue: {
    fontSize: '13px',
    color: '#ececec',
    fontWeight: '600'
  },
  noteContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '12px',
    background: 'rgba(255, 149, 0, 0.1)',
    border: '1px solid rgba(255, 149, 0, 0.2)',
    borderRadius: '8px'
  },
  noteIcon: {
    fontSize: '16px'
  },
  noteText: {
    fontSize: '13px',
    color: '#ff9500',
    fontWeight: '500'
  },
  previewSection: {
    marginBottom: '24px'
  },
  previewTitle: {
    margin: '0 0 16px 0',
    fontSize: '16px',
    fontWeight: '600',
    color: '#ececec'
  },
  previewGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '8px'
  },
  previewItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px',
    background: '#262626',
    borderRadius: '8px',
    border: '1px solid #333333'
  },
  previewIcon: {
    fontSize: '16px'
  },
  previewText: {
    fontSize: '13px',
    color: '#8e8ea0',
    fontWeight: '500'
  },
  buttonContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px'
  },
  button: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px',
    padding: '16px 24px',
    borderRadius: '10px',
    border: 'none',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
    minHeight: '52px'
  },
  pdfButton: {
    background: 'linear-gradient(135deg, #dc2626, #b91c1c)',
    color: 'white'
  },
  excelButton: {
    background: 'linear-gradient(135deg, #22c55e, #16a34a)',
    color: 'white'
  }
};

export default ExportDownload;

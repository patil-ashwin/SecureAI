// src/components/ExportDownload.jsx
import React from 'react';
import styles from './ExportDownload.module.css';

const ExportDownload = ({ exportData, loading = false }) => {
  // Download handler
  const downloadFile = (base64Data, filename, mimeType) => {
    try {
      const byteCharacters = atob(base64Data);
      const byteArray = new Uint8Array(byteCharacters.length);
      
      for (let i = 0; i < byteCharacters.length; i++) {
        byteArray[i] = byteCharacters.charCodeAt(i);
      }
      
      const blob = new Blob([byteArray], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      
      link.href = url;
      link.download = filename;
      link.click();
      
      URL.revokeObjectURL(url);
      console.log(`✅ Downloaded: ${filename}`);
    } catch (error) {
      console.error(`❌ Download failed for ${filename}:`, error);
      alert(`Download failed: ${error.message}`);
    }
  };

  const handlePDFDownload = () => {
    if (exportData?.pdf_data && exportData?.pdf_filename) {
      downloadFile(exportData.pdf_data, exportData.pdf_filename, 'application/pdf');
    }
  };

  const handleExcelDownload = () => {
    if (exportData?.excel_data && exportData?.excel_filename) {
      downloadFile(
        exportData.excel_data, 
        exportData.excel_filename, 
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      );
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingContainer}>
          <div className={styles.spinner}></div>
          <span className={styles.loadingText}>Generating export files...</span>
        </div>
      </div>
    );
  }

  if (!exportData?.success) {
    return (
      <div className={styles.container}>
        <div className={styles.errorContainer}>
          <span className={styles.errorIcon}>❌</span>
          <span className={styles.errorText}>
            {exportData?.error || 'Export generation failed'}
          </span>
          {exportData?.note && (
            <div className={styles.noteText}>💡 {exportData.note}</div>
          )}
        </div>
      </div>
    );
  }

  const hasPDF = exportData?.pdf_data && exportData?.pdf_filename;
  const hasExcel = exportData?.excel_data && exportData?.excel_filename;

  return (
    <div className={styles.container}>
      <div className={styles.successContainer}>
        <span className={styles.successIcon}>✅</span>
        <span className={styles.successText}>
          Export generated successfully for Ring {exportData.ring_id}
        </span>
      </div>
      
      <div className={styles.buttonContainer}>
        {hasPDF && (
          <button 
            className={`${styles.downloadButton} ${styles.pdfButton}`}
            onClick={handlePDFDownload}
            title={exportData.pdf_filename}
          >
            <span className={styles.buttonIcon}>📄</span>
            <span className={styles.buttonText}>Download PDF</span>
          </button>
        )}
        
        {hasExcel && (
          <button 
            className={`${styles.downloadButton} ${styles.excelButton}`}
            onClick={handleExcelDownload}
            title={exportData.excel_filename}
          >
            <span className={styles.buttonIcon}>📊</span>
            <span className={styles.buttonText}>Download Excel</span>
          </button>
        )}
      </div>

      {exportData?.generated_at && (
        <div className={styles.timestamp}>
          Generated: {new Date(exportData.generated_at).toLocaleString()}
        </div>
      )}
    </div>
  );
};

export default ExportDownload;
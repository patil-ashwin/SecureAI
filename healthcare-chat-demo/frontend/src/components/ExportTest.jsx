import React from 'react';
import { ExportDownload } from './export';

// Test component to verify export functionality
const ExportTest = () => {
  const testExportData = {
    success: true,
    ring_id: "123456",
    generated_at: new Date().toISOString(),
    pdf_data: null, // null will trigger demo download
    excel_data: null // null will trigger demo download
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px' }}>
      <h2>Export Functionality Test</h2>
      <p>This component tests the export download buttons:</p>
      
      <ExportDownload 
        exportData={testExportData}
        loading={false}
      />
    </div>
  );
};

export default ExportTest;

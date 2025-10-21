import React, { useState, useEffect } from 'react';
import { ExportDownload } from './export';
import { useExport } from '../hooks/useExport';

// Example showing how to integrate export into your existing analysis component
const AnalysisResultsWithExport = ({ message, result }) => {
  const { generateExport } = useExport();
  const [exportData, setExportData] = useState(null);
  
  // Auto-generate export when analysis completes
  useEffect(() => {
    if (result && result.intent === 'ring_explanation') {
      // Extract ring ID from various possible sources
      const ringId = result.parameters?.ring_id || 
                    result.raw_result?.ring_id ||
                    message.text.match(/ring\s+(\d+)/i)?.[1] ||
                    '123456'; // fallback for demo
      
      if (ringId) {
        handleGenerateExport(ringId);
      }
    }
  }, [result]);
  
  const handleGenerateExport = async (ringId) => {
    try {
      const exportResult = await generateExport(ringId, 'both');
      setExportData(exportResult);
    } catch (error) {
      console.error('Export generation failed:', error);
      // Still show export component with demo functionality
      setExportData({
        success: false,
        ring_id: ringId,
        error: error.message,
        generated_at: new Date().toISOString()
      });
    }
  };

  return (
    <div className="analysis-results">
      {/* Your existing analysis display */}
      <div className="executive-summary">
        <h3>Executive Summary</h3>
        <p>{result?.explanation || 'Analysis results would appear here...'}</p>
      </div>
      
      <div className="ring-composition">
        <h3>Ring Composition</h3>
        {/* Your existing ring composition display */}
      </div>
      
      <div className="risk-assessment">
        <h3>Risk Assessment</h3>
        {/* Your existing risk assessment display */}
      </div>
      
      {/* ADD THIS: Export functionality at the bottom */}
      {exportData && (
        <ExportDownload 
          exportData={exportData}
          loading={false}
        />
      )}
    </div>
  );
};

export default AnalysisResultsWithExport;

// Usage instructions:
// 1. Import this component or copy the export logic to your existing component
// 2. Make sure your component receives 'message' and 'result' props
// 3. The export buttons will appear automatically after analysis completes
// 4. Ring ID will be extracted from result.parameters.ring_id or message text

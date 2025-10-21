import React from 'react';
import SimpleExportButtons from './SimpleExportButtons';
import { isRingAnalysis, extractRingId } from '../utils/ringDetector';

const ExportOnlyTest = () => {
  const testText = "Executive Summary\n\nRing 345453 is comprised of 15 entities...";
  const hasRing = isRingAnalysis(testText);
  const ringId = extractRingId("export ring 345453");

  return (
    <div style={{ 
      padding: '20px', 
      maxWidth: '600px', 
      margin: '0 auto',
      backgroundColor: '#0d1117',
      color: '#ececec',
      fontFamily: 'system-ui'
    }}>
      <h2 style={{ color: '#10a37f' }}>Export Test</h2>
      <p>Ring detection: {hasRing ? '✅ Detected' : '❌ Not detected'}</p>
      <p>Ring ID: {ringId || 'Not found'}</p>
      
      <div style={{
        background: '#1a1a1a',
        border: '1px solid #333',
        borderRadius: '8px',
        padding: '16px',
        marginTop: '20px'
      }}>
        <p>Sample ring analysis text...</p>
        <SimpleExportButtons ringId="345453" />
      </div>
    </div>
  );
};

export default ExportOnlyTest;

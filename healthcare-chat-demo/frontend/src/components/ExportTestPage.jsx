import React from 'react';
import ExportDownload from './ExportDownload';
import { formatAnalysisText } from '../utils/textFormatter';

const ExportTestPage = () => {
  const sampleAnalysisText = `**Executive Summary**

Ring 345453 is comprised of 15 entities with a total of 8 DDA accounts and 3 RPS accounts.

---

**1. Ring Composition**

**15** Entities Identified:
- **4** PAE Entities (Personal Account Entities)
- **2** PE Entities  
- **9** All Accounts (identified including open and closed)

**2. Risk Assessment**

Average PAE Risk Score: **0.152**, indicating moderate risk across the ring.

**3. Key Findings**

**Multiple High-Risk Entities:** The presence of 4 PAE entities within a single ring is a significant red flag for coordinated fraudulent activity.`;

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto', backgroundColor: '#0d1117', minHeight: '100vh', color: '#ececec' }}>
      <h1 style={{ color: '#10a37f', marginBottom: '20px' }}>Export Functionality Test</h1>
      
      <div style={{ marginBottom: '30px' }}>
        <h2>Original Analysis (with formatting issues):</h2>
        <div style={{ background: '#1a1a1a', padding: '15px', borderRadius: '8px', marginBottom: '20px', whiteSpace: 'pre-wrap' }}>
          {sampleAnalysisText}
        </div>
      </div>
      
      <div style={{ marginBottom: '30px' }}>
        <h2>Fixed Analysis (with export buttons):</h2>
        <div style={{ background: '#1a1a1a', padding: '15px', borderRadius: '8px' }}>
          <div dangerouslySetInnerHTML={{ __html: formatAnalysisText(sampleAnalysisText) }} />
          <ExportDownload ringId="345453" messageText={sampleAnalysisText} />
        </div>
      </div>
      
      <div style={{ background: '#1a1a1a', padding: '15px', borderRadius: '8px', border: '1px solid #404040' }}>
        <h3 style={{ color: '#10a37f' }}>Integration Instructions:</h3>
        <ol style={{ color: '#8e8ea0', lineHeight: '1.6' }}>
          <li>The MessageBubble component has been updated automatically</li>
          <li>Export buttons will appear for any message containing ring analysis</li>
          <li>Markdown formatting (** and ---) is now properly converted to HTML</li>
          <li>Download buttons work with demo data for testing</li>
        </ol>
      </div>
    </div>
  );
};

export default ExportTestPage;

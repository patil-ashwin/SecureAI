import React from 'react';
import ExportDownload from './ExportDownload';
import { formatAnalysisText, isRingAnalysis, extractRingId } from '../utils/textFormatter';

const ComprehensiveTestPage = () => {
  const sampleAnalysisText = `**Executive Summary**

Ring 345453 is comprised of 15 entities with a total of 8 DDA accounts and 3 RPS accounts. The investigation highlights several high-risk entities and advanced methods, highlighting techniques and associated links and tactics. PAE risk level of 0.192, including a moderate risk profile. The investigation pinpoints several high-risk entities and advanced methods, highlighting patterns associated with data trends.

---

1. **Ring Composition**

**15** Entities Identified:
- **4** PAE Entities (Personal Account Entities)
- **2** PE Entities  
- **9** All Accounts (identified including open and closed)
- **2** Closed Accounts
- **3** Addresses: 3 distinct geographical locations
- **2** Payment Methods: 2 Zelle tokens with multiple sender associations  
- **1** Emails: 1 associated email address

2. **Risk Assessment**

Average PAE Risk Score: **0.152**, indicating moderate risk across the ring.
- **High-Risk Indicators:** 
- Multiple PAE entities related to the same network
- Account closures with recent account openings, suggesting possible detection or internal controls
- Zelle tokens with multiple sender associations, indicating potential money movement bypassing

# Key Findings

- **Multiple PAE Entities:** The presence of 4 PAE entities within a single ring is a significant red flag for coordinated fraudulent activity.
- **Account Closure Timing:** The recent closure of two accounts suggests possible reaction to detection or internal controls.
- **Payment Method Abuse:** Zelle tokens with multiple sender counts suggest potential exploitation of digital payment methods for rapid fund movement.
- **Geographic Diversity:** The use of at least two distinct addresses indicates a distribution network to coordinate fraudulent activitie bypassed by multiple sender associations.`;

  const isRing = isRingAnalysis(sampleAnalysisText);
  const ringId = extractRingId(sampleAnalysisText);

  return (
    <div style={{ 
      padding: '40px 20px', 
      maxWidth: '1200px', 
      margin: '0 auto', 
      backgroundColor: '#0d1117', 
      minHeight: '100vh', 
      color: '#ececec',
      fontFamily: '"Söhne", ui-sans-serif, system-ui, -apple-system, sans-serif'
    }}>
      <div style={{
        textAlign: 'center',
        marginBottom: '40px',
        padding: '20px',
        background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)',
        borderRadius: '12px',
        border: '1px solid #404040'
      }}>
        <h1 style={{ color: '#10a37f', marginBottom: '16px', fontSize: '32px' }}>
          Comprehensive Fix Verification
        </h1>
        <p style={{ color: '#8e8ea0', fontSize: '18px', margin: 0 }}>
          Testing all fixes: Export buttons, formatting, professional styling
        </p>
      </div>
      
      <div style={{ marginBottom: '40px' }}>
        <h2 style={{ color: '#ececec', marginBottom: '20px' }}>Before Fix (Raw Text):</h2>
        <div style={{ 
          background: '#1a1a1a', 
          padding: '20px', 
          borderRadius: '8px', 
          marginBottom: '20px', 
          whiteSpace: 'pre-wrap',
          border: '1px solid #333',
          fontSize: '14px',
          color: '#8e8ea0'
        }}>
          {sampleAnalysisText}
        </div>
      </div>
      
      <div style={{ marginBottom: '40px' }}>
        <h2 style={{ color: '#ececec', marginBottom: '20px' }}>After Fix (Professional Display):</h2>
        
        {/* Professional message container with border */}
        <div style={{
          border: '1px solid #404040',
          borderRadius: '12px',
          background: 'linear-gradient(145deg, #1a1a1a 0%, #1e1e1e 100%)',
          overflow: 'hidden',
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)'
        }}>
          <div style={{
            padding: '24px',
            color: '#ececec',
            lineHeight: '1.7',
            fontSize: '15px'
          }}>
            <div dangerouslySetInnerHTML={{ __html: formatAnalysisText(sampleAnalysisText) }} />
            
            {/* Export functionality */}
            {isRing && ringId && (
              <ExportDownload ringId={ringId} messageText={sampleAnalysisText} />
            )}
          </div>
        </div>
      </div>
      
      <div style={{
        background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)',
        padding: '24px',
        borderRadius: '12px',
        border: '1px solid #404040'
      }}>
        <h3 style={{ color: '#10a37f', marginBottom: '16px' }}>✅ Fixes Applied:</h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '16px',
          color: '#8e8ea0',
          lineHeight: '1.6'
        }}>
          <div>
            <strong style={{ color: '#ececec' }}>Export Functionality:</strong>
            <ul style={{ marginLeft: '20px', marginTop: '8px' }}>
              <li>✅ PDF and Excel download buttons</li>
              <li>✅ Auto-detection of ring analysis</li>
              <li>✅ Professional styling with animations</li>
              <li>✅ Demo data for immediate testing</li>
            </ul>
          </div>
          <div>
            <strong style={{ color: '#ececec' }}>Text Formatting:</strong>
            <ul style={{ marginLeft: '20px', marginTop: '8px' }}>
              <li>✅ **bold text** → <strong>bold text</strong></li>
              <li>✅ Removed --- horizontal lines</li>
              <li>✅ Fixed bullet point spacing</li>
              <li>✅ Proper section headers</li>
            </ul>
          </div>
          <div>
            <strong style={{ color: '#ececec' }}>Professional Styling:</strong>
            <ul style={{ marginLeft: '20px', marginTop: '8px' }}>
              <li>✅ Thin professional border</li>
              <li>✅ Gradient backgrounds</li>
              <li>✅ Proper typography</li>
              <li>✅ Responsive design</li>
            </ul>
          </div>
          <div>
            <strong style={{ color: '#ececec' }}>Content Issues:</strong>
            <ul style={{ marginLeft: '20px', marginTop: '8px' }}>
              <li>✅ No more response truncation</li>
              <li>✅ Fixed indentation issues</li>
              <li>✅ Proper line spacing</li>
              <li>✅ Complete content display</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComprehensiveTestPage;

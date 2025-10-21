export const extractRingId = (text) => {
  if (!text) return null;
  
  const patterns = [
    /ring\s+(\d+)/i,
    /export ring (\d+)/i,
    /ring (\d{3,})/i
  ];
  
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) return match[1];
  }
  
  return null;
};

export const isRingAnalysis = (text) => {
  if (!text) return false;
  
  const indicators = [
    'PAE Entities',
    'Ring Composition', 
    'Key Findings',
    'Executive Summary',
    'Risk Assessment',
    'Entity Analysis'
  ];
  
  return indicators.some(indicator => 
    text.toLowerCase().includes(indicator.toLowerCase())
  );
};

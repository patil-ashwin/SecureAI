import React, { useState, useEffect } from 'react';
import './App.css';

// Icons (using Unicode symbols for simplicity)
const Shield = () => <span className="nav-icon">🛡️</span>;
const Settings = () => <span className="nav-icon">⚙️</span>;
const Eye = () => <span className="nav-icon">👁️</span>;
const FileText = () => <span className="nav-icon">📄</span>;
const Users = () => <span className="nav-icon">👥</span>;
const Activity = () => <span className="nav-icon">📊</span>;
const Database = () => <span className="nav-icon">🗄️</span>;
const AlertTriangle = () => <span className="nav-icon">⚠️</span>;

interface MaskingPattern {
  type: 'show_first' | 'show_last' | 'show_first_last' | 'full_mask' | 'custom';
  showFirst?: number;
  showLast?: number;
  maskChar: string;
  separator?: string;
  preserveFormat?: boolean;
}

interface ConfigData {
  phiDetection: {
    enabled: boolean;
    confidence: number;
    entities: string[];
    realTimeDetection: boolean;
  };
  maskingStrategies: {
    [key: string]: {
      enabled: boolean;
      pattern: MaskingPattern;
      context: string[];
      description?: string;
    };
  };
  auditSettings: {
    enabled: boolean;
    logLevel: string;
    retentionDays: number;
    realTimeAlerts: boolean;
  };
  roleBasedAccess: {
    [role: string]: {
      phiAccess: string;
      canDecrypt: boolean;
      canGeneratePDF: boolean;
      allowedEntities: string[];
    };
  };
  systemSettings: {
    apiEndpoint: string;
    encryptionKey: string;
    syncInterval: number;
    offlineMode: boolean;
  };
}

const defaultConfig: ConfigData = {
  phiDetection: {
    enabled: true,
    confidence: 0.6,
    entities: ['PERSON', 'EMAIL', 'PHONE', 'SSN', 'CREDIT_CARD', 'DATE_OF_BIRTH', 'ADDRESS'],
    realTimeDetection: true
  },
  maskingStrategies: {
    'PERSON': {
      enabled: true,
      pattern: {
        type: 'show_first',
        showFirst: 1,
        showLast: 0,
        maskChar: '*',
        preserveFormat: false
      },
      context: ['API', 'LLM', 'LOGS'],
      description: 'Show first initial, mask rest (e.g., J*** S***)'
    },
    'EMAIL': {
      enabled: true,
      pattern: {
        type: 'custom',
        showFirst: 1,
        showLast: 0,
        maskChar: '*',
        separator: '@',
        preserveFormat: true
      },
      context: ['LOGS', 'API'],
      description: 'Show first char and domain (e.g., j***@company.com)'
    },
    'PHONE': {
      enabled: true,
      pattern: {
        type: 'show_last',
        showFirst: 0,
        showLast: 4,
        maskChar: '*',
        preserveFormat: true
      },
      context: ['API', 'LLM', 'LOGS'],
      description: 'Show last 4 digits (e.g., ***-***-1234)'
    },
    'SSN': {
      enabled: true,
      pattern: {
        type: 'show_last',
        showFirst: 0,
        showLast: 4,
        maskChar: '*',
        preserveFormat: true
      },
      context: ['API', 'LLM'],
      description: 'Show last 4 digits (e.g., ***-**-1234)'
    },
    'CREDIT_CARD': {
      enabled: true,
      pattern: {
        type: 'show_first_last',
        showFirst: 4,
        showLast: 4,
        maskChar: '*',
        preserveFormat: true
      },
      context: ['DATABASE', 'API', 'LOGS'],
      description: 'Show first 4 and last 4 (e.g., 1234-****-****-5678)'
    },
    'DATE_OF_BIRTH': {
      enabled: true,
      pattern: {
        type: 'show_last',
        showLast: 4,
        showFirst: 0,
        maskChar: '*',
        preserveFormat: true
      },
      context: ['LOGS'],
      description: 'Show only year (e.g., **/**/1985)'
    },
    'ADDRESS': {
      enabled: true,
      pattern: {
        type: 'show_last',
        showLast: 15,
        showFirst: 0,
        maskChar: '*',
        preserveFormat: false
      },
      context: ['LOGS'],
      description: 'Show city/state only'
    }
  },
  auditSettings: {
    enabled: true,
    logLevel: 'INFO',
    retentionDays: 90,
    realTimeAlerts: true
  },
  roleBasedAccess: {
    'doctor': {
      phiAccess: 'full',
      canDecrypt: true,
      canGeneratePDF: true,
      allowedEntities: ['PERSON', 'EMAIL', 'PHONE', 'SSN', 'DATE_OF_BIRTH']
    },
    'nurse': {
      phiAccess: 'masked',
      canDecrypt: false,
      canGeneratePDF: false,
      allowedEntities: ['PERSON', 'EMAIL']
    },
    'supervisor': {
      phiAccess: 'full',
      canDecrypt: true,
      canGeneratePDF: true,
      allowedEntities: ['PERSON', 'EMAIL', 'PHONE', 'SSN', 'CREDIT_CARD', 'DATE_OF_BIRTH']
    },
    'admin': {
      phiAccess: 'full',
      canDecrypt: true,
      canGeneratePDF: true,
      allowedEntities: ['PERSON', 'EMAIL', 'PHONE', 'SSN', 'CREDIT_CARD', 'DATE_OF_BIRTH']
    }
  },
  systemSettings: {
    apiEndpoint: 'http://localhost:8003',
    encryptionKey: 'healthcare-phi-key',
    syncInterval: 5,
    offlineMode: true
  }
};

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('phi-detection');
  const [config, setConfig] = useState<ConfigData>(defaultConfig);
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState<{type: string, message: string} | null>(null);

  // Load configuration from backend on startup
  useEffect(() => {
    const loadConfiguration = async () => {
      try {
        const response = await fetch(`${config.systemSettings.apiEndpoint}/api/config`);
        if (response.ok) {
          const data = await response.json();
          setConfig(data);
          console.log('Configuration loaded from backend');
        }
      } catch (error) {
        console.log('Using default configuration');
      }
    };

    loadConfiguration();
  }, []);

  // Real-time configuration sync
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${config.systemSettings.apiEndpoint}/api/config`);
        if (response.ok) {
          const data = await response.json();
          setConfig(data);
          console.log('Configuration synced from backend');
        }
      } catch (error) {
        console.log('Configuration sync failed, using cached config');
      }
    }, config.systemSettings.syncInterval * 60 * 1000); // Convert minutes to milliseconds

    return () => clearInterval(interval);
  }, [config.systemSettings.syncInterval, config.systemSettings.apiEndpoint]);

  const showNotification = (type: string, message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 3000);
  };

  const updateConfig = (section: keyof ConfigData, updates: any) => {
    setConfig(prev => ({
      ...prev,
      [section]: { ...prev[section], ...updates }
    }));
    showNotification('success', 'Configuration updated successfully!');
  };

  const saveConfiguration = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${config.systemSettings.apiEndpoint}/api/config`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
      });

      if (!response.ok) {
        throw new Error('Failed to save configuration');
      }

      showNotification('success', 'Configuration saved and applied to all services!');
    } catch (error) {
      showNotification('error', 'Failed to save configuration');
      console.error('Configuration save error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const resetConfiguration = () => {
    setConfig(defaultConfig);
    showNotification('warning', 'Configuration reset to defaults');
  };

  const renderPHIDetection = () => (
    <div className="card">
      <div className="card-header">
        <div>
          <h3 className="card-title">PHI Detection Settings</h3>
          <p className="card-subtitle">Configure automatic PII/PHI detection and protection</p>
        </div>
        <div className="toggle">
          <input
            type="checkbox"
            checked={config.phiDetection.enabled}
            onChange={(e) => updateConfig('phiDetection', { enabled: e.target.checked })}
          />
          <span className="toggle-slider"></span>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="form-group">
          <label className="form-label">Detection Confidence</label>
          <input
            type="range"
            min="0.1"
            max="1.0"
            step="0.1"
            value={config.phiDetection.confidence}
            onChange={(e) => updateConfig('phiDetection', { confidence: parseFloat(e.target.value) })}
            className="form-input"
          />
          <div style={{ color: '#a0a0a0', fontSize: '0.8rem', marginTop: '0.25rem' }}>
            {config.phiDetection.confidence}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Real-time Detection</label>
          <div className="toggle">
            <input
              type="checkbox"
              checked={config.phiDetection.realTimeDetection}
              onChange={(e) => updateConfig('phiDetection', { realTimeDetection: e.target.checked })}
            />
            <span className="toggle-slider"></span>
          </div>
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Detected Entities</label>
        <div className="grid grid-3">
          {config.phiDetection.entities.map((entity, index) => (
            <div key={index} className="badge badge-info">
              {entity}
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderMaskingStrategies = () => (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Character-Based Masking Strategies</h3>
        <p className="card-subtitle">Configure pattern-based masking for different PII entities</p>
      </div>

      {Object.entries(config.maskingStrategies).map(([entity, strategy]) => (
        <div key={entity} className="card" style={{ marginBottom: '1rem' }}>
          <div className="card-header">
            <div>
              <h4 style={{ color: '#ffffff', fontSize: '1rem' }}>{entity}</h4>
              <p style={{ color: '#a0a0a0', fontSize: '0.8rem' }}>{strategy.description || `Pattern-based masking for ${entity}`}</p>
            </div>
            <div className="toggle">
              <input
                type="checkbox"
                checked={strategy.enabled}
                onChange={(e) => updateConfig('maskingStrategies', {
                  ...config.maskingStrategies,
                  [entity]: { ...strategy, enabled: e.target.checked }
                })}
              />
              <span className="toggle-slider"></span>
            </div>
          </div>

          <div className="grid grid-2">
            <div className="form-group">
              <label className="form-label">Masking Pattern</label>
              <select
                value={strategy.pattern.type}
                onChange={(e) => updateConfig('maskingStrategies', {
                  ...config.maskingStrategies,
                  [entity]: { 
                    ...strategy, 
                    pattern: { ...strategy.pattern, type: e.target.value as any }
                  }
                })}
                className="form-select"
              >
                <option value="show_first">Show First N Characters</option>
                <option value="show_last">Show Last N Characters</option>
                <option value="show_first_last">Show First & Last N Characters</option>
                <option value="full_mask">Full Masking</option>
                <option value="custom">Custom Pattern</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Mask Character</label>
              <input
                type="text"
                maxLength={1}
                value={strategy.pattern.maskChar}
                onChange={(e) => updateConfig('maskingStrategies', {
                  ...config.maskingStrategies,
                  [entity]: { 
                    ...strategy, 
                    pattern: { ...strategy.pattern, maskChar: e.target.value || '*' }
                  }
                })}
                className="form-input"
                placeholder="*"
              />
            </div>
          </div>

          <div className="grid grid-2">
            {(strategy.pattern.type === 'show_first' || strategy.pattern.type === 'show_first_last') && (
              <div className="form-group">
                <label className="form-label">Show First Characters</label>
                <input
                  type="number"
                  value={strategy.pattern.showFirst || 0}
                  onChange={(e) => updateConfig('maskingStrategies', {
                    ...config.maskingStrategies,
                    [entity]: { 
                      ...strategy, 
                      pattern: { ...strategy.pattern, showFirst: parseInt(e.target.value) || 0 }
                    }
                  })}
                  className="form-input"
                  min="0"
                  max="10"
                />
              </div>
            )}

            {(strategy.pattern.type === 'show_last' || strategy.pattern.type === 'show_first_last') && (
              <div className="form-group">
                <label className="form-label">Show Last Characters</label>
                <input
                  type="number"
                  value={strategy.pattern.showLast || 0}
                  onChange={(e) => updateConfig('maskingStrategies', {
                    ...config.maskingStrategies,
                    [entity]: { 
                      ...strategy, 
                      pattern: { ...strategy.pattern, showLast: parseInt(e.target.value) || 0 }
                    }
                  })}
                  className="form-input"
                  min="0"
                  max="10"
                />
              </div>
            )}
          </div>

          <div className="grid grid-2">
            <div className="form-group">
              <label className="form-label">Preserve Format (dashes, spaces)</label>
              <div className="toggle">
                <input
                  type="checkbox"
                  checked={strategy.pattern.preserveFormat || false}
                  onChange={(e) => updateConfig('maskingStrategies', {
                    ...config.maskingStrategies,
                    [entity]: { 
                      ...strategy, 
                      pattern: { ...strategy.pattern, preserveFormat: e.target.checked }
                    }
                  })}
                />
                <span className="toggle-slider"></span>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Context</label>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {strategy.context.map((ctx, index) => (
                  <span key={index} className="badge badge-success">{ctx}</span>
                ))}
              </div>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Live Preview</label>
            <div style={{ 
              padding: '0.75rem', 
              background: 'rgba(76, 158, 255, 0.1)', 
              borderRadius: '8px',
              color: '#4a9eff',
              fontFamily: 'monospace',
              fontSize: '0.9rem'
            }}>
              {(() => {
                // Sample data for each entity type
                const samples: Record<string, string> = {
                  'CREDIT_CARD': '4532-1234-5678-9012',
                  'SSN': '123-45-6789',
                  'PHONE': '555-123-4567',
                  'EMAIL': 'john.doe@company.com',
                  'PERSON': 'John Smith',
                  'DATE_OF_BIRTH': '01/15/1985',
                  'ADDRESS': '123 Main Street, New York, NY'
                };

                const sample = samples[entity] || 'Sample Text';
                const pattern = strategy.pattern;
                const maskChar = pattern.maskChar || '*';
                let text = sample;
                
                // Remove formatting if not preserving
                if (!pattern.preserveFormat) {
                  text = text.replace(/[-\s()\/]/g, '');
                }
                
                const textLen = text.length;
                let masked = '';

                if (pattern.type === 'full_mask') {
                  masked = maskChar.repeat(textLen);
                } else if (pattern.type === 'show_first') {
                  const showFirst = pattern.showFirst || 0;
                  if (textLen <= showFirst) {
                    masked = text;
                  } else {
                    masked = text.substring(0, showFirst) + maskChar.repeat(textLen - showFirst);
                  }
                } else if (pattern.type === 'show_last') {
                  const showLast = pattern.showLast || 0;
                  if (textLen <= showLast) {
                    masked = text;
                  } else {
                    masked = maskChar.repeat(textLen - showLast) + text.substring(textLen - showLast);
                  }
                } else if (pattern.type === 'show_first_last') {
                  const showFirst = pattern.showFirst || 0;
                  const showLast = pattern.showLast || 0;
                  if (textLen <= (showFirst + showLast)) {
                    masked = text;
                  } else {
                    const middleLen = textLen - showFirst - showLast;
                    masked = text.substring(0, showFirst) + maskChar.repeat(middleLen) + text.substring(textLen - showLast);
                  }
                } else if (pattern.type === 'custom' && entity === 'EMAIL') {
                  const parts = text.split('@');
                  if (parts.length === 2) {
                    const showFirst = pattern.showFirst || 1;
                    const localPart = parts[0];
                    const maskedLocal = localPart.substring(0, showFirst) + maskChar.repeat(Math.max(0, localPart.length - showFirst));
                    masked = maskedLocal + '@' + parts[1];
                  } else {
                    masked = text;
                  }
                } else {
                  masked = maskChar.repeat(textLen);
                }

                // Restore format if preserving
                if (pattern.preserveFormat && text !== sample) {
                  let result = '';
                  let maskedIdx = 0;
                  for (const char of sample) {
                    if (['-', ' ', '(', ')', '/'].includes(char)) {
                      result += char;
                    } else if (maskedIdx < masked.length) {
                      result += masked[maskedIdx];
                      maskedIdx++;
                    }
                  }
                  masked = result;
                }

                return (
                  <>
                    <div style={{ marginBottom: '0.5rem', color: '#888' }}>
                      Original: {sample}
                    </div>
                    <div style={{ color: '#4a9eff', fontWeight: 'bold' }}>
                      Masked: {masked}
                    </div>
                  </>
                );
              })()}
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderAuditSettings = () => (
    <div className="card">
      <div className="card-header">
        <div>
          <h3 className="card-title">Audit & Logging</h3>
          <p className="card-subtitle">Configure audit trail and logging settings</p>
        </div>
        <div className="toggle">
          <input
            type="checkbox"
            checked={config.auditSettings.enabled}
            onChange={(e) => updateConfig('auditSettings', { enabled: e.target.checked })}
          />
          <span className="toggle-slider"></span>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="form-group">
          <label className="form-label">Log Level</label>
          <select
            value={config.auditSettings.logLevel}
            onChange={(e) => updateConfig('auditSettings', { logLevel: e.target.value })}
            className="form-select"
          >
            <option value="DEBUG">DEBUG</option>
            <option value="INFO">INFO</option>
            <option value="WARN">WARN</option>
            <option value="ERROR">ERROR</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Retention (Days)</label>
          <input
            type="number"
            value={config.auditSettings.retentionDays}
            onChange={(e) => updateConfig('auditSettings', { retentionDays: parseInt(e.target.value) })}
            className="form-input"
            min="1"
            max="365"
          />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Real-time Alerts</label>
        <div className="toggle">
          <input
            type="checkbox"
            checked={config.auditSettings.realTimeAlerts}
            onChange={(e) => updateConfig('auditSettings', { realTimeAlerts: e.target.checked })}
          />
          <span className="toggle-slider"></span>
        </div>
      </div>
    </div>
  );

  const renderRoleBasedAccess = () => (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Role-Based Access Control</h3>
        <p className="card-subtitle">Configure PHI access permissions for different user roles</p>
      </div>

      {Object.entries(config.roleBasedAccess).map(([role, permissions]) => (
        <div key={role} className="card" style={{ marginBottom: '1rem' }}>
          <div className="card-header">
            <div>
              <h4 style={{ color: '#ffffff', fontSize: '1rem', textTransform: 'capitalize' }}>{role}</h4>
              <p style={{ color: '#a0a0a0', fontSize: '0.8rem' }}>Access permissions for {role} role</p>
            </div>
            <span className={`badge ${permissions.phiAccess === 'full' ? 'badge-success' : 'badge-warning'}`}>
              {permissions.phiAccess.toUpperCase()} ACCESS
            </span>
          </div>

          <div className="grid grid-2">
            <div className="form-group">
              <label className="form-label">PHI Access Level</label>
              <select
                value={permissions.phiAccess}
                onChange={(e) => updateConfig('roleBasedAccess', {
                  ...config.roleBasedAccess,
                  [role]: { ...permissions, phiAccess: e.target.value }
                })}
                className="form-select"
              >
                <option value="full">Full Access</option>
                <option value="masked">Masked Only</option>
                <option value="none">No Access</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Permissions</label>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                <div className="toggle">
                  <input
                    type="checkbox"
                    checked={permissions.canDecrypt}
                    onChange={(e) => updateConfig('roleBasedAccess', {
                      ...config.roleBasedAccess,
                      [role]: { ...permissions, canDecrypt: e.target.checked }
                    })}
                  />
                  <span className="toggle-slider"></span>
                </div>
                <span style={{ color: '#a0a0a0', fontSize: '0.8rem' }}>Can Decrypt</span>
                
                <div className="toggle">
                  <input
                    type="checkbox"
                    checked={permissions.canGeneratePDF}
                    onChange={(e) => updateConfig('roleBasedAccess', {
                      ...config.roleBasedAccess,
                      [role]: { ...permissions, canGeneratePDF: e.target.checked }
                    })}
                  />
                  <span className="toggle-slider"></span>
                </div>
                <span style={{ color: '#a0a0a0', fontSize: '0.8rem' }}>Can Generate PDF</span>
              </div>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Allowed Entities</label>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              {permissions.allowedEntities.map((entity, index) => (
                <span key={index} className="badge badge-info">{entity}</span>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderSystemSettings = () => (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">System Settings</h3>
        <p className="card-subtitle">Configure system-wide settings and API endpoints</p>
      </div>

      <div className="grid grid-2">
        <div className="form-group">
          <label className="form-label">API Endpoint</label>
          <input
            type="url"
            value={config.systemSettings.apiEndpoint}
            onChange={(e) => updateConfig('systemSettings', { apiEndpoint: e.target.value })}
            className="form-input"
            placeholder="http://localhost:8002"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Sync Interval (minutes)</label>
          <input
            type="number"
            value={config.systemSettings.syncInterval}
            onChange={(e) => updateConfig('systemSettings', { syncInterval: parseInt(e.target.value) })}
            className="form-input"
            min="1"
            max="60"
          />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Encryption Key</label>
        <input
          type="password"
          value={config.systemSettings.encryptionKey}
          onChange={(e) => updateConfig('systemSettings', { encryptionKey: e.target.value })}
          className="form-input"
          placeholder="Enter encryption key"
        />
      </div>

      <div className="form-group">
        <label className="form-label">Offline Mode</label>
        <div className="toggle">
          <input
            type="checkbox"
            checked={config.systemSettings.offlineMode}
            onChange={(e) => updateConfig('systemSettings', { offlineMode: e.target.checked })}
          />
          <span className="toggle-slider"></span>
        </div>
        <p style={{ color: '#a0a0a0', fontSize: '0.8rem', marginTop: '0.25rem' }}>
          Allow system to work without central platform connection
        </p>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'phi-detection':
        return renderPHIDetection();
      case 'masking-strategies':
        return renderMaskingStrategies();
      case 'audit-settings':
        return renderAuditSettings();
      case 'role-based-access':
        return renderRoleBasedAccess();
      case 'system-settings':
        return renderSystemSettings();
      default:
        return renderPHIDetection();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon">S</div>
            SecureAI Configuration
          </div>
          <div className="status-indicator">
            <div className="status-dot"></div>
            <span>Live Configuration</span>
          </div>
        </div>
      </header>

      <div className="main-layout">
        <nav className="sidebar">
          <ul className="sidebar-nav">
            <li className="nav-item">
              <a
                className={`nav-link ${activeTab === 'phi-detection' ? 'active' : ''}`}
                onClick={() => setActiveTab('phi-detection')}
                href="#"
              >
                <Shield />
                PHI Detection
              </a>
            </li>
            <li className="nav-item">
              <a
                className={`nav-link ${activeTab === 'masking-strategies' ? 'active' : ''}`}
                onClick={() => setActiveTab('masking-strategies')}
                href="#"
              >
                <Eye />
                Masking Strategies
              </a>
            </li>
            <li className="nav-item">
              <a
                className={`nav-link ${activeTab === 'audit-settings' ? 'active' : ''}`}
                onClick={() => setActiveTab('audit-settings')}
                href="#"
              >
                <FileText />
                Audit Settings
              </a>
            </li>
            <li className="nav-item">
              <a
                className={`nav-link ${activeTab === 'role-based-access' ? 'active' : ''}`}
                onClick={() => setActiveTab('role-based-access')}
                href="#"
              >
                <Users />
                Role-Based Access
              </a>
            </li>
            <li className="nav-item">
              <a
                className={`nav-link ${activeTab === 'system-settings' ? 'active' : ''}`}
                onClick={() => setActiveTab('system-settings')}
                href="#"
              >
                <Settings />
                System Settings
              </a>
            </li>
          </ul>
        </nav>

        <main className="content">
          <div className="content-header">
            <h1 className="content-title">
              {activeTab === 'phi-detection' && 'PHI Detection Configuration'}
              {activeTab === 'masking-strategies' && 'Masking Strategies'}
              {activeTab === 'audit-settings' && 'Audit & Logging Settings'}
              {activeTab === 'role-based-access' && 'Role-Based Access Control'}
              {activeTab === 'system-settings' && 'System Settings'}
            </h1>
            <p className="content-subtitle">
              Configure and manage SecureAI privacy protection settings in real-time
            </p>
          </div>

          {renderContent()}

          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Configuration Actions</h3>
              <p className="card-subtitle">Save, reset, or export your configuration</p>
            </div>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              <button
                className="btn btn-primary"
                onClick={saveConfiguration}
                disabled={isLoading}
              >
                {isLoading && <div className="spinner"></div>}
                Save Configuration
              </button>
              <button className="btn btn-secondary" onClick={resetConfiguration}>
                Reset to Defaults
              </button>
              <button className="btn btn-secondary">
                Export Configuration
              </button>
              <button className="btn btn-danger">
                Test Configuration
              </button>
            </div>
          </div>
        </main>
      </div>

      {notification && (
        <div className={`notification notification-${notification.type}`}>
          {notification.message}
        </div>
      )}
    </div>
  );
};

export default App;
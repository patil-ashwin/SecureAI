import React, { useState, useEffect } from 'react';
import './RoleSelector.css';

const RoleSelector = ({ onRoleChange }) => {
  const [roles, setRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState('general');
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRoles();
    // Load saved role from localStorage
    const savedRole = localStorage.getItem('user_role');
    const savedUsername = localStorage.getItem('username');
    if (savedRole) setSelectedRole(savedRole);
    if (savedUsername) setUsername(savedUsername);
  }, []);

  const fetchRoles = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/roles');
      const data = await response.json();
      setRoles(data.roles);
    } catch (error) {
      console.error('Failed to fetch roles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = (roleId) => {
    setSelectedRole(roleId);
    localStorage.setItem('user_role', roleId);
    onRoleChange(roleId);
  };

  const handleLogin = () => {
    if (username.trim()) {
      localStorage.setItem('username', username.trim());
      localStorage.setItem('user_role', selectedRole);
      onRoleChange(selectedRole);
    }
  };

  if (loading) {
    return <div className="role-selector">Loading roles...</div>;
  }

  const currentRole = roles.find(r => r.id === selectedRole);

  return (
    <div className="role-selector">
      <div className="role-header">
        <h3>👤 User Role & PHI Access</h3>
        <p>Select your role to determine PHI visibility</p>
      </div>
      
      <div className="login-section">
        <input
          type="text"
          placeholder="Enter your name"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="username-input"
        />
        <button onClick={handleLogin} className="login-btn">
          Login
        </button>
      </div>

      <div className="roles-grid">
        {roles.map((role) => (
          <div
            key={role.id}
            className={`role-card ${selectedRole === role.id ? 'selected' : ''}`}
            onClick={() => handleRoleChange(role.id)}
          >
            <div className="role-icon">
              {role.id === 'doctor' && '👨‍⚕️'}
              {role.id === 'nurse' && '👩‍⚕️'}
              {role.id === 'admin' && '👨‍💼'}
              {role.id === 'general' && '👤'}
            </div>
            <div className="role-info">
              <h4>{role.name}</h4>
              <p>{role.description}</p>
              <div className={`phi-badge ${role.phi_access}`}>
                PHI: {role.phi_access === 'full' ? 'Visible' : 'Masked'}
              </div>
            </div>
          </div>
        ))}
      </div>

      {currentRole && (
        <div className="current-role">
          <strong>Current Role:</strong> {currentRole.name} 
          <span className={`phi-status ${currentRole.phi_access}`}>
            ({currentRole.phi_access === 'full' ? 'PHI Visible' : 'PHI Masked'})
          </span>
        </div>
      )}
    </div>
  );
};

export default RoleSelector;

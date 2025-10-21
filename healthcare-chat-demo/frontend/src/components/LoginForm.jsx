import React, { useState, useEffect } from 'react';
import './LoginForm.css';

const LoginForm = ({ onLogin, onCancel }) => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [loading, setLoading] = useState(true);
  const [loginLoading, setLoginLoading] = useState(false);
  const [error, setError] = useState('');

  const getPasswordForUser = (email) => {
    const passwords = {
      'dr.smith@hospital.com': 'doctor123',
      'supervisor.jones@hospital.com': 'super123',
      'nurse.wilson@hospital.com': 'nurse123',
      'admin@hospital.com': 'admin123'
    };
    return passwords[email] || 'password123';
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/users');
      const data = await response.json();
      setUsers(data.users);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async () => {
    if (!selectedUser) {
      setError('Please select a user');
      return;
    }

    setLoginLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8002/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: selectedUser,
          password: getPasswordForUser(selectedUser)
        })
      });

      const data = await response.json();

      if (data.success) {
        // Store auth info
        localStorage.setItem('auth_token', data.auth_token);
        localStorage.setItem('user_info', JSON.stringify(data.user));
        localStorage.setItem('user_role', data.user.role);
        localStorage.setItem('username', data.user.username);
        
        onLogin(data.user);
      } else {
        setError(data.message || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Login failed. Please try again.');
    } finally {
      setLoginLoading(false);
    }
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'doctor': return '👨‍⚕️';
      case 'supervisor': return '👨‍💼';
      case 'nurse': return '👩‍⚕️';
      case 'admin': return '🔧';
      default: return '👤';
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'doctor': return '#28a745';
      case 'supervisor': return '#007bff';
      case 'nurse': return '#ffc107';
      case 'admin': return '#6c757d';
      default: return '#6c757d';
    }
  };

  if (loading) {
    return (
      <div className="login-form">
        <div className="login-loading">
          <div className="spinner"></div>
          <p>Loading users...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="login-form">
      <div className="login-header">
        <h2>🏥 SecureAI Healthcare Login</h2>
        <p>Select a user to login and test role-based PHI access</p>
      </div>

      <div className="users-grid">
        {users.map((user) => (
          <div
            key={user.email}
            className={`user-card ${selectedUser === user.email ? 'selected' : ''}`}
            onClick={() => setSelectedUser(user.email)}
            style={{ borderColor: getRoleColor(user.role) }}
          >
            <div className="user-icon">
              {getRoleIcon(user.role)}
            </div>
            <div className="user-info">
              <h4>{user.username}</h4>
              <p className="user-email">{user.email}</p>
              <p className="user-role">{user.role.toUpperCase()}</p>
              <p className="user-department">{user.department}</p>
              <div className="user-permissions">
                <span className={`phi-badge ${user.phi_access}`}>
                  PHI: {user.phi_access === 'full' ? 'Visible' : 'Masked'}
                </span>
                {user.can_generate_pdf && (
                  <span className="pdf-badge">PDF</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="login-actions">
        <button
          onClick={handleLogin}
          disabled={!selectedUser || loginLoading}
          className="login-btn"
        >
          {loginLoading ? 'Logging in...' : 'Login'}
        </button>
        <button
          onClick={onCancel}
          className="cancel-btn"
        >
          Cancel
        </button>
      </div>

      <div className="login-footer">
        <p><strong>Demo Users:</strong></p>
        <ul>
          <li><strong>Doctor:</strong> Full PHI access, can generate PDFs</li>
          <li><strong>Supervisor:</strong> Full PHI access, can generate PDFs</li>
          <li><strong>Nurse:</strong> Masked PHI, cannot generate PDFs</li>
          <li><strong>Admin:</strong> Full PHI access, can generate PDFs</li>
        </ul>
      </div>
    </div>
  );
};

export default LoginForm;

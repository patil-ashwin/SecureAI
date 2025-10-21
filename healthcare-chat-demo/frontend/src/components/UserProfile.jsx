import React, { useState, useEffect } from 'react';
import './UserProfile.css';

const UserProfile = ({ onLogout }) => {
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    const authToken = localStorage.getItem('auth_token');
    if (!authToken) {
      onLogout();
      return;
    }

    try {
      const response = await fetch(`http://localhost:8002/api/profile?auth_token=${authToken}`);
      const data = await response.json();
      
      if (data.success) {
        setUserInfo(data.user);
      } else {
        onLogout();
      }
    } catch (error) {
      console.error('Failed to load profile:', error);
      onLogout();
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
    onLogout();
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
      <div className="user-profile">
        <div className="profile-loading">
          <div className="spinner"></div>
          <p>Loading profile...</p>
        </div>
      </div>
    );
  }

  if (!userInfo) {
    return null;
  }

  return (
    <div className="user-profile-minimal">
      <div className="profile-info">
        <div className="profile-avatar">
          {getRoleIcon(userInfo.role)}
        </div>
        <div className="profile-details">
          <span className="profile-name">{userInfo.username}</span>
          <span className="profile-role" style={{ color: getRoleColor(userInfo.role) }}>
            {userInfo.role.toUpperCase()}
          </span>
        </div>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </div>
    </div>
  );
};

export default UserProfile;

import React from 'react';
import './TimeBasedGreeting.css';

const TimeBasedGreeting = ({ userInfo }) => {
  const getTimeBasedGreeting = () => {
    const hour = new Date().getHours();
    
    if (hour >= 5 && hour < 12) {
      return {
        greeting: "Good morning",
        icon: "🌅",
        message: "Ready to start your day with AI assistance?"
      };
    } else if (hour >= 12 && hour < 17) {
      return {
        greeting: "Good afternoon",
        icon: "☀️",
        message: "How can I help you this afternoon?"
      };
    } else if (hour >= 17 && hour < 21) {
      return {
        greeting: "Good evening",
        icon: "🌆",
        message: "Hope you're having a productive evening!"
      };
    } else {
      return {
        greeting: "Good night",
        icon: "🌙",
        message: "Working late? I'm here to help!"
      };
    }
  };

  const getFirstName = () => {
    if (!userInfo) return "User";
    
    // Parse first name from username (e.g., "Dr. Sarah Smith" -> "Dr. Sarah")
    const parseFirstName = (fullName) => {
      if (!fullName) return "User";
      const parts = fullName.split(' ');
      if (parts.length >= 3) {
        // Handle titles like "Dr. Sarah Smith"
        return parts.slice(0, -1).join(' '); // "Dr. Sarah"
      } else if (parts.length === 2) {
        return parts[0]; // "Sarah"
      } else {
        return parts[0] || "User";
      }
    };

    return userInfo.given_name || parseFirstName(userInfo.username || userInfo.name) || "User";
  };

  const getRoleBasedGreeting = () => {
    if (!userInfo) return "";
    
    const role = userInfo.role?.toLowerCase() || '';
    
    switch (role) {
      case 'doctor':
        return "How can I assist with patient care today?";
      case 'supervisor':
        return "Ready to review cases and manage operations?";
      case 'nurse':
        return "How can I help with patient monitoring?";
      case 'admin':
        return "What administrative tasks can I assist with?";
      default:
        return "How can I help you today?";
    }
  };

  const timeGreeting = getTimeBasedGreeting();
  const roleGreeting = getRoleBasedGreeting();
  const firstName = getFirstName();

  return (
    <div className="time-greeting">
      <div className="greeting-header">
        <span className="greeting-icon">{timeGreeting.icon}</span>
        <div className="greeting-text">
          <h2 className="greeting-main">
            {timeGreeting.greeting}, {firstName}!
          </h2>
          <p className="greeting-subtitle">{timeGreeting.message}</p>
          <p className="greeting-role">{roleGreeting}</p>
        </div>
      </div>
    </div>
  );
};

export default TimeBasedGreeting;

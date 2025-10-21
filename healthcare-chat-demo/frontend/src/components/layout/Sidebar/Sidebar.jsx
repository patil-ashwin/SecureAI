// src/components/layout/Sidebar/Sidebar.jsx
import React from 'react';
import { Plus, Search, Library, Settings, X } from 'lucide-react';
import { Button } from '@components/common';
import { useClickOutside } from '@hooks';
import styles from './Sidebar.module.css';

const Sidebar = ({ 
  isOpen, 
  onClose, 
  onNewChat,
  configs = [],
  className 
}) => {
  const sidebarRef = useClickOutside(() => {
    if (isOpen) onClose();
  });

  const navigationItems = [
    { icon: Search, label: 'Search chats', disabled: true },
    { icon: Library, label: 'Library', disabled: true },
    { icon: Settings, label: 'GPTs', disabled: true }
  ];

  return (
    <>
      {/* Backdrop */}
      {isOpen && <div className={styles.backdrop} onClick={onClose} />}
      
      {/* Sidebar */}
      <div 
        ref={sidebarRef}
        className={`${styles.sidebar} ${isOpen ? styles.open : ''} ${className || ''}`}
      >
        <div className={styles.header}>
          <Button
            variant="ghost"
            size="small"
            onClick={onClose}
            className={styles.closeButton}
          >
            <X size={20} />
          </Button>
        </div>

        <div className={styles.content}>
          {/* New Chat Button */}
          <Button
            variant="ghost"
            onClick={onNewChat}
            className={styles.newChatButton}
          >
            <Plus size={16} />
            New chat
          </Button>

          {/* Navigation */}
          <nav className={styles.navigation}>
            {navigationItems.map((item, index) => (
              <button
                key={index}
                className={`${styles.navItem} ${item.disabled ? styles.disabled : ''}`}
                disabled={item.disabled}
              >
                <item.icon size={16} />
                <span>{item.label}</span>
              </button>
            ))}
          </nav>

          {/* Configurations */}
          {configs.length > 0 && (
            <div className={styles.configsSection}>
              <h3 className={styles.configsTitle}>Available Configurations</h3>
              <div className={styles.configsList}>
                {configs.map((config, index) => (
                  <div key={index} className={styles.configItem}>
                    <div className={styles.configName}>{config.intent}</div>
                    <div className={styles.configDesc}>{config.description}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className={styles.footer}>
          <div className={styles.user}>
            <div className={styles.userAvatar}>
              <span>U</span>
            </div>
            <span className={styles.userName}>User</span>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
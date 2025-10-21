// src/components/layout/Header/Header.jsx
import React from 'react';
import { Menu } from 'lucide-react';
import { Button } from '@components/common';
import styles from './Header.module.css';

const Header = ({ onMenuClick, title = "BART Assistant" }) => {
  return (
    <header className={styles.header}>
      <div className={styles.content}>
        <Button
          variant="ghost"
          size="small"
          onClick={onMenuClick}
          className={styles.menuButton}
        >
          <Menu size={20} />
        </Button>
        
        <h1 className={styles.title}>{title}</h1>
        
        <div className={styles.actions}>
          {/* Future: Add user menu, settings, etc. */}
        </div>
      </div>
    </header>
  );
};

export default Header;
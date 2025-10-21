// src/components/common/Icon/Icon.jsx
import React from 'react';
import * as LucideIcons from 'lucide-react';

const Icon = ({ name, size = 16, color, className, ...props }) => {
  const IconComponent = LucideIcons[name];
  
  if (!IconComponent) {
    console.warn(`Icon "${name}" not found`);
    return null;
  }

  return (
    <IconComponent
      size={size}
      color={color}
      className={className}
      {...props}
    />
  );
};

export default Icon;
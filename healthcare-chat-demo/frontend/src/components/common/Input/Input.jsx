// src/components/common/Input/Input.jsx
import React, { forwardRef } from 'react';
import { classNames } from '@utils/helpers';
import styles from './Input.module.css';

const Input = forwardRef(({
  type = 'text',
  placeholder,
  value,
  onChange,
  onFocus,
  onBlur,
  disabled = false,
  error,
  className,
  ...props
}, ref) => {
  const inputClass = classNames(
    styles.input,
    {
      [styles.error]: error,
      [styles.disabled]: disabled
    },
    className
  );

  return (
    <div className={styles.container}>
      <input
        ref={ref}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        onFocus={onFocus}
        onBlur={onBlur}
        disabled={disabled}
        className={inputClass}
        {...props}
      />
      {error && (
        <span className={styles.errorText}>{error}</span>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
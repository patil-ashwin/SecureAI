// src/components/forms/ParameterForm/ParameterForm.jsx
import React, { useState } from 'react';
import { Button, Input } from '@components/common';
import { capitalizeFirst } from '@utils/formatters';
import styles from './ParameterForm.module.css';

const ParameterForm = ({ 
  queryData, 
  onSubmit,
  loading = false,
  className 
}) => {
  const [parameters, setParameters] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const missingParams = queryData?.missing_parameters || [];

  const handleInputChange = (paramName, value) => {
    setParameters(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  const handleSubmit = async () => {
    if (isSubmitting || !onSubmit) return;

    setIsSubmitting(true);
    try {
      await onSubmit(queryData, parameters);
    } catch (error) {
      console.error('Parameter submission failed:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isFormValid = missingParams.every(param => 
    parameters[param] && parameters[param].trim().length > 0
  );

  if (!missingParams || missingParams.length === 0) {
    return null;
  }

  return (
    <div className={`${styles.parameterForm} ${className || ''}`}>
      <div className={styles.header}>
        <h4 className={styles.title}>Please provide the required parameters:</h4>
      </div>
      
      <div className={styles.fields}>
        {missingParams.map((param, index) => (
          <div key={index} className={styles.field}>
            <label className={styles.label}>
              {capitalizeFirst(param.replace('_', ' '))}:
            </label>
            <Input
              type="text"
              value={parameters[param] || ''}
              onChange={(e) => handleInputChange(param, e.target.value)}
              placeholder={`Enter ${param.replace('_', ' ')}`}
              disabled={isSubmitting || loading}
              className={styles.input}
            />
          </div>
        ))}
      </div>
      
      <div className={styles.actions}>
        <Button
          onClick={handleSubmit}
          disabled={!isFormValid || isSubmitting || loading}
          loading={isSubmitting}
          variant="primary"
        >
          {isSubmitting ? 'Processing...' : 'Submit Parameters'}
        </Button>
      </div>
    </div>
  );
};

export default ParameterForm;
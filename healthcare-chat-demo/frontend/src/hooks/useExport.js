import { useState, useCallback } from 'react';
import exportService from '../services/exportService';

export const useExport = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateExport = useCallback(async (ringId, format) => {
    setLoading(true);
    setError(null);
    try {
      const result = await exportService.generateExport(ringId, format);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const isExportAvailable = useCallback(() => {
    return exportService.isExportAvailable();
  }, []);

  return {
    loading,
    error,
    generateExport,
    isExportAvailable
  };
};

export default useExport;

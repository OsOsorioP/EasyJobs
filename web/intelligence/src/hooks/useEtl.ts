import { useState } from 'react';
import type { EtlResult, EtlType } from '../types';
import { etlService } from '../lib/services/etl.service';

export function useEtl() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [etlType, setEtlType] = useState<EtlType>('csv');
  const [isUploading, setIsUploading] = useState(false);
  const [etlResult, setEtlResult] = useState<EtlResult | null>(null);
  const [etlError, setEtlError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setEtlError('');
      setEtlResult(null);

      if (file.name.endsWith('.csv')) {
        setEtlType('csv');
      } else if (file.name.endsWith('.zip')) {
        setEtlType('zip');
      }
    }
  };

  const handleUploadETL = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setEtlError('');
    setEtlResult(null);

    try {
      const response = await etlService.uploadEtl(selectedFile, etlType);
      setEtlResult(response);
    } catch (err) {
      console.warn("Fallo de conexión real con el pipeline ETL. Simulando respuesta.", err);
      setEtlError("La API del Pipeline ETL (puerto 8002) está offline. Simulando procesamiento...");
    } finally {
        setIsUploading(false);
    }
  };

  return {
    selectedFile,
    isUploading,
    etlResult,
    etlError,
    handleFileChange,
    handleUploadETL,
  };
}
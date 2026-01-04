import { useState, useCallback } from 'react';

import { jobsService } from '../services/jobs';
import { useError } from '../context/ErrorContext';
import { GenerateRequest } from '../types/job';
import { STATUS_MESSAGES, DEFAULT_LANG, DEFAULT_GEO, DEFAULT_NUM_WEBSITES } from '../constants';

interface UseJobUploadReturn {
  file: File | null;
  lang: string;
  geo: string;
  numWebsites: number;
  uploading: boolean;
  setFile: (file: File | null) => void;
  setLang: (lang: string) => void;
  setGeo: (geo: string) => void;
  setNumWebsites: (num: number) => void;
  handleSubmit: (onSuccess: (jobId: string) => void) => Promise<void>;
}

/**
 * Hook for managing job upload state and logic.
 */
export function useJobUpload(): UseJobUploadReturn {
  const [file, setFile] = useState<File | null>(null);
  const [lang, setLang] = useState(DEFAULT_LANG);
  const [geo, setGeo] = useState(DEFAULT_GEO);
  const [numWebsites, setNumWebsites] = useState(DEFAULT_NUM_WEBSITES);
  const [uploading, setUploading] = useState(false);
  const { showError, showSuccess } = useError();

  const handleSubmit = useCallback(
    async (onSuccess: (jobId: string) => void) => {
      if (!file) {
        showError(STATUS_MESSAGES.FILE_REQUIRED);
        return;
      }

      setUploading(true);
      try {
        const uploadResponse = await jobsService.uploadFile(file);
        await jobsService.generateContent({
          job_id: uploadResponse.job_id,
          lang,
          geo,
          num_websites: numWebsites,
        } as GenerateRequest);
        showSuccess(STATUS_MESSAGES.JOB_CREATED);
        onSuccess(uploadResponse.job_id);
      } catch (error: unknown) {
        const errorMessage =
          (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
          STATUS_MESSAGES.UPLOAD_ERROR;
        showError(errorMessage);
      } finally {
        setUploading(false);
      }
    },
    [file, lang, geo, numWebsites, showError, showSuccess]
  );

  return {
    file,
    lang,
    geo,
    numWebsites,
    uploading,
    setFile,
    setLang,
    setGeo,
    setNumWebsites,
    handleSubmit,
  };
}


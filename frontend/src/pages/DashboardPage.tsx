import React, { useState } from 'react';
import { Box } from '@mui/material';
import { JobUpload } from '../components/Jobs/JobUpload';
import { JobList } from '../components/Jobs/JobList';
import { Layout } from '../components/Layout/Layout';
import { logger } from '../utils/logger';

export const DashboardPage: React.FC = () => {
  const [refreshKey, setRefreshKey] = useState(0);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadSuccess = (jobId: string) => {
    logger.debug('Job created successfully:', jobId);
    setRefreshKey((prev) => prev + 1);
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <Layout>
      <JobUpload onUploadSuccess={handleUploadSuccess} />
      <JobList key={refreshKey} refreshTrigger={refreshTrigger} />
    </Layout>
  );
};


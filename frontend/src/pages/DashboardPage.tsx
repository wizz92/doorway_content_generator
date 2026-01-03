import React, { useState } from 'react';
import { Box } from '@mui/material';
import { JobUpload } from '../components/Jobs/JobUpload';
import { JobList } from '../components/Jobs/JobList';
import { Layout } from '../components/Layout/Layout';

export const DashboardPage: React.FC = () => {
  const [refreshKey, setRefreshKey] = useState(0);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadSuccess = (jobId: string) => {
    console.log('Job created successfully:', jobId);
    // Force refresh of job list
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


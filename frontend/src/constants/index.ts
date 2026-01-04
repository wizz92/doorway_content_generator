/** Application constants */

/** Polling interval for job status updates (milliseconds) */
export const JOB_POLLING_INTERVAL = 2000;

/** Default job list limit */
export const DEFAULT_JOB_LIST_LIMIT = 50;

/** Maximum job list limit */
export const MAX_JOB_LIST_LIMIT = 1000;

/** Default number of websites */
export const DEFAULT_NUM_WEBSITES = 3;

/** Minimum number of websites */
export const MIN_NUM_WEBSITES = 1;

/** Maximum number of websites */
export const MAX_NUM_WEBSITES = 100;

/** Default language code */
export const DEFAULT_LANG = 'hu';

/** Default geography code */
export const DEFAULT_GEO = 'HU';

/** Animation durations (milliseconds) */
export const ANIMATION_DURATION_FAST = 300;
export const ANIMATION_DURATION_NORMAL = 600;

/** Snackbar display durations (milliseconds) */
export const SNACKBAR_DURATION_ERROR = 6000;
export const SNACKBAR_DURATION_SUCCESS = 4000;

/** Status messages */
export const STATUS_MESSAGES = {
  DOWNLOAD_STARTED: 'Download started',
  JOB_CANCELLED: 'Job cancelled',
  JOB_CREATED: 'Job created successfully!',
  UPLOAD_ERROR: 'Failed to upload and generate job',
  DOWNLOAD_ERROR: 'Failed to download',
  CANCEL_ERROR: 'Failed to cancel job',
  FILE_REQUIRED: 'Please select a CSV file',
} as const;


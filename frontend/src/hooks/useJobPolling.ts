import { useEffect, useRef } from 'react';

import { JOB_POLLING_INTERVAL } from '../constants';

interface UseJobPollingOptions {
  enabled?: boolean;
  interval?: number;
  onPoll?: () => void;
}

/**
 * Hook for polling job status updates.
 */
export function useJobPolling(
  callback: () => void,
  options: UseJobPollingOptions = {}
): void {
  const { enabled = true, interval = JOB_POLLING_INTERVAL, onPoll } = options;
  const callbackRef = useRef(callback);

  // Update callback ref when it changes
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    const poll = () => {
      callbackRef.current();
      onPoll?.();
    };

    // Poll immediately
    poll();

    // Set up interval
    const intervalId = setInterval(poll, interval);

    return () => {
      clearInterval(intervalId);
    };
  }, [enabled, interval, onPoll]);
}


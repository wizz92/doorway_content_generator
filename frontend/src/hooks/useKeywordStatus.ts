import { useCallback, useMemo } from 'react';
import { Job, KeywordStatus } from '../types/job';

interface KeywordStatusDisplay {
  text: string;
  color: 'success' | 'warning' | 'default';
}

interface UseKeywordStatusReturn {
  filteredKeywords: string[];
  getKeywordStatus: (keyword: string) => KeywordStatus | null;
  getStatusDisplay: (status: KeywordStatus | null) => KeywordStatusDisplay;
}

/**
 * Hook for managing keyword status and filtering.
 * Properly reacts to changes in job.keyword_status.
 */
export function useKeywordStatus(job: Job, searchQuery: string): UseKeywordStatusReturn {
  const keywords = job.keywords || [];
  const keywordStatus = job.keyword_status || {};

  // Create a stable reference that updates when keyword_status changes
  // Serialize to detect deep object changes
  const keywordStatusSerialized = useMemo(() => {
    return JSON.stringify(keywordStatus);
  }, [
    job.id,
    job.keywords_completed,
    job.websites_completed,
    // Stringify to detect deep changes in keyword_status object
    JSON.stringify(keywordStatus),
  ]);

  // Parse back to get current keywordStatus object
  const currentKeywordStatus = useMemo(
    () => (keywordStatusSerialized ? JSON.parse(keywordStatusSerialized) : {}),
    [keywordStatusSerialized]
  );

  const filteredKeywords = useMemo(() => {
    if (!searchQuery.trim()) {
      return keywords;
    }
    const query = searchQuery.toLowerCase();
    return keywords.filter((keyword) => keyword.toLowerCase().includes(query));
  }, [keywords, searchQuery]);

  const getKeywordStatus = useCallback(
    (keyword: string): KeywordStatus | null => {
      return currentKeywordStatus[keyword] || null;
    },
    [currentKeywordStatus]
  );

  const getStatusDisplay = useCallback((status: KeywordStatus | null): KeywordStatusDisplay => {
    if (!status) {
      return { text: 'Pending', color: 'default' };
    }

    const { completed_websites, total_websites } = status;
    const completedCount = completed_websites.length;

    if (completedCount === 0) {
      return { text: 'Pending', color: 'default' };
    } else if (completedCount === total_websites) {
      return { text: `Completed (${completedCount}/${total_websites})`, color: 'success' };
    } else {
      return { text: `In Progress (${completedCount}/${total_websites})`, color: 'warning' };
    }
  }, []);

  return {
    filteredKeywords,
    getKeywordStatus,
    getStatusDisplay,
  };
}


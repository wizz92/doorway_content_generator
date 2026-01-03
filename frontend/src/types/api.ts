/** API error response */
export interface ApiError {
  detail: string;
  message?: string;
}

/** API response wrapper */
export interface ApiResponse<T> {
  data: T;
  status: number;
}


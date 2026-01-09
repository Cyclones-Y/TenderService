
// @ts-ignore
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/dev-api';

/**
 * Constructs a full API URL.
 * @param path - The endpoint path (e.g., '/tenders/dashboard')
 * @returns The full URL
 */
export const getApiUrl = (path: string): string => {
  const cleanBase = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${cleanBase}${cleanPath}`;
};

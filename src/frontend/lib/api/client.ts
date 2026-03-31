const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const HTTP_METHODS = {
  GET: 'GET',
  POST: 'POST',
  PUT: 'PUT',
  DELETE: 'DELETE',
} as const;

const HEADERS = {
  CONTENT_TYPE: 'Content-Type',
  APPLICATION_JSON: 'application/json',
} as const;

interface ErrorResponse {
  error: string;
  error_code: string;
}

const DEFAULT_ERROR: ErrorResponse = {
  error: 'Unknown error',
  error_code: 'UNKNOWN_ERROR',
};

export class ApiError extends Error {
  constructor(
    public status: number,
    public errorCode: string,
    message: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => DEFAULT_ERROR);
    throw new ApiError(response.status, error.error_code, error.error);
  }
  
  return response.json();
}

interface RequestConfig {
  method: string;
  credentials: RequestCredentials;
  headers?: HeadersInit;
  body?: string;
}

function buildRequestConfig(
  method: string,
  data?: unknown
): RequestConfig {
  const config: RequestConfig = {
    method,
    credentials: 'include',
  };

  if (data !== undefined) {
    config.headers = {
      [HEADERS.CONTENT_TYPE]: HEADERS.APPLICATION_JSON,
    };
    config.body = JSON.stringify(data);
  }

  return config;
}

export const apiClient = {
  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      buildRequestConfig(HTTP_METHODS.POST, data)
    );
    return handleResponse<T>(response);
  },

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      buildRequestConfig(HTTP_METHODS.GET)
    );
    return handleResponse<T>(response);
  },

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      buildRequestConfig(HTTP_METHODS.PUT, data)
    );
    return handleResponse<T>(response);
  },

  async delete<T>(endpoint: string): Promise<T> {
    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      buildRequestConfig(HTTP_METHODS.DELETE)
    );
    return handleResponse<T>(response);
  },
} as const;
import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { config } from '../config/env';

// ─── Storage Keys ────────────────────────────────────────────────────────────
export const STORAGE_KEYS = {
    ACCESS_TOKEN: '@revivo:access_token',
    REFRESH_TOKEN: '@revivo:refresh_token',
} as const;

// ─── API Error Shape ──────────────────────────────────────────────────────────
export class ApiError extends Error {
    constructor(
        public statusCode: number,
        public detail: string,
        public isNetwork: boolean = false,
    ) {
        super(detail);
        this.name = 'ApiError';
    }
}

// ─── Create base Axios instance ───────────────────────────────────────────────
const api: AxiosInstance = axios.create({
    baseURL: config.API_BASE_URL,
    timeout: 10_000,
    headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
    },
});

// ─── Request interceptor: inject Bearer token ────────────────────────────────
api.interceptors.request.use(async (req: InternalAxiosRequestConfig) => {
    const token = await AsyncStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    if (token && req.headers) {
        req.headers.Authorization = `Bearer ${token}`;
    }
    return req;
});

// Refresh-in-progress guard (prevent multiple concurrent refresh calls)
let isRefreshing = false;
let failedQueue: Array<{
    resolve: (token: string) => void;
    reject: (err: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null) {
    failedQueue.forEach((prom) => {
        if (error) prom.reject(error);
        else prom.resolve(token!);
    });
    failedQueue = [];
}

// ─── Response interceptor: handle errors + auto-refresh on 401 ──────────────
api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        // Network / timeout errors
        if (!error.response) {
            console.warn('[API Network Error]', `${error.config?.baseURL}${error.config?.url}`, error.message);
            throw new ApiError(0, `Network error — please check your connection (${error.config?.baseURL || 'unknown URL'}).`, true);
        }

        const { status, data } = error.response as { status: number; data: { detail?: string } };
        const detail = data?.detail ?? 'An unexpected error occurred.';

        // 401 — try token refresh once
        if (status === 401 && !originalRequest._retry) {
            if (isRefreshing) {
                return new Promise<string>((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                }).then((newToken) => {
                    if (originalRequest.headers) {
                        (originalRequest.headers as Record<string, string>).Authorization = `Bearer ${newToken}`;
                    }
                    return api(originalRequest);
                });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                const refreshToken = await AsyncStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
                if (!refreshToken) throw new Error('No refresh token');

                // The refresh endpoint receives the token in the body as a query param
                const refreshResponse = await axios.post(
                    `${config.API_BASE_URL}/auth/refresh`,
                    null,
                    { params: { refresh_token: refreshToken } }
                );

                const { access_token, refresh_token: newRefresh } = refreshResponse.data;
                await AsyncStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, access_token);
                await AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, newRefresh);

                processQueue(null, access_token);
                if (originalRequest.headers) {
                    (originalRequest.headers as Record<string, string>).Authorization = `Bearer ${access_token}`;
                }
                return api(originalRequest);
            } catch (refreshError) {
                processQueue(refreshError, null);
                // Wipe tokens so the app goes back to login
                await AsyncStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
                await AsyncStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
                throw new ApiError(401, 'Session expired. Please log in again.');
            } finally {
                isRefreshing = false;
            }
        }

        // Map specific status codes to user-friendly messages
        const messages: Record<number, string> = {
            400: detail,
            401: 'Invalid credentials.',
            403: 'You do not have permission to perform this action.',
            404: 'The requested resource was not found.',
            422: 'Validation error — please check your input.',
            500: 'Server error. Please try again later.',
        };

        throw new ApiError(status, messages[status] ?? detail);
    }
);

export default api;

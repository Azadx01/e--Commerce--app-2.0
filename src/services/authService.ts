import AsyncStorage from '@react-native-async-storage/async-storage';
import api, { STORAGE_KEYS } from './apiClient';

// ─── Types ────────────────────────────────────────────────────────────────────
export interface UserRead {
    id: number;
    email: string;
    name: string | null;
    role: string;
    status: string;
    created_at: string;
}

export interface RegisterPayload {
    email: string;
    password: string;
    name: string;
    role?: string;
}

export interface LoginPayload {
    username: string; // FastAPI OAuth2PasswordRequestForm expects 'username'
    password: string;
}

export interface TokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

// ─── Service ──────────────────────────────────────────────────────────────────
export const authService = {
    /**
     * POST /auth/register
     * Creates a new user account.
     */
    register: async (payload: RegisterPayload): Promise<UserRead> => {
        const response = await api.post<UserRead>('/auth/register', payload);
        return response.data;
    },

    /**
     * POST /auth/login
     * Authenticates with FastAPI's OAuth2PasswordRequestForm format
     * (application/x-www-form-urlencoded), persists tokens to AsyncStorage.
     */
    login: async (payload: LoginPayload): Promise<TokenResponse> => {
        // FastAPI OAuth2 form expects URL-encoded body
        const formData = new URLSearchParams();
        formData.append('username', payload.username);
        formData.append('password', payload.password);

        const response = await api.post<TokenResponse>('/auth/login', formData.toString(), {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });

        const tokens = response.data;
        await AsyncStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, tokens.access_token);
        await AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokens.refresh_token);
        return tokens;
    },

    /**
     * GET /auth/me
     * Fetches the authenticated user's profile.
     */
    getMe: async (): Promise<UserRead> => {
        const response = await api.get<UserRead>('/auth/me');
        return response.data;
    },

    /**
     * POST /auth/logout
     * Blacklists the current token on the server and clears local storage.
     */
    logout: async (): Promise<void> => {
        try {
            await api.post('/auth/logout');
        } finally {
            // Always clear local tokens even if server call fails
            await AsyncStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
            await AsyncStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        }
    },

    /**
     * Check if a valid access token exists locally.
     */
    hasToken: async (): Promise<boolean> => {
        const token = await AsyncStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
        return !!token;
    },
};

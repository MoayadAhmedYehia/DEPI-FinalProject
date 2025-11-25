import apiClient from './api';

export interface User {
    id: string;
    email: string;
    full_name: string;
    created_at: string;
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    email: string;
    password: string;
    full_name: string;
}

export interface AuthResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    user: User;
}

export interface RefreshTokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

class AuthService {
    async login(data: LoginRequest): Promise<AuthResponse> {
        const response = await apiClient.post<AuthResponse>('/api/auth/login', data);
        this.setTokens(response.data);
        return response.data;
    }

    async register(data: RegisterRequest): Promise<AuthResponse> {
        const response = await apiClient.post<AuthResponse>('/api/auth/register', data);
        this.setTokens(response.data);
        return response.data;
    }

    async logout(): Promise<void> {
        try {
            await apiClient.post('/api/auth/logout');
        } finally {
            this.clearTokens();
        }
    }

    async refreshToken(): Promise<RefreshTokenResponse> {
        const refreshToken = sessionStorage.getItem('refresh_token');
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await apiClient.post<RefreshTokenResponse>('/api/auth/refresh', {
            refresh_token: refreshToken,
        });

        this.setTokens(response.data);
        return response.data;
    }

    async getCurrentUser(): Promise<User> {
        const response = await apiClient.get<User>('/api/auth/me');
        sessionStorage.setItem('user', JSON.stringify(response.data));
        return response.data;
    }

    private setTokens(data: AuthResponse | RefreshTokenResponse): void {
        sessionStorage.setItem('access_token', data.access_token);
        sessionStorage.setItem('refresh_token', data.refresh_token);

        if ('user' in data) {
            sessionStorage.setItem('user', JSON.stringify(data.user));
        }
    }

    private clearTokens(): void {
        sessionStorage.removeItem('access_token');
        sessionStorage.removeItem('refresh_token');
        sessionStorage.removeItem('user');
    }

    getStoredUser(): User | null {
        const userStr = sessionStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    }

    isAuthenticated(): boolean {
        return !!sessionStorage.getItem('access_token');
    }
}

export const authService = new AuthService();

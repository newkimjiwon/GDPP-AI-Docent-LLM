// File: frontend/src/store/authStore.js
import { create } from 'zustand';
import { authService } from '../services/auth';

const useAuthStore = create((set) => ({
    user: null,
    token: authService.getToken(),
    isAuthenticated: !!authService.getToken(),
    isLoading: false,
    error: null,

    login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
            const data = await authService.login(email, password);
            authService.setToken(data.access_token);

            // Get user info
            const user = await authService.getCurrentUser();

            set({
                user,
                token: data.access_token,
                isAuthenticated: true,
                isLoading: false,
            });

            return true;
        } catch (error) {
            set({
                error: error.response?.data?.detail || 'Login failed',
                isLoading: false,
            });
            return false;
        }
    },

    register: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
            const data = await authService.register(email, password);
            authService.setToken(data.access_token);

            // Get user info
            const user = await authService.getCurrentUser();

            set({
                user,
                token: data.access_token,
                isAuthenticated: true,
                isLoading: false,
            });

            return true;
        } catch (error) {
            set({
                error: error.response?.data?.detail || 'Registration failed',
                isLoading: false,
            });
            return false;
        }
    },

    logout: () => {
        authService.logout();
        set({
            user: null,
            token: null,
            isAuthenticated: false,
        });
    },

    clearError: () => set({ error: null }),
}));

export default useAuthStore;

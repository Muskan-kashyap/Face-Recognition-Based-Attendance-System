import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '../services/authService';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      isHydrated: false,

      login: async (email, password) => {
        set({ isLoading: true });
        try {
          const response = await authService.login(email, password);
          const { access_token, refresh_token } = response.data;
          
          // Fetch user profile immediately after login
          const meResponse = await authService.getMe(access_token);
          
          set({
            user: meResponse.data,
            token: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
          });
          return true;
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: async () => {
        try {
          const { token } = get();
          if (token) {
            await authService.logout(token);
          }
        } catch (e) {
          // Ignore logout errors
        } finally {
          set({
            user: null,
            token: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
          });
          localStorage.removeItem('auth-storage');
        }
      },

      setToken: (token) => set({ token }),
      setRefreshToken: (refreshToken) => set({ refreshToken }),

      refreshAccessToken: async () => {
        const { refreshToken } = get();
        if (!refreshToken) {
          get().logout();
          throw new Error('No refresh token available');
        }
        try {
          const response = await authService.refreshToken(refreshToken);
          set({ token: response.data.access_token, isAuthenticated: true });
          return response.data.access_token;
        } catch (error) {
          get().logout();
          throw error;
        }
      },

      hydrate: () => {
        const state = get();
        set({ isHydrated: true });
        if (state.token && !state.user) {
          // Try to restore user from token
          authService
            .getMe(state.token)
            .then((res) => {
              set({ user: res.data, isAuthenticated: true });
            })
            .catch(() => {
              get().logout();
            });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);


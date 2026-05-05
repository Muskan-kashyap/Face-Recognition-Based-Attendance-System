// import { create } from 'zustand';
// import { persist } from 'zustand/middleware';
// import { authService } from '../services/authService';

// export const useAuthStore = create(
//   persist(
//     (set, get) => ({
//       user: null,
//       token: null,
//       refreshToken: null,
//       isAuthenticated: false,
//       isLoading: false,
//       isHydrated: false,

//       login: async (email, password) => {
//         set({ isLoading: true });
//         try {
//           const response = await authService.login(email, password);
//           const { access_token, refresh_token } = response.data;
          
//           // Fetch user profile immediately after login
//           const meResponse = await authService.getMe(access_token);
          
//           set({
//             user: meResponse.data,
//             token: access_token,
//             refreshToken: refresh_token,
//             isAuthenticated: true,
//             isLoading: false,
//           });
//           return true;
//         } catch (error) {
//           set({ isLoading: false });
//           throw error;
//         }
//       },

//       logout: async () => {
//         try {
//           const { token } = get();
//           if (token) {
//             await authService.logout(token);
//           }
//         } catch (e) {
//           // Ignore logout errors
//         } finally {
//           set({
//             user: null,
//             token: null,
//             refreshToken: null,
//             isAuthenticated: false,
//             isLoading: false,
//           });
//           localStorage.removeItem('auth-storage');
//         }
//       },

//       setToken: (token) => set({ token }),
//       setRefreshToken: (refreshToken) => set({ refreshToken }),

//       refreshAccessToken: async () => {
//         const { refreshToken } = get();
//         if (!refreshToken) {
//           get().logout();
//           throw new Error('No refresh token available');
//         }
//         try {
//           const response = await authService.refreshToken(refreshToken);
//           set({ token: response.data.access_token, isAuthenticated: true });
//           return response.data.access_token;
//         } catch (error) {
//           get().logout();
//           throw error;
//         }
//       },

//       hydrate: () => {
//         const state = get();
//         set({ isHydrated: true });
//         if (state.token && !state.user) {
//           // Try to restore user from token
//           authService
//             .getMe(state.token)
//             .then((res) => {
//               set({ user: res.data, isAuthenticated: true });
//             })
//             .catch(() => {
//               get().logout();
//             });
//         }
//       },
//     }),
//     {
//       name: 'auth-storage',
//       partialize: (state) => ({
//         token: state.token,
//         refreshToken: state.refreshToken,
//         user: state.user,
//         isAuthenticated: state.isAuthenticated,
//       }),
//     }
//   )
// );


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

      // =========================
      // LOGIN (FIXED)
      // =========================
      login: async (email, password) => {
        set({ isLoading: true });

        try {
          const response = await authService.login(email, password);
          const { access_token, refresh_token } = response.data;

          // ✅ CRITICAL: sync immediately
          localStorage.setItem("access_token", access_token);
          localStorage.setItem("refresh_token", refresh_token);

          // ✅ Now interceptor will work
          const meResponse = await authService.getMe();

          // Normalize user object: ensure role is a string
          const userData = meResponse.data;
          if (userData.role && typeof userData.role === 'object') {
            userData.role = userData.role.name.toLowerCase();
          } else if (typeof userData.role === 'string') {
            userData.role = userData.role.toLowerCase();
          }

          set({
            user: userData,
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

      // =========================
      // LOGOUT (FIXED)
      // =========================
      logout: async () => {
        try {
          const { token } = get();
          if (token) {
            await authService.logout(token);
          }
        } catch {
          // ignore
        } finally {
          // ✅ clear everything consistently
          localStorage.removeItem('auth-storage');
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');

          set({
            user: null,
            token: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      setToken: (token) => set({ token }),
      setRefreshToken: (refreshToken) => set({ refreshToken }),

      // =========================
      // REFRESH TOKEN (FIXED)
      // =========================
      refreshAccessToken: async () => {
        const { refreshToken } = get();

        if (!refreshToken) {
          get().logout();
          throw new Error('No refresh token available');
        }

        try {
          const response = await authService.refreshToken(refreshToken);
          const newAccessToken = response.data.access_token;

          // ✅ sync everywhere
          localStorage.setItem("access_token", newAccessToken);

          set({
            token: newAccessToken,
            isAuthenticated: true
          });

          return newAccessToken;

        } catch (error) {
          get().logout();
          throw error;
        }
      },

      // =========================
      // HYDRATE (FIXED)
      // =========================
      hydrate: () => {
        const state = get();
        set({ isHydrated: true });

        if (state.token && !state.user) {
          authService
            .getMe() // ✅ no manual token
            .then((res) => {
              const userData = res.data;
              if (userData.role && typeof userData.role === 'object') {
                userData.role = userData.role.name.toLowerCase();
              } else if (typeof userData.role === 'string') {
                userData.role = userData.role.toLowerCase();
              }
              set({
                user: userData,
                isAuthenticated: true
              });
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

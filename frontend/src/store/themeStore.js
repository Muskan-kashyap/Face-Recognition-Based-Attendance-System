import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useThemeStore = create(
  persist(
    (set, get) => ({
      theme: 'dark', // default
      isDark: true,
      // toggleTheme: () => {
      //   const newTheme = get().theme === 'dark' ? 'light' : 'dark';
      //   set({ theme: newTheme, isDark: newTheme === 'dark' });
      //   // Apply immediately
      //   document.documentElement.className = newTheme;
      //   localStorage.setItem('theme', newTheme);
      // },
      // setTheme: (theme) => {
      //   set({ theme, isDark: theme === 'dark' });
      //   document.documentElement.className = theme;
      //   localStorage.setItem('theme', theme);
      // },
      toggleTheme: () => {
        const newTheme = get().theme === 'dark' ? 'light' : 'dark';
        set({ theme: newTheme, isDark: newTheme === 'dark' });

        // 🔥 FIXED: Target document.body instead of documentElement
        document.body.classList.remove('light', 'dark');
        document.body.classList.add(newTheme);

        localStorage.setItem('theme', newTheme);
      },
      setTheme: (theme) => {
        set({ theme, isDark: theme === 'dark' });

        document.body.classList.remove('light', 'dark');
        document.body.classList.add(theme);

        localStorage.setItem('theme', theme);
      },
    }),
    {
      name: 'theme-storage',
    }
  )
);

// Auto-apply on module load
// if (typeof document !== 'undefined') {
//   const savedTheme = localStorage.getItem('theme') || 'dark';
//   document.documentElement.className = savedTheme;
// }
if (typeof document !== 'undefined') {
  const savedTheme = localStorage.getItem('theme') || 'dark';
  document.body.classList.add(savedTheme); // Target body here too
}



import { Sun, Moon } from 'lucide-react';
import { useThemeStore } from '../../store/themeStore';
import { Button } from './Button';
import { cn } from '../../lib/utils';

const ThemeToggle = () => {
  const { isDark, toggleTheme } = useThemeStore();

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleTheme}
      className="h-9 w-9 p-0 rounded-full hover:bg-accent/20"
      title={isDark ? 'Light mode' : 'Dark mode'}
    >
      <Sun className={cn("h-5 w-5 transition-all duration-300", isDark && "rotate-180 text-yellow-400")} />
      <Moon className={cn("h-5 w-5 transition-all duration-300 absolute", !isDark && "text-slate-400 rotate-0")} />
    </Button>
  );
};

export default ThemeToggle;


import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Clock,
  Users,
  BarChart3,
  Settings,
  Ticket,
  CreditCard,
  Receipt,
  Menu,
  LogOut,
  Bell,
  Search,
  ChevronDown,
  ShieldCheck,
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { Avatar } from '../components/ui/Avatar';
import ThemeToggle from '../components/ui/Toggle';
import { cn } from '../lib/utils';

const navItems = [
  { label: 'Overview', icon: LayoutDashboard, path: '/dashboard', roles: ['admin', 'manager', 'employee'] },
  { label: 'Attendance', icon: Clock, path: '/dashboard/attendance', roles: ['admin', 'manager', 'employee'] },
  { label: 'Users', icon: Users, path: '/dashboard/users', roles: ['admin', 'manager'] },
  { label: 'Reports', icon: BarChart3, path: '/dashboard/reports', roles: ['admin', 'manager'] },
  { label: 'Support', icon: Ticket, path: '/dashboard/ticketing', roles: ['admin', 'manager', 'employee'] },
  { label: 'Payroll', icon: CreditCard, path: '/dashboard/payroll', roles: ['admin', 'manager'] },
  { label: 'Reimbursements', icon: Receipt, path: '/dashboard/reimbursements', roles: ['admin', 'manager', 'employee'] },
  { label: 'Settings', icon: Settings, path: '/dashboard/settings', roles: ['admin', 'manager', 'employee'] },
];

const ROLE_HIERARCHY = {
  'superadmin': 4,
  'admin': 3,
  'manager': 2,
  'employee': 1
};


export default function DashboardLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const userRole = (typeof user?.role === 'string' ? user.role : user?.role?.name || 'employee').toLowerCase();

  const filteredNav = navItems.filter((item) => {
    return item.roles.some(role => {
      const userLevel = ROLE_HIERARCHY[userRole] || 0;
      const requiredLevel = ROLE_HIERARCHY[role] || 0;
      return userLevel >= requiredLevel;
    });
  });

  // Mobile menu should close on navigation - handled by the nav item click or simple state check
  // Avoid setting state directly in effect if possible, but here it's meant to close the menu.
  // To satisfy the lint, we can wrap it or ensure it only runs when mobileOpen is true.
  useEffect(() => {
    if (mobileOpen) {
      setMobileOpen(false);
    }
  }, [location.pathname]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 1024) setSidebarOpen(false);
      else setSidebarOpen(true);
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-gray-950 text-slate-900 dark:text-gray-100 flex transition-colors duration-300">      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-gray-950/40 backdrop-blur-sm z-40 lg:hidden transition-opacity"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed lg:sticky top-0 left-0 z-50 h-screen bg-white dark:bg-gray-900 border-r border-slate-200 dark:border-gray-800 flex flex-col transition-all duration-300',
          sidebarOpen ? 'w-64' : 'w-20',
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Logo */}
        <div className="h-16 flex items-center px-4 border-b border-slate-200 dark:border-gray-800">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-indigo-600 flex items-center justify-center shrink-0 shadow-lg shadow-indigo-500/30">
              <ShieldCheck className="h-5 w-5 text-white" />
            </div>
            {sidebarOpen && (
              <span className="text-lg font-bold tracking-tight text-slate-900 dark:text-white">
                VisionCore
              </span>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1 hide-scrollbar">
          {filteredNav.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
                isActive(item.path)
                  ? 'bg-indigo-500/10 text-indigo-400 shadow-sm'
                  : 'text-slate-500 dark:text-gray-400 hover:bg-slate-100 dark:hover:bg-gray-800 hover:text-slate-900 dark:hover:text-white'

              )}
              title={!sidebarOpen ? item.label : undefined}
            >
              <item.icon className={cn('h-5 w-5 shrink-0 transition-colors duration-200', isActive(item.path) ? 'text-indigo-400' : 'text-gray-500')} />
              {sidebarOpen && <span>{item.label}</span>}
            </Link>
          ))}
        </nav>

        {/* User section */}
        <div className="p-3 border-t border-gray-800">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="hidden lg:flex w-full items-center justify-center p-2 text-slate-500 dark:text-gray-400 hover:bg-slate-100 dark:hover:bg-gray-800 rounded-xl transition-colors mb-2"
          >
            {sidebarOpen ? <ChevronDown className="h-4 w-4 rotate-90" /> : <ChevronDown className="h-4 w-4 -rotate-90" />}
          </button>

          <div className="flex items-center gap-3 px-3 py-2">
            <Avatar name={user?.full_name} size="sm" />
            {sidebarOpen && (
              <div className="min-w-0">
                <p className="text-sm font-medium truncate text-slate-900 dark:text-white">{user?.full_name || 'User'}</p>
                <p className="text-xs text-gray-500">{userRole}</p>
              </div>
            )}
          </div>

          <button
            onClick={handleLogout}
            className={cn(
              'flex items-center gap-3 px-3 py-2.5 mt-1 rounded-xl text-sm font-medium text-slate-500 dark:text-gray-400 hover:bg-red-500/10 hover:text-red-400 transition-colors w-full',
              !sidebarOpen && 'justify-center'
            )}
          >
            <LogOut className="h-5 w-5 shrink-0" />
            {sidebarOpen && <span>Sign out</span>}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Topbar */}
        <header className="h-16 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-slate-200 dark:border-gray-800 px-4 lg:px-8 flex items-center justify-between sticky top-0 z-30">
          <div className="flex items-center gap-4">
            <button
              onClick={() => {
                if (window.innerWidth < 1024) setMobileOpen(true);
                else setSidebarOpen(!sidebarOpen);
              }}
              className="lg:hidden p-2 text-gray-500 hover:bg-gray-800 rounded-xl transition-colors"
            >
              <Menu className="h-5 w-5" />
            </button>

            {/* Breadcrumb */}
            <nav className="hidden md:flex items-center text-sm text-gray-500">
              <span className="font-medium text-slate-900 dark:text-white">Dashboard</span>
              {location.pathname !== '/dashboard' && (
                <>
                  <span className="mx-2 text-gray-700">/</span>
                  <span className="capitalize">
                    {location.pathname.split('/').pop().replace(/-/g, ' ')}
                  </span>
                </>
              )}
            </nav>
          </div>

          <div className="flex items-center gap-3">
            {/* Search */}
            <div className="hidden md:flex items-center bg-slate-100 dark:bg-gray-800 rounded-xl px-3 py-2 transition-all focus-within:ring-2 focus-within:ring-indigo-500/50 border border-slate-200 dark:border-transparent">
              <Search className="h-4 w-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search..."
                className="bg-transparent border-none outline-none text-sm text-slate-700 dark:text-gray-200 placeholder:text-slate-400 dark:placeholder:text-gray-500 ml-2 w-48"
              />
            </div>

            {/* Notifications */}
            <button className="relative p-2 text-slate-500 dark:text-gray-500 hover:bg-slate-100 dark:hover:bg-gray-800 rounded-xl transition-colors">
              <Bell className="h-5 w-5" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 bg-red-500 rounded-full border-2 border-gray-900" />
            </button>

            {/* 🔥 NEW: Theme Toggle */}
            <ThemeToggle />

            {/* User dropdown */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-2 p-1 rounded-xl hover:bg-gray-800 transition-colors"
              >
                <Avatar name={user?.full_name} size="sm" />
                <ChevronDown className="h-4 w-4 text-gray-500 hidden sm:block" />
              </button>

              {userMenuOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} />
                  <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-slate-200 dark:border-gray-800 py-1 z-50 animate-fade-in">
                    <div className="px-4 py-3 border-b border-gray-800">
                      <p className="text-sm font-medium text-white">{user?.full_name}</p>
                      <p className="text-xs text-gray-500">{user?.email}</p>
                    </div>
                    <div className="p-1">
                      <Link
                        to="/dashboard/settings"
                        className="flex items-center gap-2 px-3 py-2 text-sm text-slate-700 dark:text-gray-300 hover:bg-slate-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                        onClick={() => setUserMenuOpen(false)}
                      >
                        <Settings className="h-4 w-4" />
                        Settings
                      </Link>
                      <button
                        onClick={() => {
                          setUserMenuOpen(false);
                          handleLogout();
                        }}
                        className="flex w-full items-center gap-2 px-3 py-2 mt-1 text-sm text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                      >
                        <LogOut className="h-4 w-4" />
                        Sign out
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 lg:p-8 overflow-y-auto hide-scrollbar">
          <div className="max-w-7xl mx-auto animate-fade-in">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}


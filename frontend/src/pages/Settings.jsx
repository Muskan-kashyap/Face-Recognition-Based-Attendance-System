import React, { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { useThemeStore } from '../store/themeStore';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import { Bell, Shield, User, Building, Moon, Sun } from 'lucide-react';

export default function Settings() {
  const { user } = useAuthStore();
  const { theme, setTheme } = useThemeStore();

  return (
    <div className="space-y-8 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Settings</h1>
        <p className="text-sm text-slate-500 dark:text-gray-400 mt-1">Manage your account and preferences</p>
      </div>

      {/* Profile */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-slate-900 dark:text-white">
            <User className="h-5 w-5 text-indigo-400" />
            Profile
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center gap-4">
            <Avatar name={user?.full_name} size="lg" />
            <div>
              <p className="text-base font-semibold text-slate-900 dark:text-white">{user?.full_name}</p>
              <p className="text-sm text-slate-500 dark:text-gray-400">{user?.email}</p>
              <Badge variant="primary" className="mt-1">{user?.role?.name}</Badge>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label="Full name" defaultValue={user?.full_name} />
            <Input label="Email" type="email" defaultValue={user?.email} />
          </div>
          <Button>Save changes</Button>
        </CardContent>
      </Card>

      {/* Security */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-slate-900 dark:text-white">
            <Shield className="h-5 w-5 text-indigo-400" />
            Security
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input label="Current password" type="password" />
          <Input label="New password" type="password" />
          <Input label="Confirm new password" type="password" />
          <Button>Update password</Button>
        </CardContent>
      </Card>

      {/* Appearance */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-slate-900 dark:text-white">
            <Moon className="h-5 w-5 text-indigo-400" />
            Appearance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-900 dark:text-white">Interface theme</p>
              <p className="text-xs text-slate-500 dark:text-gray-400">Choose between light and dark mode</p>
            </div>
            <div className="flex bg-slate-100 dark:bg-gray-800 rounded-lg p-1 border border-slate-200 dark:border-transparent">
              <button
                onClick={() => setTheme('light')}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${theme === 'light' ? 'bg-white text-indigo-600 shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-900'}`}
              >
                <Sun className="h-4 w-4" />
                Light
              </button>
              <button
                onClick={() => setTheme('dark')}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${theme === 'dark' ? 'bg-gray-700 text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'}`}
              >
                <Moon className="h-4 w-4" />
                Dark
              </button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Organization */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-slate-900 dark:text-white">
            <Building className="h-5 w-5 text-indigo-400" />
            Organization
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input label="Organization name" placeholder="Acme Inc." />
          <Input label="Department" placeholder="Engineering" />
          <Button>Save organization</Button>
        </CardContent>
      </Card>
    </div>
  );
}


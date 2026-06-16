import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuthStore } from '../store/authStore';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import { useToast } from '../components/ui/Toast';
import { adminService } from '../services/adminService';
import {
  Bell, Shield, User, Building, Moon, Sun,
  Zap, ZapOff, Save, Key, RefreshCw, Loader2,
} from 'lucide-react';

const Section = ({ title, description, icon: Icon, children }) => (
  <Card>
    <CardHeader className="border-b border-gray-800/50 pb-4">
      <div className="flex items-center gap-3">
        <div className="h-9 w-9 rounded-xl bg-indigo-500/10 flex items-center justify-center">
          <Icon className="h-5 w-5 text-indigo-400" />
        </div>
        <div>
          <CardTitle className="text-white text-base">{title}</CardTitle>
          {description && (
            <CardDescription className="text-gray-500 text-xs mt-0.5">{description}</CardDescription>
          )}
        </div>
      </div>
    </CardHeader>
    <CardContent className="pt-5">{children}</CardContent>
  </Card>
);

const Toggle = ({ enabled, onToggle, loading, disabled }) => (
  <button
    onClick={onToggle}
    disabled={loading || disabled}
    aria-pressed={enabled}
    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed ${
      enabled ? 'bg-indigo-600' : 'bg-gray-700'
    }`}
  >
    <span className="sr-only">{enabled ? 'Disable' : 'Enable'}</span>
    <span
      className={`inline-flex h-4 w-4 items-center justify-center rounded-full bg-white shadow-md transform transition-transform duration-300 ${
        enabled ? 'translate-x-6' : 'translate-x-1'
      }`}
    >
      {loading && <Loader2 className="h-3 w-3 text-indigo-500 animate-spin" />}
    </span>
  </button>
);

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.07 } },
};
const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35 } },
};

export default function Settings() {
  const { user } = useAuthStore();
  const toast = useToast();
  const userRole = user?.role?.name || 'Employee';
  const isSuperAdmin = userRole === 'SuperAdmin';

  const [profileForm, setProfileForm] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
  });
  const [passwordForm, setPasswordForm] = useState({
    current: '', next: '', confirm: '',
  });
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);

  // Web3 toggle state (SuperAdmin only)
  const [web3Enabled, setWeb3Enabled] = useState(false);
  const [web3Loading, setWeb3Loading] = useState(false);
  const [web3Fetching, setWeb3Fetching] = useState(false);

  useEffect(() => {
    if (isSuperAdmin) fetchWeb3Status();
  }, [isSuperAdmin]);

  const fetchWeb3Status = async () => {
    setWeb3Fetching(true);
    try {
      const res = await adminService.getBlockchainStatus();
      setWeb3Enabled(res.data?.enabled ?? false);
    } catch {
      // backend may not be running — silently default to false
    } finally {
      setWeb3Fetching(false);
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSavingProfile(true);
    try {
      // API call would go here: await userService.updateProfile(profileForm);
      await new Promise((r) => setTimeout(r, 700)); // simulate
      toast({ message: 'Profile updated successfully.', type: 'success' });
    } catch {
      toast({ message: 'Failed to save profile. Please try again.', type: 'error' });
    } finally {
      setSavingProfile(false);
    }
  };

  const handleSavePassword = async (e) => {
    e.preventDefault();
    if (passwordForm.next !== passwordForm.confirm) {
      toast({ message: 'New passwords do not match.', type: 'error' });
      return;
    }
    if (passwordForm.next.length < 8) {
      toast({ message: 'Password must be at least 8 characters.', type: 'warning' });
      return;
    }
    setSavingPassword(true);
    try {
      // await authService.changePassword(passwordForm);
      await new Promise((r) => setTimeout(r, 700));
      toast({ message: 'Password changed successfully.', type: 'success' });
      setPasswordForm({ current: '', next: '', confirm: '' });
    } catch {
      toast({ message: 'Failed to update password.', type: 'error' });
    } finally {
      setSavingPassword(false);
    }
  };

  const handleWeb3Toggle = async () => {
    setWeb3Loading(true);
    const next = !web3Enabled;
    try {
      await adminService.toggleBlockchain(next);
      setWeb3Enabled(next);
      toast({
        message: next
          ? '✅ Blockchain anchoring enabled — transactions will consume gas.'
          : '⛔ Blockchain anchoring disabled — system in simulation mode.',
        type: next ? 'success' : 'warning',
        duration: 5000,
      });
    } catch {
      toast({ message: 'Failed to update blockchain setting.', type: 'error' });
    } finally {
      setWeb3Loading(false);
    }
  };

  return (
    <motion.div
      className="space-y-6 max-w-2xl"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Header */}
      <motion.div variants={itemVariants}>
        <h1 className="text-2xl font-bold text-white tracking-tight">Settings</h1>
        <p className="text-sm text-gray-400 mt-1">Manage your account preferences and security.</p>
      </motion.div>

      {/* Profile */}
      <motion.div variants={itemVariants}>
        <Section title="Profile" description="Your personal information" icon={User}>
          {/* Avatar row */}
          <div className="flex items-center gap-4 p-4 rounded-xl bg-gray-800/30 border border-gray-700/40 mb-5">
            <Avatar name={user?.full_name} size="lg" />
            <div>
              <p className="text-sm font-semibold text-white">{user?.full_name || '—'}</p>
              <p className="text-xs text-gray-400 mt-0.5">{user?.email || '—'}</p>
              <Badge variant="primary" className="mt-1.5 text-[10px]">
                {userRole}
              </Badge>
            </div>
          </div>

          <form onSubmit={handleSaveProfile} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Full name"
                value={profileForm.full_name}
                onChange={(e) => setProfileForm((p) => ({ ...p, full_name: e.target.value }))}
                required
              />
              <Input
                label="Email"
                type="email"
                value={profileForm.email}
                onChange={(e) => setProfileForm((p) => ({ ...p, email: e.target.value }))}
                required
              />
            </div>
            <Button type="submit" isLoading={savingProfile} className="gap-2">
              <Save className="h-4 w-4" />
              Save changes
            </Button>
          </form>
        </Section>
      </motion.div>

      {/* Security */}
      <motion.div variants={itemVariants}>
        <Section title="Security" description="Change your account password" icon={Shield}>
          <form onSubmit={handleSavePassword} className="space-y-4">
            <Input
              label="Current password"
              type="password"
              value={passwordForm.current}
              onChange={(e) => setPasswordForm((p) => ({ ...p, current: e.target.value }))}
              required
            />
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="New password"
                type="password"
                value={passwordForm.next}
                onChange={(e) => setPasswordForm((p) => ({ ...p, next: e.target.value }))}
                required
              />
              <Input
                label="Confirm new password"
                type="password"
                value={passwordForm.confirm}
                onChange={(e) => setPasswordForm((p) => ({ ...p, confirm: e.target.value }))}
                required
              />
            </div>
            <Button type="submit" isLoading={savingPassword} className="gap-2">
              <Key className="h-4 w-4" />
              Update password
            </Button>
          </form>
        </Section>
      </motion.div>

      {/* Notifications (placeholder) */}
      <motion.div variants={itemVariants}>
        <Section title="Notifications" description="Manage alerts and email preferences" icon={Bell}>
          <div className="space-y-4">
            {[
              { label: 'Late arrival alerts', sub: 'Get notified when employees clock in late' },
              { label: 'Daily attendance digest', sub: 'Receive a summary at end of each workday' },
              { label: 'Ticket updates', sub: 'Be alerted when your support tickets change status' },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-white">{item.label}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{item.sub}</p>
                </div>
                <Toggle enabled={false} onToggle={() => toast({ message: 'Notification preferences coming soon.', type: 'info' })} />
              </div>
            ))}
          </div>
        </Section>
      </motion.div>

      {/* SuperAdmin — Blockchain/Web3 Toggle */}
      {isSuperAdmin && (
        <motion.div variants={itemVariants}>
          <Section
            title="Blockchain Anchoring"
            description="SuperAdmin — Global Web3 audit trail control"
            icon={web3Enabled ? Zap : ZapOff}
          >
            <div className="rounded-xl border border-gray-700/50 bg-gray-800/20 divide-y divide-gray-800/50">
              {/* Status row */}
              <div className="flex items-center justify-between p-4">
                <div className="flex items-center gap-3">
                  <div className={`h-9 w-9 rounded-xl flex items-center justify-center ${web3Enabled ? 'bg-emerald-500/10' : 'bg-gray-700/50'}`}>
                    {web3Enabled
                      ? <Zap    className="h-5 w-5 text-emerald-400" />
                      : <ZapOff className="h-5 w-5 text-gray-500"    />}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white">
                      {web3Fetching ? 'Checking status…' : web3Enabled ? 'Anchoring Active' : 'Simulation Mode'}
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {web3Enabled
                        ? 'Each check-in is hashed and written to Ethereum.'
                        : 'No gas is consumed. Hashes are logged locally only.'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {!web3Fetching && (
                    <span className={`text-xs font-semibold px-2 py-1 rounded-full ${web3Enabled ? 'bg-emerald-500/15 text-emerald-400' : 'bg-gray-600/30 text-gray-400'}`}>
                      {web3Enabled ? 'LIVE' : 'OFF'}
                    </span>
                  )}
                  <Toggle
                    enabled={web3Enabled}
                    onToggle={handleWeb3Toggle}
                    loading={web3Loading}
                    disabled={web3Fetching}
                  />
                </div>
              </div>

              {/* Info row */}
              <div className="px-4 py-3 flex items-center justify-between">
                <p className="text-[11px] text-gray-500">
                  Configure <code className="text-gray-400 bg-gray-800 px-1 rounded">BLOCKCHAIN_PRIVATE_KEY</code> and <code className="text-gray-400 bg-gray-800 px-1 rounded">BLOCKCHAIN_URL</code> in your environment before enabling.
                </p>
                <button
                  onClick={fetchWeb3Status}
                  disabled={web3Fetching || web3Loading}
                  className="text-gray-500 hover:text-gray-300 transition-colors disabled:opacity-40 ml-3 shrink-0"
                  aria-label="Refresh status"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${web3Fetching ? 'animate-spin' : ''}`} />
                </button>
              </div>
            </div>
          </Section>
        </motion.div>
      )}
    </motion.div>
  );
}

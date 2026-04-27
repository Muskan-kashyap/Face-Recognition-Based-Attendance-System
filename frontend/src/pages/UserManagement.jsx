import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, UserPlus, Camera, X, Mail, Shield, Building, MoreVertical } from 'lucide-react';
import Webcam from 'react-webcam';
import { userService } from '../services/userService';
import { useAuthStore } from '../store/authStore';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { Spinner } from '../components/ui/Spinner';
import { EmptyState } from '../components/ui/EmptyState';
import { Avatar } from '../components/ui/Avatar';
import { titleCase, cn } from '../lib/utils';

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [enrollUser, setEnrollUser] = useState(null);
  const webcamRef = useRef(null);
  const { user: currentUser } = useAuthStore();
  const isAdmin = ['Admin', 'Manager'].includes(currentUser?.role?.name);

  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    role: 'Employee',
    organization: '',
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await userService.getUsers();
      setUsers(res.data || []);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await userService.createUser(form);
      setShowAdd(false);
      setForm({ full_name: '', email: '', password: '', role: 'Employee', organization: '' });
      fetchUsers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create user');
    }
  };

  const handleEnroll = async () => {
    if (!webcamRef.current || !enrollUser) return;
    try {
      const mockEmbedding = Array.from({ length: 128 }, () => Math.random());
      await userService.enrollFace(enrollUser.id, mockEmbedding);
      setEnrollUser(null);
      fetchUsers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Enrollment failed');
    }
  };

  const filtered = users.filter((u) =>
    (u.full_name || '').toLowerCase().includes(search.toLowerCase()) ||
    (u.email || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <motion.div 
      className="space-y-6 lg:space-y-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">Organization Users</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage employee accounts and biometric enrollments.</p>
        </div>
        {isAdmin && (
          <Button onClick={() => setShowAdd(true)} className="shadow-lg shadow-primary-500/30 hover:scale-105 transition-transform">
            <UserPlus className="mr-2 h-5 w-5" />
            Add Employee
          </Button>
        )}
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-11 pr-4 py-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-sm focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all shadow-sm"
          />
        </div>
      </div>

      <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.1 }}>
        <Card className="overflow-hidden border-0 shadow-xl shadow-slate-200/50 dark:shadow-none">
          <CardContent className="p-0">
            {loading ? (
              <div className="flex items-center justify-center py-32">
                <Spinner size="xl" className="text-primary-500" />
              </div>
            ) : filtered.length === 0 ? (
              <EmptyState
                icon={Shield}
                title="No users found"
                description="Try adjusting your search or add a new employee."
                actionText="Add Employee"
                onAction={() => setShowAdd(true)}
              />
            ) : (
              <div className="overflow-x-auto hide-scrollbar">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50/80 dark:bg-slate-800/50 backdrop-blur-sm border-b border-slate-100 dark:border-slate-800">
                      <th className="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Employee</th>
                      <th className="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Role</th>
                      <th className="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Organization</th>
                      <th className="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 bg-white dark:bg-transparent">
                    {filtered.map((u) => (
                      <tr key={u.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors group">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-4">
                            <Avatar name={u.full_name} size="md" className="shadow-sm border border-slate-100 dark:border-slate-800" />
                            <div>
                              <p className="text-sm font-semibold text-slate-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">{u.full_name}</p>
                              <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1 mt-0.5">
                                <Mail className="h-3 w-3" /> {u.email}
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <Badge
                            variant={
                              u.role?.name === 'Admin'
                                ? 'danger'
                                : u.role?.name === 'Manager'
                                ? 'warning'
                                : 'primary'
                            }
                            className="font-medium px-2.5 py-1"
                          >
                            {u.role?.name}
                          </Badge>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-1.5 text-sm text-slate-600 dark:text-slate-400">
                            <Building className="h-4 w-4 opacity-70" />
                            {u.organization?.name || '-'}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <span className={cn(`h-2.5 w-2.5 rounded-full shadow-sm`, u.is_active ? 'bg-emerald-500 shadow-emerald-500/20' : 'bg-slate-300 dark:bg-slate-600')} />
                            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{u.is_active ? 'Active' : 'Inactive'}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-right">
                          {isAdmin && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-500/10"
                              onClick={() => setEnrollUser(u)}
                            >
                              <Camera className="mr-2 h-4 w-4" />
                              Enroll Face
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Add user modal */}
      <AnimatePresence>
        {showAdd && (
          <Modal
            isOpen={showAdd}
            onClose={() => setShowAdd(false)}
            title="Add New Employee"
            description="Create a new account for organization access."
          >
            <form onSubmit={handleCreate} className="space-y-4 mt-2">
              <Input
                label="Full Name"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                required
                className="bg-slate-50 dark:bg-slate-900/50"
              />
              <Input
                label="Email Address"
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
                className="bg-slate-50 dark:bg-slate-900/50"
              />
              <Input
                label="Temporary Password"
                type="password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
                className="bg-slate-50 dark:bg-slate-900/50"
              />
              <div className="grid grid-cols-2 gap-4">
                <Select
                  label="Role Assignment"
                  value={form.role}
                  onChange={(e) => setForm({ ...form, role: e.target.value })}
                  options={[
                    { value: 'Employee', label: 'Employee' },
                    { value: 'Manager', label: 'Manager' },
                    { value: 'Admin', label: 'Admin' },
                  ]}
                  className="bg-slate-50 dark:bg-slate-900/50"
                />
                <Input
                  label="Organization / Dept"
                  value={form.organization}
                  onChange={(e) => setForm({ ...form, organization: e.target.value })}
                  required
                  className="bg-slate-50 dark:bg-slate-900/50"
                />
              </div>
              <div className="flex gap-3 pt-6 border-t border-slate-100 dark:border-slate-800 mt-6">
                <Button type="button" variant="ghost" className="flex-1" onClick={() => setShowAdd(false)}>
                  Cancel
                </Button>
                <Button type="submit" className="flex-1 shadow-lg shadow-primary-500/20">
                  Provision Account
                </Button>
              </div>
            </form>
          </Modal>
        )}
      </AnimatePresence>

      {/* Enroll face modal */}
      <AnimatePresence>
        {enrollUser && (
          <Modal
            isOpen={!!enrollUser}
            onClose={() => setEnrollUser(null)}
            title="Biometric Enrollment"
            description={`Register neural face template for ${enrollUser?.full_name}`}
          >
            <div className="space-y-6 mt-4">
              <div className="relative aspect-video bg-black/80 rounded-2xl overflow-hidden shadow-inner">
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 border-[3px] border-emerald-500/30 rounded-2xl pointer-events-none" />
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="w-40 h-56 border-2 border-emerald-400/50 border-dashed rounded-full shadow-[0_0_0_9999px_rgba(0,0,0,0.6)]" />
                </div>
              </div>
              <div className="bg-emerald-50 dark:bg-emerald-900/20 p-4 rounded-xl border border-emerald-100 dark:border-emerald-800/30">
                <p className="text-sm text-emerald-700 dark:text-emerald-400 flex items-start gap-2">
                  <Shield className="h-5 w-5 shrink-0" />
                  Ensure the user's face is clearly visible, well-lit, and centered within the dashed oval.
                </p>
              </div>
              <div className="flex gap-3 pt-4 border-t border-slate-100 dark:border-slate-800">
                <Button variant="ghost" className="flex-1" onClick={() => setEnrollUser(null)}>
                  Cancel
                </Button>
                <Button className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-500/20" onClick={handleEnroll}>
                  Extract & Save Template
                </Button>
              </div>
            </div>
          </Modal>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/**
 * Overview Dashboard
 * Cleaned of 398 lines of dead commented code.
 * All business logic preserved. Unified dark design system.
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Users, Clock, TrendingUp, AlertTriangle,
  Camera, Ticket, Receipt, ArrowRight, Activity,
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts';
import { attendanceService } from '../services/attendanceService';
import { userService } from '../services/userService';
import { ticketService } from '../services/ticketService';
import { useAuthStore } from '../store/authStore';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Spinner } from '../components/ui/Spinner';
import { formatTime, formatDate, titleCase, cn } from '../lib/utils';

/* ─── Animation variants ─────────────────────────────────────── */
const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
};
const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
};

/* ─── KPI Stat Card ──────────────────────────────────────────── */
const StatCard = ({ icon: Icon, label, value, accent, trend }) => (
  <motion.div variants={item}>
    <Card className="relative overflow-hidden group h-full border-gray-800/60">
      {/* Left accent bar */}
      <span className={cn('absolute left-0 top-0 h-full w-1 rounded-l-xl', accent)} />
      <CardContent className="p-5 pl-6">
        <div className="flex items-start justify-between">
          <div className={cn('h-11 w-11 rounded-xl flex items-center justify-center transition-transform group-hover:scale-105', accent + '/10')}>
            <Icon className={cn('h-5 w-5', accent.replace('bg-', 'text-'))} />
          </div>
          {trend !== undefined && (
            <span className={cn('text-xs font-bold px-2 py-1 rounded-full',
              trend >= 0
                ? 'bg-emerald-500/10 text-emerald-400'
                : 'bg-red-500/10 text-red-400'
            )}>
              {trend >= 0 ? '+' : ''}{trend}%
            </span>
          )}
        </div>
        <div className="mt-4">
          <p className="text-2xl font-extrabold text-white tracking-tight">{value}</p>
          <p className="text-xs font-medium text-gray-500 mt-1">{label}</p>
        </div>
      </CardContent>
    </Card>
  </motion.div>
);

/* ─── Custom chart tooltip ───────────────────────────────────── */
const ChartTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl px-3 py-2 shadow-xl text-sm">
      <p className="text-gray-400 mb-1">{label}</p>
      <p className="font-bold text-indigo-400">{payload[0].value} check-ins</p>
    </div>
  );
};

/* ─── Main Component ─────────────────────────────────────────── */
export default function Overview() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchDashboardData(); }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [logsRes, usersRes, ticketsRes] = await Promise.all([
        attendanceService.getLogs({ limit: 100 }),
        userService.getUsers(),
        ticketService.getTickets({ limit: 10 }),
      ]);

      const allLogs    = logsRes.data    || [];
      const allUsers   = usersRes.data   || [];
      const allTickets = ticketsRes.data || [];

      const today     = new Date().toDateString();
      const todayLogs = allLogs.filter((l) => new Date(l.check_in).toDateString() === today);

      setStats({
        totalEmployees: allUsers.length,
        todayCheckins:  todayLogs.length,
        onTime:         todayLogs.filter((l) => l.status === 'on_time').length,
        late:           todayLogs.filter((l) => l.status === 'late').length,
        openTickets:    allTickets.filter((t) => t.status === 'open').length,
      });

      setLogs(allLogs.slice(0, 8));
      setTickets(allTickets.slice(0, 4));

      // Build 7-day chart data
      const days = [];
      for (let i = 6; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        const dayStr = d.toDateString();
        days.push({
          name:     d.toLocaleDateString('en', { weekday: 'short' }),
          checkins: allLogs.filter((l) => new Date(l.check_in).toDateString() === dayStr).length,
        });
      }
      setChartData(days);
    } catch (err) {
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner size="xl" className="text-indigo-500" />
      </div>
    );
  }

  return (
    <motion.div
      className="space-y-6"
      variants={container}
      initial="hidden"
      animate="visible"
    >
      {/* ── Page Header ───────────────────────────────────────── */}
      <motion.div variants={item} className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Overview</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Welcome back,{' '}
            <span className="font-semibold text-gray-300">{user?.full_name || 'User'}</span>
          </p>
        </div>
        <Button
          onClick={() => navigate('/dashboard/attendance')}
          className="shadow-lg shadow-indigo-500/20 hover:scale-[1.02] transition-transform"
        >
          <Camera className="mr-2 h-4 w-4" />
          Check In Now
        </Button>
      </motion.div>

      {/* ── KPI Cards ─────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Users}         label="Total Employees"   value={stats?.totalEmployees ?? 0} accent="bg-blue-500"    />
        <StatCard icon={Clock}         label="Today's Check-ins" value={stats?.todayCheckins  ?? 0} accent="bg-emerald-500" />
        <StatCard icon={TrendingUp}    label="On Time"           value={stats?.onTime         ?? 0} accent="bg-indigo-500" trend={12} />
        <StatCard icon={AlertTriangle} label="Late Arrivals"     value={stats?.late           ?? 0} accent="bg-amber-500"  />
      </div>

      {/* ── Chart + Quick Actions ─────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Area Chart — 2/3 width */}
        <motion.div variants={item} className="lg:col-span-2">
          <Card className="h-full border-gray-800/60">
            <CardHeader className="pb-0">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-white text-base">Attendance Trends</CardTitle>
                  <CardDescription className="text-gray-500 text-xs mt-0.5">7-day check-in history</CardDescription>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium bg-emerald-500/10 px-2 py-1 rounded-full">
                  <Activity className="h-3 w-3" />
                  Live
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-4 min-h-[280px]">
              <ResponsiveContainer width="100%" height={260}>
                <AreaChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="checkinGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0}    />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#475569', fontSize: 11 }} dy={8} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#475569', fontSize: 11 }} />
                  <Tooltip content={<ChartTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="checkins"
                    stroke="#6366f1"
                    strokeWidth={2.5}
                    fill="url(#checkinGrad)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Quick Actions — 1/3 width */}
        <motion.div variants={item}>
          <Card className="h-full bg-gradient-to-br from-indigo-600 to-violet-700 border-0 text-white">
            <CardHeader>
              <CardTitle className="text-white text-base">Quick Actions</CardTitle>
              <CardDescription className="text-indigo-200 text-xs">Frequently used shortcuts</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {[
                { label: 'Open IT Ticket', sub: `${stats?.openTickets || 0} open`, icon: Ticket, path: '/dashboard/ticketing' },
                { label: 'Submit Expense', sub: 'Reimbursement',                   icon: Receipt, path: '/dashboard/reimbursements' },
              ].map((action) => (
                <button
                  key={action.path}
                  onClick={() => navigate(action.path)}
                  className="w-full flex items-center justify-between p-3 bg-white/10 hover:bg-white/20 rounded-xl transition-all border border-white/10 group"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-1.5 bg-white/10 rounded-lg">
                      <action.icon className="h-4 w-4" />
                    </div>
                    <div className="text-left">
                      <p className="text-sm font-medium">{action.label}</p>
                      <p className="text-[10px] text-indigo-200">{action.sub}</p>
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 opacity-40 group-hover:opacity-80 group-hover:translate-x-0.5 transition-all" />
                </button>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* ── Activity + Tickets ────────────────────────────────── */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {/* Recent check-ins */}
        <motion.div variants={item}>
          <Card className="h-full border-gray-800/60">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-white text-base">Recent Check-ins</CardTitle>
                <CardDescription className="text-gray-500 text-xs mt-0.5">Live activity feed</CardDescription>
              </div>
              <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard/attendance')}
                className="text-indigo-400 hover:text-indigo-300 text-xs">
                View all
              </Button>
            </CardHeader>
            <CardContent className="p-0">
              {logs.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-10 text-gray-600">
                  <Clock className="h-8 w-8 mb-2 opacity-30" />
                  <p className="text-sm">No activity recorded yet</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-800/60">
                  {logs.map((log) => (
                    <div key={log.id} className="flex items-center justify-between px-5 py-3 hover:bg-gray-800/30 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="h-9 w-9 rounded-full bg-indigo-500/10 text-indigo-400 flex items-center justify-center font-bold text-sm shrink-0">
                          {(log.user_name || 'U')[0].toUpperCase()}
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-white leading-tight">{log.user_name || 'User'}</p>
                          <p className="text-[11px] text-gray-500 mt-0.5">{formatDate(log.check_in)} · {formatTime(log.check_in)}</p>
                        </div>
                      </div>
                      <Badge
                        variant={log.status === 'on_time' ? 'success' : log.status === 'late' ? 'warning' : 'default'}
                        className="text-[11px] px-2 py-0.5"
                      >
                        {titleCase(log.status)}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Active Tickets */}
        <motion.div variants={item}>
          <Card className="h-full border-gray-800/60">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-white text-base">Active Tickets</CardTitle>
                <CardDescription className="text-gray-500 text-xs mt-0.5">Recent support requests</CardDescription>
              </div>
              <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard/ticketing')}
                className="text-indigo-400 hover:text-indigo-300 text-xs">
                View all
              </Button>
            </CardHeader>
            <CardContent className="p-0">
              {tickets.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-10 text-gray-600">
                  <Ticket className="h-8 w-8 mb-2 opacity-30" />
                  <p className="text-sm">No active tickets</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-800/60">
                  {tickets.map((t) => (
                    <div key={t.id} className="flex items-center justify-between px-5 py-3 hover:bg-gray-800/30 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 shrink-0">
                          <Ticket className="h-4 w-4" />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-white leading-tight">{t.title}</p>
                          <p className="text-[11px] text-gray-500 mt-0.5">
                            {t.created_at ? formatDate(t.created_at) : 'Just now'}
                          </p>
                        </div>
                      </div>
                      <Badge
                        variant={t.status === 'resolved' ? 'success' : t.status === 'open' ? 'primary' : 'warning'}
                        className="text-[11px] px-2 py-0.5 capitalize"
                      >
                        {t.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}

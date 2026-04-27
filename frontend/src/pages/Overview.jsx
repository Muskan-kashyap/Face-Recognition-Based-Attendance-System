// import React, { useEffect, useState } from 'react';
// import { useNavigate } from 'react-router-dom';
// import {
//   Users,
//   Clock,
//   TrendingUp,
//   AlertTriangle,
//   ArrowRight,
//   Camera,
//   Ticket,
//   Receipt,
// } from 'lucide-react';
// import {
//   AreaChart,
//   Area,
//   XAxis,
//   YAxis,
//   CartesianGrid,
//   Tooltip,
//   ResponsiveContainer,
// } from 'recharts';
// import { attendanceService } from '../services/attendanceService';
// import { userService } from '../services/userService';
// import { ticketService } from '../services/ticketService';
// import { useAuthStore } from '../store/authStore';
// import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
// import { Button } from '../components/ui/Button';
// import { Badge } from '../components/ui/Badge';
// import { Spinner } from '../components/ui/Spinner';
// import { formatTime, formatDate, titleCase } from '../lib/utils';

// export default function Overview() {
//   const { user } = useAuthStore();
//   const navigate = useNavigate();
//   const [stats, setStats] = useState(null);
//   const [logs, setLogs] = useState([]);
//   const [tickets, setTickets] = useState([]);
//   const [chartData, setChartData] = useState([]);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     fetchDashboardData();
//   }, []);

//   const fetchDashboardData = async () => {
//     setLoading(true);
//     try {
//       const [logsRes, usersRes, ticketsRes] = await Promise.all([
//         attendanceService.getLogs({ limit: 100 }),
//         userService.getUsers(),
//         ticketService.getTickets({ limit: 10 }),
//       ]);

//       const allLogs = logsRes.data || [];
//       const allUsers = usersRes.data || [];
//       const allTickets = ticketsRes.data || [];

//       // Compute stats
//       const today = new Date().toDateString();
//       const todayLogs = allLogs.filter((l) => new Date(l.check_in).toDateString() === today);

//       setStats({
//         totalEmployees: allUsers.length,
//         todayCheckins: todayLogs.length,
//         onTime: todayLogs.filter((l) => l.status === 'on_time').length,
//         late: todayLogs.filter((l) => l.status === 'late').length,
//         openTickets: allTickets.filter((t) => t.status === 'open').length,
//       });

//       setLogs(allLogs.slice(0, 10));
//       setTickets(allTickets.slice(0, 5));

//       // Build chart data for last 7 days
//       const days = [];
//       for (let i = 6; i >= 0; i--) {
//         const d = new Date();
//         d.setDate(d.getDate() - i);
//         const dayStr = d.toDateString();
//         const count = allLogs.filter((l) => new Date(l.check_in).toDateString() === dayStr).length;
//         days.push({
//           name: d.toLocaleDateString('en', { weekday: 'short' }),
//           checkins: count,
//         });
//       }
//       setChartData(days);
//     } catch {
//       // silent fail
//     } finally {
//       setLoading(false);
//     }
//   };

//   const StatCard = ({ icon: Icon, label, value, trend, trendLabel, color }) => (
//     <Card>
//       <CardContent className="p-6">
//         <div className="flex items-center justify-between">
//           <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${color}`}>
//             <Icon className="h-5 w-5 text-white" />
//           </div>
//           {trend !== undefined && (
//             <span className={`text-xs font-medium ${trend >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
//               {trend >= 0 ? '+' : ''}{trend}%
//             </span>
//           )}
//         </div>
//         <div className="mt-4">
//           <p className="text-2xl font-bold text-slate-900">{value}</p>
//           <p className="text-sm text-slate-500">{label}</p>
//         </div>
//       </CardContent>
//     </Card>
//   );

//   if (loading) {
//     return (
//       <div className="flex items-center justify-center h-96">
//         <Spinner size="lg" />
//       </div>
//     );
//   }

//   return (
//     <div className="space-y-8">
//       {/* Header */}
//       <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
//         <div>
//           <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
//           <p className="text-sm text-slate-500 mt-1">
//             Welcome back, {user?.full_name || 'User'}
//           </p>
//         </div>
//         <div className="flex gap-3">
//           <Button onClick={() => navigate('/dashboard/attendance')}>
//             <Camera className="mr-2 h-4 w-4" />
//             Check in
//           </Button>
//         </div>
//         </div>
        

//       {/* Stats grid */}
//       <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
//         <StatCard
//           icon={Users}
//           label="Total Employees"
//           value={stats?.totalEmployees || 0}
//           color="bg-primary-600"
//         />
//         <StatCard
//           icon={Clock}
//           label="Today's Check-ins"
//           value={stats?.todayCheckins || 0}
//           color="bg-success-600"
//         />
//         <StatCard
//           icon={TrendingUp}
//           label="On Time"
//           value={stats?.onTime || 0}
//           color="bg-info-600"
//         />
//         <StatCard
//           icon={AlertTriangle}
//           label="Late Arrivals"
//           value={stats?.late || 0}
//           color="bg-warning-600"
//         />
//       </div>

//       <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
//         {/* Chart */}
//         <Card className="lg:col-span-2">
//           <CardHeader>
//             <CardTitle>Attendance Trend</CardTitle>
//             <CardDescription>Check-ins over the last 7 days</CardDescription>
//           </CardHeader>
//           <CardContent>
//             <div className="h-72">
//               <ResponsiveContainer width="100%" height="100%">
//                 <AreaChart data={chartData}>
//                   <defs>
//                     <linearGradient id="colorCheckins" x1="0" y1="0" x2="0" y2="1">
//                       <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2} />
//                       <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
//                     </linearGradient>
//                   </defs>
//                   <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
//                   <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
//                   <YAxis stroke="#94a3b8" fontSize={12} />
//                   <Tooltip
//                     contentStyle={{
//                       borderRadius: '8px',
//                       border: '1px solid #e2e8f0',
//                       boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
//                     }}
//                   />
//                   <Area
//                     type="monotone"
//                     dataKey="checkins"
//                     stroke="#6366f1"
//                     strokeWidth={2}
//                     fillOpacity={1}
//                     fill="url(#colorCheckins)"
//                   />
//                 </AreaChart>
//               </ResponsiveContainer>
//             </div>
//           </CardContent>
//         </Card>

//         {/* Quick links */}
//         <Card>
//           <CardHeader>
//             <CardTitle>Quick Actions</CardTitle>
//           </CardHeader>
//           <CardContent className="space-y-3">
//             <Button
//               variant="secondary"
//               className="w-full justify-between"
//               onClick={() => navigate('/dashboard/ticketing')}
//             >
//               <span className="flex items-center">
//                 <Ticket className="mr-2 h-4 w-4" />
//                 Open a ticket
//               </span>
//               {stats?.openTickets > 0 && <Badge variant="warning">{stats.openTickets}</Badge>}
//             </Button>
//             <Button
//               variant="secondary"
//               className="w-full justify-between"
//               onClick={() => navigate('/dashboard/reimbursements')}
//             >
//               <span className="flex items-center">
//                 <Receipt className="mr-2 h-4 w-4" />
//                 Submit expense
//               </span>
//               <ArrowRight className="h-4 w-4 text-slate-400" />
//             </Button>
//             <Button
//               variant="secondary"
//               className="w-full justify-between"
//               onClick={() => navigate('/dashboard/users')}
//             >
//               <span className="flex items-center">
//                 <Users className="mr-2 h-4 w-4" />
//                 Manage users
//               </span>
//               <ArrowRight className="h-4 w-4 text-slate-400" />
//             </Button>
//           </CardContent>
//         </Card>
//       </div>

//       <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
//         {/* Recent activity */}
//         <Card>
//           <CardHeader className="flex flex-row items-center justify-between">
//             <div>
//               <CardTitle>Recent Activity</CardTitle>
//               <CardDescription>Latest check-ins across the organization</CardDescription>
//             </div>
//             <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard/attendance')}>
//               View all
//             </Button>
//           </CardHeader>
        
//           {/* <CardContent>
//             <div className="space-y-3">
//               {logs.length === 0 ? (
//                 <p className="text-sm text-slate-500 text-center py-8">No recent activity</p>
//               ) : (
//                 logs.map((log) => (
//                   <div key={log.id} className="flex items-center justify-between py-2">
//                     <div className="flex items-center gap-3">
//                       <div className="h-8 w-8 rounded-full bg-slate-100 flex items-center justify-center text-xs font-medium text-slate-600">
//                         {(log.user_name || '?')[0]}
//                       </div>
//                       <div>
//                         <p className="text-sm font-medium text-slate-900">{log.user_name || `User #${log.user_id}`}</p>
//                         <p className="text-xs text-slate-500">{formatDate(log.check_in)}</p>
//                       </div>
//                     <div className="text-right">
//                       <Badge
//                         variant={
//                           log.status === 'on_time'
//                             ? 'success'
//                             : log.status === 'late'
//                             ? 'warning'
//                             : 'default'
//                         }
//                       >
//                         {titleCase(log.status)}
//                       </Badge>
//                       <p className="text-xs text-slate-500 mt-1">{formatTime(log.check_in)}</p>
//                     </div>
//                 ))
//               )}
//             </div>
//           </CardContent>
//         </Card> */}
//         <CardContent>
//             <div className="space-y-3">
//                 {logs.length === 0 ? (
//                 <p className="text-sm text-slate-500 text-center py-8">
//                     No recent activity
//                 </p>
//                 ) : (
//                 logs.map((log) => (
//                     <div
//                     key={log.id}
//                     className="flex items-center justify-between py-2"
//                     >
//                     {/* Left */}
//                     <div className="flex items-center gap-3">
//                         <div className="h-8 w-8 rounded-full bg-slate-100 flex items-center justify-center text-xs font-medium text-slate-600">
//                         {(log.user_name || '?')[0]}
//                         </div>
//                         <div>
//                         <p className="text-sm font-medium text-slate-900">
//                             {log.user_name || `User #${log.user_id}`}
//                         </p>
//                         <p className="text-xs text-slate-500">
//                             {formatDate(log.check_in)}
//                         </p>
//                         </div>
//                     </div>

//                     {/* Right */}
//                     <div className="text-right">
//                         <Badge
//                         variant={
//                             log.status === 'on_time'
//                             ? 'success'
//                             : log.status === 'late'
//                             ? 'warning'
//                             : 'default'
//                         }
//                         >
//                         {titleCase(log.status)}
//                         </Badge>
//                         <p className="text-xs text-slate-500 mt-1">
//                         {formatTime(log.check_in)}
//                         </p>
//                     </div>
//                     </div>
//                 ))
//                 )}
//             </div>
//             </CardContent>
//         </Card>
        

//         {/* Recent tickets */}
//         <Card>
//           <CardHeader className="flex flex-row items-center justify-between">
//             <div>
//               <CardTitle>Recent Tickets</CardTitle>
//               <CardDescription>Latest support requests</CardDescription>
//             </div>
//             <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard/ticketing')}>
//               View all
//             </Button>
//           </CardHeader>
//           <CardContent>
//             <div className="space-y-3">
//               {tickets.length === 0 ? (
//                 <p className="text-sm text-slate-500 text-center py-8">No tickets yet</p>
//               ) : (
//                 tickets.map((ticket) => (
//                   <div key={ticket.id} className="flex items-center justify-between py-2">
//                     <div>
//                       <p className="text-sm font-medium text-slate-900">{ticket.title}</p>
//                       <p className="text-xs text-slate-500">
//                         {ticket.created_at ? formatDate(ticket.created_at) : 'N/A'}
//                       </p>
//                     </div>
//                     <Badge
//                       variant={
//                         ticket.status === 'resolved'
//                           ? 'success'
//                           : ticket.status === 'open'
//                           ? 'primary'
//                           : ticket.status === 'escalated'
//                           ? 'danger'
//                           : 'default'
//                       }
//                     >
//                       {titleCase(ticket.status)}
//                     </Badge>
//                   </div>
//                 ))
//               )}
//             </div>
//           </CardContent>
//         </Card>
//       </div>
//   );
// }

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Users,
  Clock,
  TrendingUp,
  AlertTriangle,
  Camera,
  Ticket,
  Receipt,
  ArrowRight
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
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

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } }
};

export default function Overview() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [logsRes, usersRes, ticketsRes] = await Promise.all([
        attendanceService.getLogs({ limit: 100 }),
        userService.getUsers(),
        ticketService.getTickets({ limit: 10 }),
      ]);

      const allLogs = logsRes.data || [];
      const allUsers = usersRes.data || [];
      const allTickets = ticketsRes.data || [];

      const today = new Date().toDateString();
      const todayLogs = allLogs.filter(
        (l) => new Date(l.check_in).toDateString() === today
      );

      setStats({
        totalEmployees: allUsers.length,
        todayCheckins: todayLogs.length,
        onTime: todayLogs.filter((l) => l.status === 'on_time').length,
        late: todayLogs.filter((l) => l.status === 'late').length,
        openTickets: allTickets.filter((t) => t.status === 'open').length,
      });

      setLogs(allLogs.slice(0, 8));
      setTickets(allTickets.slice(0, 4));

      const days = [];
      for (let i = 6; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        const dayStr = d.toDateString();

        const count = allLogs.filter(
          (l) => new Date(l.check_in).toDateString() === dayStr
        ).length;

        days.push({
          name: d.toLocaleDateString('en', { weekday: 'short' }),
          checkins: count,
        });
      }
      setChartData(days);
    } catch (err) {
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, label, value, trend, color, bgClass }) => (
    <motion.div variants={itemVariants}>
      <Card className="h-full border-0 relative overflow-hidden group">
        <div className={cn("absolute top-0 left-0 w-1 h-full", bgClass)} />
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className={cn(`h-12 w-12 rounded-xl flex items-center justify-center transition-transform group-hover:scale-110`, bgClass)}>
              <Icon className="h-6 w-6 text-white" />
            </div>
            {trend !== undefined && (
              <span className={cn(`text-xs font-bold px-2 py-1 rounded-full bg-slate-100 dark:bg-slate-800`, trend >= 0 ? 'text-green-500' : 'text-red-500')}>
                {trend >= 0 ? '+' : ''}{trend}%
              </span>
            )}
          </div>
          <div className="mt-5">
            <p className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">{value}</p>
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400 mt-1">{label}</p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner size="xl" className="text-primary-500" />
      </div>
    );
  }

  return (
    <motion.div 
      className="space-y-6 lg:space-y-8"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">Overview</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Welcome back, <span className="font-semibold text-slate-700 dark:text-slate-300">{user?.full_name || 'User'}</span>
          </p>
        </div>
        <Button onClick={() => navigate('/dashboard/attendance')} className="shadow-lg shadow-primary-500/30 hover:scale-105 transition-transform">
          <Camera className="mr-2 h-5 w-5" />
          Check In Now
        </Button>
      </motion.div>

      {/* Stats Bento */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
        <StatCard icon={Users} label="Total Employees" value={stats?.totalEmployees || 0} bgClass="bg-blue-600" />
        <StatCard icon={Clock} label="Today's Check-ins" value={stats?.todayCheckins || 0} bgClass="bg-emerald-500" />
        <StatCard icon={TrendingUp} label="On Time" value={stats?.onTime || 0} bgClass="bg-indigo-500" trend={12} />
        <StatCard icon={AlertTriangle} label="Late Arrivals" value={stats?.late || 0} bgClass="bg-amber-500" />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-6">
        {/* Chart */}
        <motion.div variants={itemVariants} className="lg:col-span-2 h-full">
          <Card className="h-full flex flex-col">
            <CardHeader className="pb-2">
              <CardTitle>Attendance Trends</CardTitle>
              <CardDescription>7-day check-in history</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 min-h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorCheckins" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                  <Tooltip 
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                  />
                  <Area type="monotone" dataKey="checkins" stroke="#6366f1" strokeWidth={3} fill="url(#colorCheckins)" />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Quick Actions Stack */}
        <motion.div variants={itemVariants} className="flex flex-col gap-4 lg:gap-6">
          <Card className="flex-1 bg-gradient-to-br from-indigo-500 to-purple-600 border-0 text-white">
            <CardHeader>
              <CardTitle className="text-white">Quick Actions</CardTitle>
              <CardDescription className="text-indigo-100">Need something done fast?</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <button onClick={() => navigate('/dashboard/ticketing')} className="w-full flex items-center justify-between p-3 bg-white/10 hover:bg-white/20 rounded-xl transition-colors backdrop-blur-sm border border-white/10">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white/10 rounded-lg"><Ticket className="h-4 w-4" /></div>
                  <span className="font-medium text-sm">Open IT Ticket</span>
                </div>
                <ArrowRight className="h-4 w-4 opacity-50" />
              </button>
              <button onClick={() => navigate('/dashboard/reimbursements')} className="w-full flex items-center justify-between p-3 bg-white/10 hover:bg-white/20 rounded-xl transition-colors backdrop-blur-sm border border-white/10">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white/10 rounded-lg"><Receipt className="h-4 w-4" /></div>
                  <span className="font-medium text-sm">Submit Expense</span>
                </div>
                <ArrowRight className="h-4 w-4 opacity-50" />
              </button>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Activity & Tickets Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 lg:gap-6">
        {/* Activity */}
        <motion.div variants={itemVariants}>
          <Card className="h-full">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Recent Check-ins</CardTitle>
                <CardDescription>Live feed of organization activity</CardDescription>
              </div>
              <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard/attendance')} className="text-primary-600 hover:bg-primary-50">
                View All
              </Button>
            </CardHeader>
            <CardContent>
              {logs.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 text-slate-400">
                  <Clock className="h-8 w-8 mb-2 opacity-50" />
                  <p className="text-sm">No activity recorded yet</p>
                </div>
              ) : (
                <div className="space-y-1">
                  {logs.map((log) => (
                    <div key={log.id} className="flex items-center justify-between py-3 px-2 hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-xl transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold text-sm">
                          {(log.user_name || 'U')[0].toUpperCase()}
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-slate-900 dark:text-white">{log.user_name || 'User'}</p>
                          <p className="text-xs text-slate-500 dark:text-slate-400">{formatDate(log.check_in)} at {formatTime(log.check_in)}</p>
                        </div>
                      </div>
                      <Badge variant={log.status === 'on_time' ? 'success' : log.status === 'late' ? 'warning' : 'default'} className="px-3 py-1">
                        {titleCase(log.status)}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Tickets */}
        <motion.div variants={itemVariants}>
          <Card className="h-full">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Active Tickets</CardTitle>
                <CardDescription>Recent support requests</CardDescription>
              </div>
              <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard/ticketing')} className="text-primary-600 hover:bg-primary-50">
                View All
              </Button>
            </CardHeader>
            <CardContent>
              {tickets.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 text-slate-400">
                  <Ticket className="h-8 w-8 mb-2 opacity-50" />
                  <p className="text-sm">No active tickets</p>
                </div>
              ) : (
                <div className="space-y-1">
                  {tickets.map((t) => (
                    <div key={t.id} className="flex items-center justify-between py-3 px-2 hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-xl transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded-lg bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400">
                          <Ticket className="h-4 w-4" />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-slate-900 dark:text-white">{t.title}</p>
                          <p className="text-xs text-slate-500 dark:text-slate-400">{t.created_at ? formatDate(t.created_at) : 'Just now'}</p>
                        </div>
                      </div>
                      <Badge variant={t.status === 'resolved' ? 'success' : t.status === 'open' ? 'primary' : 'warning'} className="px-3 py-1 capitalize">
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
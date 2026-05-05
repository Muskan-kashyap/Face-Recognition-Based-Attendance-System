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
  ArrowRight,
  Shield,
  Database,
  BarChart3,
  Settings
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
import { useAuthStore } from '../store/authStore';
import { attendanceService } from '../services/attendanceService';
import { userService } from '../services/userService';
import { ticketService } from '../services/ticketService';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Spinner } from '../components/ui/Spinner';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4 } }
};

// 🔥 NEW: Role-specific data & UI
const RoleDashboard = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [stats, setStats] = useState({});
  const [logs, setLogs] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  const role = (typeof user?.role === 'string' ? user.role : user?.role?.name || 'employee').toLowerCase();
  const roleDisplay = role.charAt(0).toUpperCase() + role.slice(1);

  useEffect(() => {
    fetchRoleData();
  }, [role]);

  const fetchRoleData = async () => {
    setLoading(true);
    try {
      const requests = [];
      
      if (role === 'employee') {
        // Personal data only
        requests.push(attendanceService.getMyAttendance());
        requests.push(ticketService.getMyTickets());
      } else if (role === 'manager') {
        // Team data
        requests.push(attendanceService.getTeamLogs());
        requests.push(ticketService.getTeamTickets());
        requests.push(userService.getTeamUsers());
      } else if (role === 'admin') {
        // Org data
        requests.push(attendanceService.getOrgLogs());
        requests.push(ticketService.getOrgTickets());
        requests.push(userService.getUsers());
      } else { // superadmin
        // All data
        requests.push(attendanceService.getAllLogs());
        requests.push(ticketService.getAllTickets());
        requests.push(userService.getAllUsers());
      }

      const [logsRes, ticketsRes, usersRes] = await Promise.all(requests.slice(0,3));

      const allLogs = logsRes?.data || [];
      const allUsers = usersRes?.data || [];
      const allTickets = ticketsRes?.data || [];

      // Role-specific stats
      const today = new Date().toDateString();
      const todayLogs = allLogs.filter(l => new Date(l.check_in).toDateString() === today);

      setStats({
        totalUsers: allUsers.length || 0,
        todayActivity: todayLogs.length,
        openTickets: allTickets.filter(t => t.status === 'open').length,
        highRisk: allLogs.filter(l => l.status === 'late' || l.status === 'early_leave').length, // role-specific
        role, // expose for UI
      });

      setLogs(allLogs.slice(0, 8));
      setTickets(allTickets.slice(0, 4));

      // Chart: role-scope
      const days = [];
      for (let i = 6; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        const dayStr = d.toDateString();
        const count = allLogs.filter(l => new Date(l.check_in).toDateString() === dayStr).length;
        days.push({ name: d.toLocaleDateString('en', {weekday: 'short'}), uv: count });
      }
      setChartData(days);
    } catch (err) {
      console.error('RoleDashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, label, value, color, children }) => (
    <motion.div variants={itemVariants}>
      <Card className="h-full group">
        <CardContent className="p-6 pt-8 relative h-full">
          <div className={`absolute -top-4 left-4 p-3 rounded-2xl ${color} shadow-lg`}>
            <Icon className="h-5 w-5 text-white" />
          </div>
          <div className="space-y-2">
            <p className="text-3xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">{value}</p>
            <p className="text-sm font-medium text-slate-500">{label}</p>
            {children}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner size="xl" />
      </div>
    );
  }

  const isAdminOrHigher = ['admin', 'superadmin'].includes(role);
  const isManagerOrHigher = ['manager', 'admin', 'superadmin'].includes(role);

  return (
    <motion.div 
      className="space-y-8"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Header: Role-specific */}
      <motion.div variants={itemVariants} className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            {roleDisplay} Dashboard
          </h1>
          <p className="text-lg text-slate-500 mt-2">
            {role === 'employee' && 'Your personal metrics & actions'}
            {role === 'manager' && 'Team performance overview'}
            {role === 'admin' && 'Organization insights'}
            {role === 'superadmin' && 'Multi-tenant analytics'}
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <Button onClick={() => navigate('/dashboard/attendance')} size="lg" className="shadow-xl">
            <Camera className="mr-2 h-5 w-5" />
            {role === 'employee' ? 'My Check-in' : 'View Attendance'}
          </Button>
          {isManagerOrHigher && (
            <Button variant="outline" onClick={() => navigate('/dashboard/users')} size="lg">
              Manage Team
            </Button>
          )}
        </div>
      </motion.div>

      {/* Role-specific Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          icon={Users} 
          label="Team/Users" 
          value={stats.totalUsers}
          color="bg-gradient-to-r from-blue-500 to-indigo-600" 
        >
          {isAdminOrHigher && <Badge className="mt-1">Org-wide</Badge>}
        </StatCard>
        <StatCard 
          icon={Clock} 
          label="Today's Activity" 
          value={stats.todayActivity}
          color="bg-gradient-to-r from-emerald-500 to-teal-600"
        />
        <StatCard 
          icon={Ticket} 
          label="Open Tickets" 
          value={stats.openTickets}
          color="bg-gradient-to-r from-orange-500 to-red-500"
        />
        <StatCard 
          icon={AlertTriangle} 
          label="Alerts/Issues" 
          value={stats.highRisk || 0}
          color="bg-gradient-to-r from-amber-500 to-yellow-500"
        >
          {role === 'superadmin' && <Badge variant="destructive" className="mt-1">All orgs</Badge>}
        </StatCard>
      </div>

      {/* Charts & Quick Actions */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Activity Chart */}
        <motion.div variants={itemVariants} className="xl:col-span-2">
          <Card className="h-[400px]">
            <CardHeader>
              <CardTitle>Activity Trend ({roleDisplay} view)</CardTitle>
              <CardDescription>Recent check-ins filtered by your scope</CardDescription>
            </CardHeader>
            <CardContent className="h-[280px]">
              <ResponsiveContainer>
                <AreaChart data={chartData}>
                  <CartesianGrid vertical={false} strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="uv" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Role Quick Actions */}
        <motion.div variants={itemVariants}>
          <Card className="h-[400px] flex flex-col">
            <CardHeader>
              <CardTitle>Your Actions</CardTitle>
              <CardDescription>Fast access to role-specific tools</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 flex-1 pt-1">
              <Button className="w-full justify-between" onClick={() => navigate('/dashboard/ticketing')}>
                <span>IT Support Ticket</span>
                {stats.openTickets > 0 && <Badge>{stats.openTickets}</Badge>}
              </Button>
              <Button className="w-full justify-between" onClick={() => navigate('/dashboard/reimbursements')}>
                <span>{role === 'employee' ? 'Expense Report' : 'Review Expenses'}</span>
                <ArrowRight className="h-4 w-4" />
              </Button>
              {isManagerOrHigher && (
                <>
                  <Button className="w-full justify-between" onClick={() => navigate('/dashboard/reports')}>
                    <span>Team Reports</span>
                    <BarChart3 className="h-4 w-4" />
                  </Button>
                  <Button className="w-full justify-between" onClick={() => navigate('/dashboard/payroll')}>
                    <span>Payroll Review</span>
                    <Shield className="h-4 w-4" />
                  </Button>
                </>
              )}
              {role === 'superadmin' && (
                <Button className="w-full justify-between" onClick={() => navigate('/dashboard/users')}>
                  <span>Manage Orgs</span>
                  <Database className="h-4 w-4" />
                </Button>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Role-specific bottom section */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Recent Activity - Role scoped */}
        <Card>
          <CardHeader className="flex row items-center justify-between">
            <div>
              <CardTitle>{role === 'employee' ? 'My Recent Check-ins' : 'Team Activity'}</CardTitle>
              <CardDescription>Latest in your scope</CardDescription>
            </div>
            <Button variant="ghost" onClick={() => navigate('/dashboard/attendance')} size="sm">
              View Full Log
            </Button>
          </CardHeader>
          <CardContent>
            {logs.length ? (
              logs.map((log) => (
                <div key={log.id} className="flex items-center justify-between p-3 border-b border-slate-100 last:border-b-0 hover:bg-slate-50">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 bg-gradient-to-br from-indigo-500 rounded-full flex items-center justify-center text-white font-bold">
                      {log.user_name?.[0]?.toUpperCase() || 'U'}
                    </div>
                    <div>
                      <p className="font-semibold">{log.user_name || 'User'}</p>
                      <p className="text-sm text-slate-500">{new Date(log.check_in).toLocaleString()}</p>
                    </div>
                  </div>
                  <Badge variant={log.status === 'on_time' ? 'default' : 'secondary'}>
                    {log.status?.replace('_', ' ') || 'pending'}
                  </Badge>
                </div>
              ))
            ) : (
              <div className="text-center py-12 text-slate-400">
                <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No recent activity</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Tickets - Role scoped */}
        <Card>
          <CardHeader className="flex row items-center justify-between">
            <div>
              <CardTitle>Open Items</CardTitle>
              <CardDescription>{role === 'employee' ? 'Your tickets' : 'Team tickets'}</CardDescription>
            </div>
            <Button variant="ghost" onClick={() => navigate('/dashboard/ticketing')} size="sm">
              Manage Tickets
            </Button>
          </CardHeader>
          <CardContent>
            {tickets.length ? (
              tickets.map((ticket) => (
                <div key={ticket.id} className="flex items-center justify-between p-3 border-b border-slate-100 last:border-b-0 hover:bg-slate-50">
                  <div>
                    <p className="font-semibold text-sm">{ticket.title}</p>
                    <p className="text-xs text-slate-500">{ticket.created_at}</p>
                  </div>
                  <Badge variant="outline" className="capitalize">
                    {ticket.status}
                  </Badge>
                </div>
              ))
            ) : (
              <div className="text-center py-12 text-slate-400">
                <Ticket className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No open items</p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
};

export default RoleDashboard;


import React, { useState, useEffect } from 'react';
import { Download, Calendar, Users, Clock, AlertTriangle, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { attendanceService } from '../services/attendanceService';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Spinner } from '../components/ui/Spinner';
import { EmptyState } from '../components/ui/EmptyState';
import { formatDate, formatTime, titleCase } from '../lib/utils';

export default function Reports() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('7');

  useEffect(() => {
    fetchData();
  }, [dateRange]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await attendanceService.getLogs({ limit: 200 });
      setLogs(res.data || []);
    } finally {
      setLoading(false);
    }
  };

  const filteredLogs = logs.slice(0, parseInt(dateRange) * 10);

  const statusCounts = {
    on_time: filteredLogs.filter((l) => l.status === 'on_time').length,
    late: filteredLogs.filter((l) => l.status === 'late').length,
    early: filteredLogs.filter((l) => l.status === 'early').length,
  };

  const pieData = [
    { name: 'On Time', value: statusCounts.on_time, color: '#10b981' },
    { name: 'Late', value: statusCounts.late, color: '#f59e0b' },
    { name: 'Early', value: statusCounts.early, color: '#6366f1' },
  ].filter((d) => d.value > 0);

  const dailyData = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const dayStr = d.toDateString();
    const count = filteredLogs.filter((l) => new Date(l.check_in).toDateString() === dayStr).length;
    dailyData.push({
      day: d.toLocaleDateString('en', { weekday: 'short' }),
      checkins: count,
    });
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Reports</h1>
          <p className="text-sm text-gray-400 mt-1">Attendance analytics and insights</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </select>
          <Button variant="secondary">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-lg bg-indigo-500/10 flex items-center justify-center">
                <Users className="h-5 w-5 text-indigo-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{filteredLogs.length}</p>
                <p className="text-sm text-gray-400">Total check-ins</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                <Clock className="h-5 w-5 text-emerald-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{statusCounts.on_time}</p>
                <p className="text-sm text-gray-400">On time</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                <AlertTriangle className="h-5 w-5 text-amber-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{statusCounts.late + statusCounts.early}</p>
                <p className="text-sm text-gray-400">Late / Early</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Daily Check-ins</CardTitle>
            <CardDescription>Attendance volume over the past week</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderRadius: '8px',
                      border: '1px solid #334155',
                      color: '#e2e8f0',
                      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.3)',
                    }}
                  />
                  <Bar dataKey="checkins" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Status Breakdown</CardTitle>
            <CardDescription>Distribution of attendance statuses</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center">
              {pieData.length === 0 ? (
                <p className="text-sm text-gray-400">No data</p>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#0f172a',
                        borderRadius: '8px',
                        border: '1px solid #334155',
                        color: '#e2e8f0',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
            <div className="flex justify-center gap-4 mt-4">
              {pieData.map((d) => (
                <div key={d.name} className="flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full" style={{ backgroundColor: d.color }} />
                  <span className="text-sm text-gray-400">{d.name}: {d.value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Audit table */}
      <Card>
        <CardHeader>
          <CardTitle>Audit Log</CardTitle>
          <CardDescription>Detailed attendance records</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {filteredLogs.length === 0 ? (
            <EmptyState title="No records" description="No attendance data for the selected period." />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-gray-800 bg-gray-800/50">
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Employee</th>
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Date</th>
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Time</th>
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Status</th>
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Source</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {filteredLogs.slice(0, 20).map((log) => (
                    <tr key={log.id} className="hover:bg-gray-800/50 transition-colors">
                      <td className="px-6 py-3 text-sm text-white">{log.user_name || `User #${log.user_id}`}</td>
                      <td className="px-6 py-3 text-sm text-gray-400">{formatDate(log.check_in)}</td>
                      <td className="px-6 py-3 text-sm text-gray-400">{formatTime(log.check_in)}</td>
                      <td className="px-6 py-3">
                        <Badge
                          variant={
                            log.status === 'on_time'
                              ? 'success'
                              : log.status === 'late'
                              ? 'warning'
                              : 'default'
                          }
                        >
                          {titleCase(log.status)}
                        </Badge>
                      </td>
                      <td className="px-6 py-3 text-sm text-gray-400 capitalize">{log.source}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}


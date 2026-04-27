import React, { useState, useEffect } from 'react';
import { Download, RefreshCw, DollarSign, Calendar, CreditCard } from 'lucide-react';
import { payrollService } from '../services/payrollService';
import { useAuthStore } from '../store/authStore';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Spinner } from '../components/ui/Spinner';
import { EmptyState } from '../components/ui/EmptyState';
import { formatCurrency } from '../lib/utils';

export default function Payroll() {
  const [payrolls, setPayrolls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [year, setYear] = useState(new Date().getFullYear());
  const { user } = useAuthStore();
  const isAdmin = ['Admin', 'Manager'].includes(user?.role?.name);

  useEffect(() => {
    fetchPayroll();
  }, [month, year]);

  const fetchPayroll = async () => {
    setLoading(true);
    try {
      const res = await payrollService.getPayrolls(month, year);
      setPayrolls(res.data || []);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!isAdmin) return;
    setGenerating(true);
    try {
      await payrollService.generatePayroll(month, year);
      fetchPayroll();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to generate payroll');
    } finally {
      setGenerating(false);
    }
  };

  const total = payrolls.reduce((sum, p) => sum + (p.total_salary || 0), 0);
  const deductions = payrolls.reduce((sum, p) => sum + (p.deductions || 0), 0);
  const avg = payrolls.length ? total / payrolls.length : 0;

  const months = Array.from({ length: 12 }, (_, i) => ({
    value: i + 1,
    label: new Date(0, i).toLocaleString('en', { month: 'long' }),
  }));

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Payroll</h1>
          <p className="text-sm text-gray-400 mt-1">Salary computation and disbursement</p>
        </div>
        <div className="flex items-center gap-3">
          {isAdmin && (
            <Button onClick={handleGenerate} isLoading={generating}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Generate
            </Button>
          )}
          <div className="flex items-center gap-2 rounded-lg border border-gray-700 px-3 py-2 bg-gray-800">
            <Calendar className="h-4 w-4 text-gray-400" />
            <select
              value={month}
              onChange={(e) => setMonth(Number(e.target.value))}
              className="bg-transparent text-sm text-white outline-none"
            >
              {months.map((m) => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
          </div>
          <select
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            className="rounded-lg border border-gray-700 px-3 py-2.5 text-sm outline-none bg-gray-800 text-white"
          >
            {[2024, 2025, 2026, 2027].map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-lg bg-indigo-500/10 flex items-center justify-center">
                <DollarSign className="h-5 w-5 text-indigo-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{formatCurrency(total)}</p>
                <p className="text-sm text-gray-400">Total disbursement</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-lg bg-red-500/10 flex items-center justify-center">
                <DollarSign className="h-5 w-5 text-red-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{formatCurrency(deductions)}</p>
                <p className="text-sm text-gray-400">Total deductions</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                <DollarSign className="h-5 w-5 text-emerald-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{formatCurrency(avg)}</p>
                <p className="text-sm text-gray-400">Average salary</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Payroll list */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Spinner size="lg" />
        </div>
      ) : payrolls.length === 0 ? (
        <EmptyState
          icon={CreditCard}
          title="No payroll records"
          description="Generate payroll for the selected period."
          actionText="Generate now"
          onAction={handleGenerate}
        />
      ) : (
        <div className="space-y-4">
          {payrolls.map((p) => (
            <Card key={p.id}>
              <CardContent className="p-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <div className="h-12 w-12 rounded-full bg-indigo-500/10 flex items-center justify-center text-indigo-400 font-bold">
                      {(p.user?.full_name || '?')[0]}
                    </div>
                    <div>
                      <p className="text-base font-semibold text-white">{p.user?.full_name || `User #${p.user_id}`}</p>
                      <p className="text-xs text-gray-400">ID: VC-{p.id}</p>
                    </div>
                  </div>
                  <div className="text-left sm:text-right">
                    <p className="text-2xl font-bold text-white">{formatCurrency(p.total_salary)}</p>
                    <Badge
                      variant={
                        p.status === 'paid'
                          ? 'success'
                          : p.status === 'pending'
                          ? 'warning'
                          : 'default'
                      }
                    >
                      {p.status || 'Draft'}
                    </Badge>
                  </div>
                </div>
                <div className="mt-6 grid grid-cols-3 gap-4 pt-4 border-t border-gray-800">
                  <div>
                    <p className="text-xs text-gray-400">Base salary</p>
                    <p className="text-sm font-semibold text-white">{formatCurrency(p.base_salary)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Deductions</p>
                    <p className="text-sm font-semibold text-red-400">-{formatCurrency(p.deductions)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Reimbursements</p>
                    <p className="text-sm font-semibold text-emerald-400">+{formatCurrency(p.reimbursements_total)}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}


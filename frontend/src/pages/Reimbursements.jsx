import React, { useState, useEffect } from 'react';
import { Plus, Search, Receipt, DollarSign, CheckCircle2, XCircle, ExternalLink } from 'lucide-react';
import { reimbursementService } from '../services/reimbursementService';
import { useAuthStore } from '../store/authStore';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { Select } from '../components/ui/Select';
import { EmptyState } from '../components/ui/EmptyState';
import { Spinner } from '../components/ui/Spinner';
import { formatCurrency, formatDate, titleCase } from '../lib/utils';

export default function Reimbursements() {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const { user } = useAuthStore();
  const isAdmin = ['Admin', 'Manager'].includes(user?.role?.name);

  const [newClaim, setNewClaim] = useState({
    amount: '',
    reason: '',
    receipt_url: '',
    category: 'travel',
  });

  useEffect(() => {
    fetchClaims();
  }, [statusFilter]);

  const fetchClaims = async () => {
    setLoading(true);
    try {
      const params = statusFilter ? { status: statusFilter } : {};
      const res = await reimbursementService.getClaims(params);
      setClaims(res.data || []);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await reimbursementService.createClaim({
        ...newClaim,
        amount: parseFloat(newClaim.amount),
      });
      setShowCreate(false);
      setNewClaim({ amount: '', reason: '', receipt_url: '', category: 'travel' });
      fetchClaims();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit claim');
    }
  };

  const handleApprove = async (id) => {
    try {
      await reimbursementService.approveClaim(id, { status: 'approved' });
      fetchClaims();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to approve');
    }
  };

  const handleReject = async (id) => {
    try {
      await reimbursementService.approveClaim(id, { status: 'rejected' });
      fetchClaims();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to reject');
    }
  };

  const filtered = claims.filter(
    (c) =>
      (c.reason || '').toLowerCase().includes(search.toLowerCase()) ||
      (c.category || '').toLowerCase().includes(search.toLowerCase())
  );

  const statusBadge = (status) => {
    const map = {
      pending: 'warning',
      approved: 'success',
      rejected: 'danger',
      paid: 'primary',
    };
    return map[status] || 'default';
  };

  const activeTotal = claims
    .filter((c) => c.status === 'approved' || c.status === 'paid')
    .reduce((sum, c) => sum + (c.amount || 0), 0);

  const stats = {
    active: claims.filter((c) => c.status === 'pending').length,
    approved: activeTotal,
    processed: claims.filter((c) => c.status !== 'pending').length,
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Reimbursements</h1>
          <p className="text-sm text-gray-400 mt-1">Expense claims and approvals</p>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Submit claim
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                <Receipt className="h-5 w-5 text-amber-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{stats.active}</p>
                <p className="text-sm text-gray-400">Pending</p>
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
                <p className="text-2xl font-bold text-white">{formatCurrency(stats.approved)}</p>
                <p className="text-sm text-gray-400">Approved</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-lg bg-indigo-500/10 flex items-center justify-center">
                <CheckCircle2 className="h-5 w-5 text-indigo-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{stats.processed}</p>
                <p className="text-sm text-gray-400">Processed</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
          <input
            type="text"
            placeholder="Search claims..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-700 bg-gray-800 text-white text-sm placeholder-gray-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all duration-200"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2.5 text-sm text-white outline-none"
        >
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="paid">Paid</option>
        </select>
      </div>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Spinner size="lg" />
            </div>
          ) : filtered.length === 0 ? (
            <EmptyState
              icon={Receipt}
              title="No claims found"
              description="Submit your first expense claim."
              actionText="Submit claim"
              onAction={() => setShowCreate(true)}
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-gray-800 bg-gray-800/50">
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">ID</th>
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Reason</th>
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Category</th>
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Amount</th>
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Status</th>
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Date</th>
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {filtered.map((claim) => (
                    <tr key={claim.id} className="hover:bg-gray-800/50 transition-colors">
                      <td className="px-6 py-4 text-sm font-mono text-gray-400">#{claim.id}</td>
                      <td className="px-6 py-4 text-sm font-medium text-white">{claim.reason}</td>
                      <td className="px-6 py-4 text-xs text-gray-400 uppercase">{claim.category}</td>
                      <td className="px-6 py-4 text-sm font-semibold text-white">{formatCurrency(claim.amount)}</td>
                      <td className="px-6 py-4">
                        <Badge variant={statusBadge(claim.status)}>{titleCase(claim.status)}</Badge>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-400">
                        {claim.submitted_at ? formatDate(claim.submitted_at) : 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          {claim.receipt_url && (
                            <a
                              href={claim.receipt_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="p-1.5 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition-colors duration-200"
                            >
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          )}
                          {isAdmin && claim.status === 'pending' && (
                            <>
                              <button
                                onClick={() => handleApprove(claim.id)}
                                className="p-1.5 rounded-lg hover:bg-emerald-500/10 text-gray-400 hover:text-emerald-400 transition-colors duration-200"
                                title="Approve"
                              >
                                <CheckCircle2 className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => handleReject(claim.id)}
                                className="p-1.5 rounded-lg hover:bg-red-500/10 text-gray-400 hover:text-red-400 transition-colors duration-200"
                                title="Reject"
                              >
                                <XCircle className="h-4 w-4" />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create modal */}
      <Modal
        isOpen={showCreate}
        onClose={() => setShowCreate(false)}
        title="Submit expense claim"
        description="Attach receipts for reimbursement."
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <Input
            label="Reason for expense"
            value={newClaim.reason}
            onChange={(e) => setNewClaim({ ...newClaim, reason: e.target.value })}
            placeholder="e.g., Client lunch"
            required
          />
          <Select
            label="Category"
            value={newClaim.category}
            onChange={(e) => setNewClaim({ ...newClaim, category: e.target.value })}
            options={[
              { value: 'travel', label: 'Travel' },
              { value: 'meals', label: 'Meals' },
              { value: 'supplies', label: 'Supplies' },
              { value: 'other', label: 'Other' },
            ]}
          />
          <Input
            label="Amount (USD)"
            type="number"
            step="0.01"
            value={newClaim.amount}
            onChange={(e) => setNewClaim({ ...newClaim, amount: e.target.value })}
            placeholder="0.00"
            required
          />
          <Input
            label="Receipt URL (optional)"
            value={newClaim.receipt_url}
            onChange={(e) => setNewClaim({ ...newClaim, receipt_url: e.target.value })}
            placeholder="https://..."
          />
          <div className="flex gap-3 pt-2">
            <Button type="button" variant="secondary" className="flex-1" onClick={() => setShowCreate(false)}>
              Cancel
            </Button>
            <Button type="submit" className="flex-1">
              Submit claim
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}


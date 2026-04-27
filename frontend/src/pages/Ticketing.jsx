import React, { useState, useEffect } from 'react';
import { Plus, Search, MessageSquare, Filter } from 'lucide-react';
import { ticketService } from '../services/ticketService';
import { useAuthStore } from '../store/authStore';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { Select } from '../components/ui/Select';
import { EmptyState } from '../components/ui/EmptyState';
import { Spinner } from '../components/ui/Spinner';
import { formatDate, titleCase } from '../lib/utils';

export default function Ticketing() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const { user } = useAuthStore();
  const isAdmin = ['Admin', 'Manager'].includes(user?.role?.name);

  const [newTicket, setNewTicket] = useState({
    title: '',
    description: '',
    priority: 'medium',
  });

  useEffect(() => {
    fetchTickets();
  }, [statusFilter]);

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const params = statusFilter ? { status: statusFilter } : {};
      const res = await ticketService.getTickets(params);
      setTickets(res.data || []);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await ticketService.createTicket(newTicket);
      setShowCreate(false);
      setNewTicket({ title: '', description: '', priority: 'medium' });
      fetchTickets();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create ticket');
    }
  };

  const handleStatusChange = async (id, status) => {
    try {
      await ticketService.updateTicket(id, { status });
      fetchTickets();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update');
    }
  };

  const filtered = tickets.filter(
    (t) =>
      (t.title || '').toLowerCase().includes(search.toLowerCase()) ||
      (t.description || '').toLowerCase().includes(search.toLowerCase())
  );

  const statusBadge = (status) => {
    const map = {
      open: 'primary',
      resolved: 'success',
      escalated: 'danger',
      closed: 'default',
    };
    return map[status] || 'default';
  };

  const priorityBadge = (priority) => {
    const map = {
      critical: 'danger',
      high: 'warning',
      medium: 'primary',
      low: 'success',
    };
    return map[priority] || 'default';
  };

  const stats = {
    total: tickets.length,
    open: tickets.filter((t) => t.status === 'open').length,
    resolved: tickets.filter((t) => t.status === 'resolved').length,
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Support Tickets</h1>
          <p className="text-sm text-gray-400 mt-1">Manage issues and track resolution</p>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New ticket
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <p className="text-2xl font-bold text-white">{stats.total}</p>
            <p className="text-sm text-gray-400">Total tickets</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <p className="text-2xl font-bold text-indigo-400">{stats.open}</p>
            <p className="text-sm text-gray-400">Open</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <p className="text-2xl font-bold text-emerald-400">{stats.resolved}</p>
            <p className="text-sm text-gray-400">Resolved</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
          <input
            type="text"
            placeholder="Search tickets..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-700 bg-gray-800 text-white text-sm placeholder-gray-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all duration-200"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2.5 text-sm text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"
        >
          <option value="">All statuses</option>
          <option value="open">Open</option>
          <option value="resolved">Resolved</option>
          <option value="escalated">Escalated</option>
          <option value="closed">Closed</option>
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
              icon={MessageSquare}
              title="No tickets found"
              description="Create your first support ticket to get started."
              actionText="New ticket"
              onAction={() => setShowCreate(true)}
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-gray-800 bg-gray-800/50">
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">ID</th>
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Issue</th>
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Priority</th>
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Status</th>
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Created</th>
                    <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {filtered.map((ticket) => (
                    <tr key={ticket.id} className="hover:bg-gray-800/50 transition-colors">
                      <td className="px-6 py-4 text-sm font-mono text-gray-400">#{ticket.id}</td>
                      <td className="px-6 py-4">
                        <p className="text-sm font-medium text-white">{ticket.title}</p>
                        <p className="text-xs text-gray-400 truncate max-w-xs">{ticket.description}</p>
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant={priorityBadge(ticket.priority)}>{titleCase(ticket.priority)}</Badge>
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant={statusBadge(ticket.status)}>{titleCase(ticket.status)}</Badge>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-400">
                        {ticket.created_at ? formatDate(ticket.created_at) : 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        {isAdmin ? (
                          <select
                            value={ticket.status}
                            onChange={(e) => handleStatusChange(ticket.id, e.target.value)}
                            className="rounded-lg border border-gray-700 bg-gray-800 px-2 py-1 text-xs text-white focus:border-indigo-500 outline-none"
                          >
                            <option value="open">Open</option>
                            <option value="resolved">Resolved</option>
                            <option value="escalated">Escalated</option>
                            <option value="closed">Closed</option>
                          </select>
                        ) : (
                          <span className="text-xs text-gray-500">—</span>
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

      {/* Create modal */}
      <Modal
        isOpen={showCreate}
        onClose={() => setShowCreate(false)}
        title="New Support Ticket"
        description="Describe your issue and we'll help resolve it."
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <Input
            label="Title"
            value={newTicket.title}
            onChange={(e) => setNewTicket({ ...newTicket, title: e.target.value })}
            placeholder="Brief summary of the issue"
            required
          />
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-300">Description</label>
            <textarea
              value={newTicket.description}
              onChange={(e) => setNewTicket({ ...newTicket, description: e.target.value })}
              rows={4}
              placeholder="Provide as much detail as possible..."
              required
              className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2.5 text-sm text-white placeholder-gray-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none resize-none transition-all duration-200"
            />
          </div>
          <Select
            label="Priority"
            value={newTicket.priority}
            onChange={(e) => setNewTicket({ ...newTicket, priority: e.target.value })}
            options={[
              { value: 'low', label: 'Low' },
              { value: 'medium', label: 'Medium' },
              { value: 'high', label: 'High' },
              { value: 'critical', label: 'Critical' },
            ]}
          />
          <div className="flex gap-3 pt-2">
            <Button type="button" variant="secondary" className="flex-1" onClick={() => setShowCreate(false)}>
              Cancel
            </Button>
            <Button type="submit" className="flex-1">
              Submit ticket
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}


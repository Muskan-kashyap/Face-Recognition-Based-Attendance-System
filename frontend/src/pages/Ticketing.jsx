import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    Ticket, 
    Plus, 
    Clock, 
    AlertTriangle, 
    CheckCircle2, 
    Search, 
    Filter,
    MessageSquare,
    ChevronRight,
    ArrowUpRight
} from 'lucide-react';
import axios from 'axios';

const Ticketing = () => {
    const [tickets, setTickets] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [newTicket, setNewTicket] = useState({ title: '', description: '', priority: 'medium' });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchTickets();
    }, []);

    const fetchTickets = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:8000/api/v1/ticketing/');
            setTickets(response.data);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const handleCreateTicket = async (e) => {
        e.preventDefault();
        try {
            await axios.post('http://127.0.0.1:8000/api/v1/ticketing/', newTicket);
            setIsModalOpen(false);
            setNewTicket({ title: '', description: '', priority: 'medium' });
            fetchTickets();
        } catch (err) {
            console.error(err);
        }
    };

    const getStatusStyle = (status) => {
        switch (status) {
            case 'open': return 'bg-primary/10 text-primary border-primary/20';
            case 'resolved': return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
            case 'escalated': return 'bg-accent/10 text-accent border-accent/20';
            case 'closed': return 'bg-white/5 text-text-dim border-white/10';
            default: return 'bg-white/5 text-white border-white/10';
        }
    };

    const getPriorityStyle = (priority) => {
        switch (priority) {
            case 'critical': return 'text-accent';
            case 'high': return 'text-orange-500';
            case 'medium': return 'text-primary';
            case 'low': return 'text-emerald-500';
            default: return 'text-white';
        }
    };

    return (
        <div className="max-w-7xl mx-auto py-10 px-6">
            <header className="flex justify-between items-center mb-12">
                <div>
                    <h2 className="text-4xl font-bold tracking-tight text-white mb-2">Support & Issue Resolution</h2>
                    <p className="text-text-muted font-medium">Track attendance discrepancies and system inquiries.</p>
                </div>
                <button 
                    onClick={() => setIsModalOpen(true)}
                    className="btn-premium btn-primary flex items-center gap-2 px-6 py-3 rounded-xl shadow-lg shadow-primary-glow/20"
                >
                    <Plus size={20} /> Open New Ticket
                </button>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
                <StatCard icon={Ticket} label="Total Tickets" value={tickets.length} color="primary" />
                <StatCard icon={Clock} label="Open Tickets" value={tickets.filter(t => t.status === 'open').length} color="primary" />
                <StatCard icon={AlertTriangle} label="Escalated" value={tickets.filter(t => t.status === 'escalated').length} color="accent" />
                <StatCard icon={CheckCircle2} label="Resolved" value={tickets.filter(t => t.status === 'resolved').length} color="emerald-500" />
            </div>

            <div className="glass-card border-white/5 overflow-hidden">
                <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
                    <div className="flex items-center gap-4 bg-bg-deep/50 border border-white/5 rounded-xl px-4 py-2 w-96 focus-within:border-primary/40 transition-all">
                        <Search size={18} className="text-text-dim" />
                        <input type="text" placeholder="Search tickets..." className="bg-transparent border-none text-sm text-white focus:outline-none w-full" />
                    </div>
                    <div className="flex items-center gap-2">
                        <button className="p-2 glass-panel border-white/5 text-text-muted hover:text-white transition-colors">
                            <Filter size={20} />
                        </button>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="text-[10px] font-black uppercase tracking-[0.2em] text-text-dim bg-white/[0.01]">
                                <th className="px-8 py-5">Ticket ID</th>
                                <th className="px-8 py-5">Issue Title</th>
                                <th className="px-8 py-5">Priority</th>
                                <th className="px-8 py-5">Status</th>
                                <th className="px-8 py-5">Created</th>
                                <th className="px-8 py-5 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {tickets.map((ticket) => (
                                <tr key={ticket.id} className="group hover:bg-white/[0.02] transition-all">
                                    <td className="px-8 py-6">
                                        <span className="text-xs font-mono font-bold text-text-dim group-hover:text-primary transition-colors">#{ticket.id}</span>
                                    </td>
                                    <td className="px-8 py-6">
                                        <div>
                                            <p className="text-sm font-bold text-white group-hover:text-primary transition-colors">{ticket.title}</p>
                                            <p className="text-[10px] text-text-dim mt-1 truncate max-w-xs">{ticket.description}</p>
                                        </div>
                                    </td>
                                    <td className="px-8 py-6">
                                        <span className={`text-[10px] font-black uppercase tracking-widest ${getPriorityStyle(ticket.priority)}`}>
                                            {ticket.priority}
                                        </span>
                                    </td>
                                    <td className="px-8 py-6">
                                        <span className={`px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border ${getStatusStyle(ticket.status)}`}>
                                            {ticket.status}
                                        </span>
                                    </td>
                                    <td className="px-8 py-6 text-xs text-text-dim font-medium">
                                        {new Date(ticket.created_at).toLocaleDateString()}
                                    </td>
                                    <td className="px-8 py-6 text-right">
                                        <button className="p-2 glass-panel border-white/5 text-text-muted hover:text-primary hover:border-primary/20 transition-all">
                                            <ChevronRight size={18} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {tickets.length === 0 && !loading && (
                                <tr>
                                    <td colSpan="6" className="px-8 py-20 text-center">
                                        <div className="flex flex-col items-center gap-4 text-text-dim">
                                            <MessageSquare size={48} className="opacity-20" />
                                            <p className="text-sm font-medium">No tickets found. You're all clear!</p>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Create Ticket Modal */}
            <AnimatePresence>
                {isModalOpen && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-bg-deep/80 backdrop-blur-sm">
                        <motion.div 
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className="glass-card w-full max-w-xl border-white/10 shadow-2xl p-10 relative overflow-hidden"
                        >
                            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 blur-3xl -z-10" />
                            
                            <h3 className="text-2xl font-bold text-white mb-2">New Support Ticket</h3>
                            <p className="text-text-muted text-sm mb-8">Describe the issue and our team will resolve it within 48 hours.</p>

                            <form onSubmit={handleCreateTicket} className="space-y-6">
                                <div>
                                    <label className="block text-[10px] font-black text-text-dim uppercase tracking-[0.2em] mb-2">Issue Summary</label>
                                    <input 
                                        type="text" 
                                        required
                                        className="w-full bg-bg-deep/50 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-primary/40 transition-all"
                                        value={newTicket.title}
                                        onChange={(e) => setNewTicket({...newTicket, title: e.target.value})}
                                        placeholder="e.g., Face not recognized at Terminal A"
                                    />
                                </div>
                                <div>
                                    <label className="block text-[10px] font-black text-text-dim uppercase tracking-[0.2em] mb-2">Detailed Description</label>
                                    <textarea 
                                        required
                                        rows="4"
                                        className="w-full bg-bg-deep/50 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-primary/40 transition-all resize-none"
                                        value={newTicket.description}
                                        onChange={(e) => setNewTicket({...newTicket, description: e.target.value})}
                                        placeholder="Please provide as much detail as possible..."
                                    />
                                </div>
                                <div>
                                    <label className="block text-[10px] font-black text-text-dim uppercase tracking-[0.2em] mb-2">Priority Level</label>
                                    <div className="flex gap-4">
                                        {['low', 'medium', 'high', 'critical'].map((p) => (
                                            <button
                                                key={p}
                                                type="button"
                                                onClick={() => setNewTicket({...newTicket, priority: p})}
                                                className={`flex-1 py-2 rounded-lg text-[10px] font-black uppercase tracking-widest border transition-all ${newTicket.priority === p ? 'bg-primary/20 border-primary/40 text-primary' : 'bg-white/5 border-white/5 text-text-dim hover:bg-white/10'}`}
                                            >
                                                {p}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="flex gap-4 pt-4">
                                    <button 
                                        type="button"
                                        onClick={() => setIsModalOpen(false)}
                                        className="flex-1 px-6 py-4 rounded-xl border border-white/10 text-white text-xs font-bold uppercase tracking-widest hover:bg-white/5 transition-all"
                                    >
                                        Cancel
                                    </button>
                                    <button 
                                        type="submit"
                                        className="flex-1 btn-premium btn-primary px-6 py-4 rounded-xl shadow-lg shadow-primary-glow/20"
                                    >
                                        Submit Ticket
                                    </button>
                                </div>
                            </form>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
};

const StatCard = ({ icon: Icon, label, value, color }) => (
    <div className="glass-card p-6 border-white/5 group hover:border-primary/20 transition-all duration-500">
        <div className="flex justify-between items-start mb-4">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center bg-${color}/10 border border-${color}/20 text-${color}`}>
                <Icon size={20} />
            </div>
            <div className="text-[10px] font-black text-emerald-500 flex items-center gap-1">
                <ArrowUpRight size={12} /> 12%
            </div>
        </div>
        <p className="text-[10px] font-bold text-text-dim uppercase tracking-widest mb-1">{label}</p>
        <p className="text-3xl font-bold text-white tracking-tight">{value}</p>
    </div>
);

export default Ticketing;

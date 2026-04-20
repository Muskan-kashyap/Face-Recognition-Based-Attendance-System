import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    Receipt, 
    Plus, 
    Clock, 
    CheckCircle2, 
    XCircle,
    DollarSign,
    ExternalLink,
    Search,
    ChevronRight,
    Wallet
} from 'lucide-react';
import axios from 'axios';

const Reimbursements = () => {
    const [claims, setClaims] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [newClaim, setNewClaim] = useState({ amount: '', reason: '', receipt_url: '' });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchClaims();
    }, []);

    const fetchClaims = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:8000/api/v1/reimbursement/');
            setClaims(response.data);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const handleCreateClaim = async (e) => {
        e.preventDefault();
        try {
            await axios.post('http://127.0.0.1:8000/api/v1/reimbursement/', newClaim);
            setIsModalOpen(false);
            setNewClaim({ amount: '', reason: '', receipt_url: '' });
            fetchClaims();
        } catch (err) {
            console.error(err);
        }
    };

    const getStatusStyle = (status) => {
        switch (status) {
            case 'pending': return 'bg-primary/10 text-primary border-primary/20';
            case 'approved': return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
            case 'rejected': return 'bg-accent/10 text-accent border-accent/20';
            case 'paid': return 'bg-white/5 text-text-dim border-white/10';
            default: return 'bg-white/5 text-white border-white/10';
        }
    };

    return (
        <div className="max-w-7xl mx-auto py-10 px-6">
            <header className="flex justify-between items-center mb-12">
                <div>
                    <h2 className="text-4xl font-bold tracking-tight text-white mb-2">Reimbursement Hub</h2>
                    <p className="text-text-muted font-medium">Manage expense claims and travel payouts.</p>
                </div>
                <button 
                    onClick={() => setIsModalOpen(true)}
                    className="btn-premium btn-primary flex items-center gap-2 px-6 py-3 rounded-xl shadow-lg shadow-primary-glow/20"
                >
                    <Plus size={20} /> Submit New Claim
                </button>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                <StatCard icon={Receipt} label="Active Claims" value={claims.filter(c => c.status === 'pending').length} />
                <StatCard icon={Wallet} label="Total Reimbursed" value={`$${claims.filter(c => c.status === 'approved' || c.status === 'paid').reduce((acc, curr) => acc + curr.amount, 0).toLocaleString()}`} />
                <StatCard icon={CheckCircle2} label="Processed" value={claims.filter(c => c.status !== 'pending').length} />
            </div>

            <div className="glass-card border-white/5 overflow-hidden">
                <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
                    <div className="flex items-center gap-4 bg-bg-deep/50 border border-white/5 rounded-xl px-4 py-2 w-96">
                        <Search size={18} className="text-text-dim" />
                        <input type="text" placeholder="Search claims..." className="bg-transparent border-none text-sm text-white focus:outline-none w-full" />
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="text-[10px] font-black uppercase tracking-[0.2em] text-text-dim bg-white/[0.01]">
                                <th className="px-8 py-5">Claim ID</th>
                                <th className="px-8 py-5">Reason</th>
                                <th className="px-8 py-5">Amount</th>
                                <th className="px-8 py-5">Status</th>
                                <th className="px-8 py-5">Submitted</th>
                                <th className="px-8 py-5 text-right">Receipt</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {claims.map((claim) => (
                                <tr key={claim.id} className="group hover:bg-white/[0.02] transition-all">
                                    <td className="px-8 py-6 text-xs font-mono font-bold text-text-dim group-hover:text-primary transition-colors">#{claim.id}</td>
                                    <td className="px-8 py-6">
                                        <p className="text-sm font-bold text-white group-hover:text-primary transition-colors">{claim.reason}</p>
                                    </td>
                                    <td className="px-8 py-6">
                                        <p className="text-sm font-bold text-white font-mono">${claim.amount.toLocaleString()}</p>
                                    </td>
                                    <td className="px-8 py-6">
                                        <span className={`px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border ${getStatusStyle(claim.status)}`}>
                                            {claim.status}
                                        </span>
                                    </td>
                                    <td className="px-8 py-6 text-xs text-text-dim font-medium">
                                        {new Date(claim.submitted_at).toLocaleDateString()}
                                    </td>
                                    <td className="px-8 py-6 text-right">
                                        <button className="p-2 glass-panel border-white/5 text-text-muted hover:text-primary hover:border-primary/20 transition-all">
                                            <ExternalLink size={16} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Create Claim Modal */}
            <AnimatePresence>
                {isModalOpen && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-bg-deep/80 backdrop-blur-sm">
                        <motion.div 
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="glass-card w-full max-w-lg border-white/10 shadow-2xl p-10"
                        >
                            <h3 className="text-2xl font-bold text-white mb-2 text-center">Submit Claim</h3>
                            <p className="text-text-muted text-sm mb-8 text-center">Attach your receipts for verification.</p>

                            <form onSubmit={handleCreateClaim} className="space-y-6">
                                <div>
                                    <label className="block text-[10px] font-black text-text-dim uppercase tracking-[0.2em] mb-2">Reason for Expense</label>
                                    <input 
                                        type="text" 
                                        required
                                        className="w-full bg-bg-deep/50 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-primary/40"
                                        value={newClaim.reason}
                                        onChange={(e) => setNewClaim({...newClaim, reason: e.target.value})}
                                        placeholder="e.g., Client Lunch, Flight to NYC"
                                    />
                                </div>
                                <div>
                                    <label className="block text-[10px] font-black text-text-dim uppercase tracking-[0.2em] mb-2">Amount (USD)</label>
                                    <div className="relative">
                                        <DollarSign size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-text-dim" />
                                        <input 
                                            type="number" 
                                            required
                                            className="w-full bg-bg-deep/50 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-white focus:outline-none focus:border-primary/40 font-mono"
                                            value={newClaim.amount}
                                            onChange={(e) => setNewClaim({...newClaim, amount: e.target.value})}
                                            placeholder="0.00"
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-[10px] font-black text-text-dim uppercase tracking-[0.2em] mb-2">Receipt Image URL</label>
                                    <input 
                                        type="text" 
                                        className="w-full bg-bg-deep/50 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-primary/40"
                                        value={newClaim.receipt_url}
                                        onChange={(e) => setNewClaim({...newClaim, receipt_url: e.target.value})}
                                        placeholder="https://..."
                                    />
                                </div>

                                <div className="flex gap-4 pt-4">
                                    <button 
                                        type="button"
                                        onClick={() => setIsModalOpen(false)}
                                        className="flex-1 px-6 py-4 rounded-xl border border-white/10 text-white text-xs font-bold uppercase tracking-widest"
                                    >
                                        Cancel
                                    </button>
                                    <button 
                                        type="submit"
                                        className="flex-1 btn-premium btn-primary px-6 py-4 rounded-xl shadow-lg shadow-primary-glow/20"
                                    >
                                        Submit Claim
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

const StatCard = ({ icon: Icon, label, value }) => (
    <div className="glass-card p-8 border-white/5 flex items-center gap-6">
        <div className="w-14 h-14 rounded-2xl flex items-center justify-center bg-primary/10 border border-primary/20 text-primary">
            <Icon size={28} />
        </div>
        <div>
            <p className="text-[10px] font-bold text-text-dim uppercase tracking-widest mb-1">{label}</p>
            <p className="text-2xl font-bold text-white tracking-tight">{value}</p>
        </div>
    </div>
);

export default Reimbursements;

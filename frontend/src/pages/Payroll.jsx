import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
    CreditCard, 
    Download, 
    TrendingUp, 
    Calendar,
    ChevronDown,
    DollarSign,
    MinusCircle,
    PlusCircle,
    Info,
    RefreshCw
} from 'lucide-react';
import axios from 'axios';

const Payroll = () => {
    const [payrolls, setPayrolls] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
    const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

    useEffect(() => {
        fetchPayroll();
    }, [selectedMonth, selectedYear]);

    const fetchPayroll = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`http://127.0.0.1:8000/api/v1/payroll/?month=${selectedMonth}&year=${selectedYear}`);
            setPayrolls(response.data);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const handleGenerate = async () => {
        try {
            await axios.post(`http://127.0.0.1:8000/api/v1/payroll/generate?month=${selectedMonth}&year=${selectedYear}`);
            fetchPayroll();
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="max-w-7xl mx-auto py-10 px-6">
            <header className="flex justify-between items-end mb-12">
                <div>
                    <h2 className="text-4xl font-bold tracking-tight text-white mb-2">Payroll Intelligence</h2>
                    <p className="text-text-muted font-medium">Automated salary computation and disbursement.</p>
                </div>
                <div className="flex gap-4">
                    <button 
                        onClick={handleGenerate}
                        className="btn-premium btn-primary flex items-center gap-2 px-6 py-3 rounded-xl shadow-lg shadow-primary-glow/20"
                    >
                        <RefreshCw size={18} className={loading ? 'animate-spin' : ''} /> Generate Current
                    </button>
                    <div className="flex items-center gap-2 glass-panel border-white/5 px-4 py-2 rounded-xl">
                        <Calendar size={18} className="text-primary" />
                        <select 
                            value={selectedMonth} 
                            onChange={(e) => setSelectedMonth(e.target.value)}
                            className="bg-transparent border-none text-white text-sm font-bold focus:outline-none cursor-pointer"
                        >
                            {[...Array(12)].map((_, i) => (
                                <option key={i+1} value={i+1}>{new Date(0, i).toLocaleString('en', { month: 'long' })}</option>
                            ))}
                        </select>
                    </div>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Main List */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    {payrolls.map((payroll, idx) => (
                        <motion.div 
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            key={payroll.id} 
                            className="glass-card border-white/5 p-8 group hover:border-primary/20 transition-all duration-500 overflow-hidden relative"
                        >
                            <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-primary/5 to-transparent pointer-events-none" />
                            
                            <div className="flex justify-between items-start relative z-10">
                                <div className="flex items-center gap-6">
                                    <div className="w-16 h-16 rounded-2xl bg-bg-deep/50 border border-white/10 flex items-center justify-center text-primary shadow-inner">
                                        <DollarSign size={32} />
                                    </div>
                                    <div>
                                        <p className="text-[10px] font-black text-text-dim uppercase tracking-[0.3em] mb-1">Employee Reference</p>
                                        <h4 className="text-xl font-bold text-white mb-1 tracking-tight">System User #{payroll.user_id}</h4>
                                        <div className="flex items-center gap-3">
                                            <span className={`px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest border ${payroll.status === 'paid' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' : 'bg-primary/10 text-primary border-primary/20'}`}>
                                                {payroll.status}
                                            </span>
                                            <span className="text-[10px] text-text-dim font-bold font-mono">ID: VC-PR-{payroll.id}</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="text-[10px] font-black text-text-dim uppercase tracking-[0.3em] mb-1">Net Salary</p>
                                    <p className="text-4xl font-bold text-white tracking-tighter">${payroll.total_salary.toLocaleString()}</p>
                                </div>
                            </div>

                            <div className="mt-10 grid grid-cols-3 gap-6 pt-8 border-t border-white/5">
                                <BreakdownItem label="Base Pay" value={payroll.base_salary} icon={PlusCircle} color="text-white" />
                                <BreakdownItem label="Deductions" value={payroll.deductions} icon={MinusCircle} color="text-accent" isNegative />
                                <BreakdownItem label="Reimbursements" value={payroll.reimbursements_total} icon={PlusCircle} color="text-emerald-500" />
                            </div>

                            <div className="mt-8 flex justify-end gap-3">
                                <button className="px-4 py-2 glass-panel border-white/5 text-[10px] font-bold uppercase tracking-widest text-text-muted hover:text-white transition-all flex items-center gap-2">
                                    <Info size={14} /> Details
                                </button>
                                <button className="px-4 py-2 glass-panel border-white/5 text-[10px] font-bold uppercase tracking-widest text-text-muted hover:text-primary hover:border-primary/20 transition-all flex items-center gap-2">
                                    <Download size={14} /> PDF
                                </button>
                            </div>
                        </motion.div>
                    ))}
                    {payrolls.length === 0 && !loading && (
                        <div className="glass-card py-24 text-center border-white/5">
                             <CreditCard size={64} className="mx-auto text-text-dim opacity-10 mb-6" />
                             <p className="text-text-muted font-medium">No payroll records found for this period.</p>
                        </div>
                    )}
                </div>

                {/* Insights Sidebar */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="glass-card p-8 border-white/5">
                        <h4 className="text-[10px] font-black text-text-dim uppercase tracking-[0.3em] mb-10 border-b border-white/5 pb-4">Budget Intelligence</h4>
                        
                        <div className="space-y-8">
                            <InsightItem label="Total Disbursement" value={`$${payrolls.reduce((acc, curr) => acc + curr.total_salary, 0).toLocaleString()}`} trend="+4.2%" />
                            <InsightItem label="Average Salary" value={`$${payrolls.length ? (payrolls.reduce((acc, curr) => acc + curr.total_salary, 0) / payrolls.length).toFixed(0).toLocaleString() : 0}`} />
                            <InsightItem label="Total Deductions" value={`$${payrolls.reduce((acc, curr) => acc + curr.deductions, 0).toLocaleString()}`} />
                        </div>

                        <div className="mt-12 p-6 glass-panel border-emerald-500/20 bg-emerald-500/5">
                             <div className="flex gap-4">
                                <TrendingUp className="text-emerald-500 flex-shrink-0" size={20} />
                                <div>
                                    <p className="text-xs font-bold mb-1 uppercase tracking-tight text-emerald-500">Efficiency Boost</p>
                                    <p className="text-[10px] text-emerald-500/80 leading-relaxed font-medium">
                                        Automated deductions saved 42 hours of manual HR processing this month.
                                    </p>
                                </div>
                             </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const BreakdownItem = ({ label, value, icon: Icon, color, isNegative }) => (
    <div>
        <div className="flex items-center gap-2 mb-1">
            <Icon size={12} className={color} />
            <p className="text-[10px] font-bold text-text-dim uppercase tracking-widest">{label}</p>
        </div>
        <p className={`text-lg font-bold font-mono ${color}`}>{isNegative ? '-' : ''}${value.toLocaleString()}</p>
    </div>
);

const InsightItem = ({ label, value, trend }) => (
    <div className="flex justify-between items-end">
        <div>
            <p className="text-[10px] font-bold text-text-dim uppercase tracking-widest mb-1">{label}</p>
            <p className="text-2xl font-bold text-white tracking-tight">{value}</p>
        </div>
        {trend && <span className="text-[9px] font-black text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full uppercase">{trend}</span>}
    </div>
);

export default Payroll;

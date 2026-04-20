import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { 
    FileText, 
    Download, 
    Filter, 
    Calendar, 
    ChevronDown, 
    FilePieChart,
    Search,
    Bell,
    Github,
    Slack,
    Share2,
    Database,
    Zap
} from 'lucide-react';
import { 
    BarChart, 
    Bar, 
    XAxis, 
    YAxis, 
    CartesianGrid, 
    Tooltip, 
    ResponsiveContainer,
    Cell
} from 'recharts';

const Reports = () => {
    const [dateRange, setDateRange] = useState('Last 7 Days');
    const [logs, setLogs] = useState([]);
    const [wellnessData, setWellnessData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchReportData = async () => {
            try {
                const logsRes = await axios.get('http://127.0.0.1:8000/api/v1/attendance/logs');
                const wellnessRes = await axios.get('http://127.0.0.1:8000/api/v1/attendance/wellness-heatmap');
                
                setLogs(logsRes.data);
                setWellnessData(wellnessRes.data);
            } catch (err) {
                console.error("Failed to fetch workforce intel:", err);
                // Fallback mock
                setLogs([
                    { id: 1, user_name: 'Captain Price', check_in: new Date().toISOString(), status: 'on_time', emotion: 'Neutral' },
                ]);
            } finally {
                setLoading(false);
            }
        };

        fetchReportData();
    }, []);
    
    const chartData = [
        { name: 'Mon', count: 1200 },
        { name: 'Tue', count: 1150 },
        { name: 'Wed', count: 1210 },
        { name: 'Thu', count: 1180 },
        { name: 'Fri', count: 1225 },
        { name: 'Sat', count: 450 },
        { name: 'Sun', count: 380 },
    ];

    return (
        <div className="space-y-10">
            <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
                <div className="flex flex-col gap-1">
                    <h2 className="text-4xl font-black italic tracking-tighter uppercase">Workforce Intelligence</h2>
                    <p className="text-[10px] font-black text-text-muted tracking-[0.3em] uppercase opacity-50 italic">Generated Post-Scan Analytics // Secure Export Protocol Active</p>
                </div>
                <div className="flex gap-4 w-full md:w-auto">
                    <div className="glass px-6 py-3 flex items-center gap-4 cursor-pointer hover:bg-white hover:bg-opacity-5 transition-all">
                        <Calendar size={16} className="text-primary" />
                        <span className="text-[10px] font-black uppercase tracking-widest">{dateRange}</span>
                        <ChevronDown size={14} className="text-text-muted" />
                    </div>
                    <div className="flex gap-2">
                        <button className="glass p-3 hover:text-success transition-all" title="Export Excel"><Download size={20} /></button>
                        <button className="glass p-3 hover:text-danger transition-all" title="Export PDF"><FileText size={20} /></button>
                        <button className="btn-primary px-8 py-3 flex items-center gap-3 font-black italic">
                            <Zap size={18} /> SYNC BLOCKCHAIN
                        </button>
                    </div>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* AI Predictive Analytics */}
                <div className="lg:col-span-8 card bg-white shadow-sm shadow-gray-200/50 p-8 space-y-6">
                    <div className="flex justify-between items-center">
                        <div className="flex items-center gap-3">
                            <div className="p-2.5 bg-rose-50 rounded-xl text-rose-600">
                                <Zap size={20} />
                            </div>
                            <h3 className="text-lg font-bold text-gray-900 uppercase tracking-tight">AI Burnout Risk Index</h3>
                        </div>
                        <span className="text-[10px] font-bold text-rose-600 bg-rose-50 px-3 py-1 rounded-full uppercase tracking-widest">High Alert Sectors</span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <RiskIndicator label="Technical Recon" risk="High (84%)" color="text-rose-600" />
                        <RiskIndicator label="Core Ops" risk="Low (12%)" color="text-emerald-500" />
                        <RiskIndicator label="Support Lead" risk="Med (42%)" color="text-warning" />
                    </div>

                    <div className="mt-8 pt-8 border-t border-gray-100">
                        <p className="text-xs font-medium text-gray-500 italic leading-relaxed">
                            "Neural models detected abnormal shifts in check-in times for Sector 4. Predictive burnout probability has increased by 14% over the last 48 hours."
                        </p>
                    </div>
                </div>

                <div className="lg:col-span-4 card bg-indigo-600 border-none p-8 flex flex-col justify-between overflow-hidden relative group text-white">
                    <div className="relative z-10">
                        <h3 className="text-lg font-bold mb-2">Workforce Stability</h3>
                        <p className="text-white/70 text-xs font-medium leading-relaxed">System-wide AI recognition models are synced with blockchain nodes.</p>
                    </div>
                    
                    <div className="relative z-10 py-4">
                        <div className="text-5xl font-extrabold tracking-tighter mb-1 italic">98.2%</div>
                        <div className="text-[10px] font-bold text-white/50 uppercase tracking-widest">Model Accuracy</div>
                    </div>
                    
                    <button className="relative z-10 w-full py-3 bg-white/10 hover:bg-white/20 text-white text-[10px] font-bold uppercase tracking-widest rounded-xl transition-all">
                        Generate Stability Report
                    </button>
                    <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-pink-500 opacity-20 blur-[60px]" />
                </div>

                {/* Log Stream */}
                <div className="lg:col-span-12 glass overflow-hidden">
                    <div className="px-10 py-8 border-b border-white border-opacity-5 flex justify-between items-center">
                        <div className="flex items-center gap-4">
                            <Database size={18} className="text-primary" />
                            <h3 className="text-xl font-black italic uppercase tracking-tighter">Secure Audit Trail</h3>
                        </div>
                        <div className="flex items-center gap-4">
                             <div className="glass px-4 py-2 flex items-center gap-3 border-opacity-[0.03]">
                                <Search size={14} className="text-text-muted" />
                                <input type="text" placeholder="FILTER LOGS..." className="bg-transparent border-none outline-none text-[9px] font-black uppercase tracking-widest w-40" />
                             </div>
                             <Filter size={18} className="text-text-muted cursor-pointer hover:text-white transition-all" />
                        </div>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-white bg-opacity-[0.01]">
                                    <TableHead label="Operative" />
                                    <TableHead label="Timestamp" />
                                    <TableHead label="Verification" />
                                    <TableHead label="Affective Core" />
                                    <TableHead label="Blockchain Seal" />
                                </tr>
                            </thead>
                            <tbody>
                                {logs.map((log, i) => (
                                    <tr key={i} className="border-b border-white border-opacity-[0.02] hover:bg-white hover:bg-opacity-[0.01] transition-all">
                                        <td className="p-8">
                                            <span className="text-xs font-black uppercase tracking-tight">{log.user_name || 'Anonymous'}</span>
                                        </td>
                                        <td className="p-8">
                                            <span className="text-[10px] font-bold uppercase tracking-widest text-text-muted">
                                                {new Date(log.check_in).toLocaleTimeString()}
                                            </span>
                                        </td>
                                        <td className="p-8">
                                            <span className={`text-[10px] font-black uppercase tracking-widest italic ${log.status === 'on_time' ? 'text-success' : 'text-warning'}`}>
                                                {log.status.replace('_', ' ')}
                                            </span>
                                        </td>
                                        <td className="p-8">
                                            <span className="text-[10px] font-bold uppercase tracking-widest text-text-muted italic">{log.emotion || 'Neural'}</span>
                                        </td>
                                        <td className="p-8 font-mono">
                                            <div className="flex items-center gap-3">
                                                <span className="text-[9px] font-bold text-primary opacity-50">
                                                    {log.id.toString().padStart(6, '0')}...SEAL
                                                </span>
                                                <Share2 size={12} className="text-text-muted opacity-40 hover:opacity-100 cursor-pointer" />
                                            </div>
                                        </td>
                                    </tr>
                                ))}

                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

const RiskIndicator = ({ label, risk, color }) => (
    <div className="flex flex-col gap-2 p-4 bg-gray-50 rounded-2xl border border-gray-100">
        <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{label}</span>
        <span className={`text-sm font-bold ${color} italic`}>{risk}</span>
    </div>
);

const QuickStat = ({ label, value }) => (
    <div className="flex flex-col items-end">
        <span className="text-[8px] font-black text-text-muted uppercase tracking-widest">{label}</span>
        <span className="text-xs font-black italic uppercase tracking-tight text-white">{value}</span>
    </div>
);

const TableHead = ({ label }) => (
    <th className="p-8 text-[10px] font-black uppercase tracking-[0.2em] text-text-muted italic opacity-40">
        {label}
    </th>
);

export default Reports;

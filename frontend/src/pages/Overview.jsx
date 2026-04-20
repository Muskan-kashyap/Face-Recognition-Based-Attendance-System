import React from 'react';
import { motion } from 'framer-motion';
import { 
    Users, 
    Activity, 
    Clock, 
    BrainCircuit, 
    ArrowUpRight, 
    Lightbulb, 
    Zap,
    ShieldCheck,
    AlertCircle
} from 'lucide-react';

const Overview = () => {
    return (
        <div className="space-y-8">
            {/* Header with Smart Insight */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-black tracking-tighter uppercase text-white">Tactical <span className="text-primary">Overview</span></h1>
                    <p className="text-text-muted text-xs font-bold uppercase tracking-widest mt-1">Node Status: Active | Analytics: Live</p>
                </div>
                <motion.div 
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="glass-panel px-4 py-3 flex items-center gap-3 border-primary/20 bg-primary/5"
                >
                    <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                        <BrainCircuit size={16} className="text-primary animate-pulse" />
                    </div>
                    <div className="text-[10px] font-black uppercase tracking-widest text-text-main">
                        <span className="text-primary">AI Insight:</span> Burnout risk detected in R&D Dept.
                    </div>
                </motion.div>
            </div>

            {/* Bento Grid Layout */}
            <div className="grid grid-cols-1 md:grid-cols-4 md:grid-rows-2 gap-4 h-full md:h-[600px]">
                
                {/* Main Metric - Punctuality */}
                <div className="md:col-span-2 md:row-span-1 glass-card p-6 flex flex-col justify-between group">
                    <div className="flex justify-between items-start">
                        <div className="p-3 bg-primary/10 rounded-xl text-primary"><Activity size={24} /></div>
                        <div className="text-success text-xs font-black flex items-center gap-1">
                            +12.4% <ArrowUpRight size={14} />
                        </div>
                    </div>
                    <div>
                        <h3 className="text-[10px] font-black text-text-dim uppercase tracking-[0.2em] mb-1">Organization Punctuality</h3>
                        <div className="text-5xl font-black text-white tracking-tighter italic">94.8%</div>
                    </div>
                </div>

                {/* Secondary Metric - Active Now */}
                <div className="md:col-span-1 md:row-span-1 glass-card p-6 flex flex-col justify-between">
                    <div className="p-3 bg-accent/10 rounded-xl text-accent self-start"><Users size={24} /></div>
                    <div>
                        <h3 className="text-[10px] font-black text-text-dim uppercase tracking-[0.2em] mb-1">Active Operatives</h3>
                        <div className="text-4xl font-black text-white tracking-tighter italic">124</div>
                    </div>
                </div>

                {/* Mini Metric - Sync */}
                <div className="md:col-span-1 md:row-span-1 glass-card p-6 flex flex-col justify-between bg-gradient-to-br from-primary/10 to-transparent">
                    <div className="p-3 bg-white/5 rounded-xl text-white self-start"><ShieldCheck size={24} /></div>
                    <div>
                        <h3 className="text-[10px] font-black text-text-dim uppercase tracking-[0.2em] mb-1">Blockchain Hash</h3>
                        <div className="text-xl font-mono text-primary truncate">0x7f...3e9</div>
                    </div>
                </div>

                {/* Large Visual Card - Productivity Trend */}
                <div className="md:col-span-3 md:row-span-1 glass-card p-6 relative overflow-hidden">
                    <div className="relative z-10">
                        <h3 className="text-[10px] font-black text-text-dim uppercase tracking-[0.2em] mb-6">Neural Productivity Matrix</h3>
                        <div className="h-48 flex items-end gap-2">
                            {[40, 60, 45, 90, 65, 80, 50, 85, 95, 70, 60, 75].map((h, i) => (
                                <motion.div 
                                    key={i}
                                    initial={{ height: 0 }}
                                    animate={{ height: `${h}%` }}
                                    transition={{ delay: i * 0.05, duration: 0.8 }}
                                    className="flex-1 bg-primary/20 hover:bg-primary transition-colors border-t border-primary/30"
                                />
                            ))}
                        </div>
                    </div>
                    {/* Background Grid Pattern */}
                    <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(var(--primary) 1px, transparent 1px)', backgroundSize: '20px 20px' }} />
                </div>

                {/* Smart Onboarding / Empty State Placeholder */}
                <div className="md:col-span-1 md:row-span-1 glass-card p-6 border-accent/30 bg-accent/5">
                    <div className="flex flex-col h-full justify-between">
                        <div className="space-y-4">
                            <div className="flex items-center gap-2">
                                <Zap size={18} className="text-accent" />
                                <span className="text-[10px] font-black uppercase tracking-widest text-white">Getting Started</span>
                            </div>
                            <div className="space-y-2">
                                <OnboardingStep text="Enroll first 10 Operatives" completed={true} />
                                <OnboardingStep text="Configure Department Shifts" completed={false} />
                                <OnboardingStep text="Secure Blockchain Root" completed={false} />
                            </div>
                        </div>
                        <button className="text-[10px] font-black uppercase tracking-widest text-accent hover:underline flex items-center gap-2">
                            Complete Setup <ArrowUpRight size={14} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

const OnboardingStep = ({ text, completed }) => (
    <div className="flex items-center gap-3">
        <div className={`w-4 h-4 rounded-md border ${completed ? 'bg-accent border-accent' : 'border-white/10'} flex items-center justify-center`}>
            {completed && <ShieldCheck size={10} color="black" />}
        </div>
        <span className={`text-[10px] font-bold uppercase tracking-tight ${completed ? 'text-text-dim line-through' : 'text-text-muted'}`}>
            {text}
        </span>
    </div>
);

export default Overview;

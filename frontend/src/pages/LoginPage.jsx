import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, Lock, User, ArrowRight, Fingerprint } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = (e) => {
        e.preventDefault();
        // Mock login
        navigate('/dashboard');
    };

    return (
        <div className="min-h-screen mesh-bg relative flex items-center justify-center p-6 overflow-hidden">
            <div className="noise-overlay" />
            
            {/* Animated Background Elements */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 blur-[120px] rounded-full animate-pulse" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-accent/10 blur-[120px] rounded-full animate-pulse" style={{ animationDelay: '2s' }} />

            <motion.div 
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className="w-full max-w-md relative z-10"
            >
                {/* Logo Area */}
                <div className="flex flex-col items-center mb-10">
                    <motion.div 
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        className="w-16 h-16 bg-primary rounded-2xl flex items-center justify-center shadow-2xl shadow-primary/40 mb-6 relative overflow-hidden"
                    >
                        <ShieldCheck color="white" size={32} />
                        <div className="scan-line" />
                    </motion.div>
                    <h1 className="text-4xl font-black italic uppercase tracking-tighter text-white">
                        Vision<span className="text-primary">Core</span>
                    </h1>
                    <p className="text-[10px] font-black uppercase tracking-[0.4em] text-text-muted mt-2">
                        Neural Identity Management
                    </p>
                </div>

                {/* Login Card */}
                <div className="glass-card p-10 relative group">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                    
                    <form onSubmit={handleLogin} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-[10px] font-black uppercase tracking-widest text-text-dim ml-1">Secure Identifier</label>
                            <div className="relative">
                                <User className="absolute left-4 top-1/2 -translate-y-1/2 text-text-dim" size={18} />
                                <input 
                                    type="text" 
                                    placeholder="OPERATIVE ID / EMAIL"
                                    className="w-full bg-bg-deep/50 border border-white/5 rounded-xl py-4 pl-12 pr-4 text-sm font-bold placeholder:text-text-dim focus:outline-none focus:border-primary/50 focus:ring-4 focus:ring-primary/10 transition-all"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <div className="flex justify-between items-center ml-1">
                                <label className="text-[10px] font-black uppercase tracking-widest text-text-dim">Encryption Key</label>
                                <a href="#" className="text-[10px] font-black uppercase tracking-widest text-primary hover:underline">Reset</a>
                            </div>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-text-dim" size={18} />
                                <input 
                                    type="password" 
                                    placeholder="••••••••••••"
                                    className="w-full bg-bg-deep/50 border border-white/5 rounded-xl py-4 pl-12 pr-4 text-sm font-bold placeholder:text-text-dim focus:outline-none focus:border-primary/50 focus:ring-4 focus:ring-primary/10 transition-all"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                        </div>

                        <button 
                            type="submit"
                            className="w-full btn-premium btn-primary shadow-xl shadow-primary/20"
                        >
                            Establish Uplink <ArrowRight size={18} />
                        </button>
                    </form>

                    <div className="mt-10 pt-8 border-t border-white/5 flex flex-col items-center gap-6">
                        <div className="flex items-center gap-4 w-full">
                            <div className="h-px bg-white/5 flex-1" />
                            <span className="text-[9px] font-black uppercase tracking-[0.3em] text-text-dim">Biometric Bypass</span>
                            <div className="h-px bg-white/5 flex-1" />
                        </div>
                        
                        <button className="flex items-center gap-3 text-[10px] font-black uppercase tracking-widest text-text-muted hover:text-white transition-all">
                            <Fingerprint size={20} className="text-primary" />
                            Use Registered Facial ID
                        </button>
                    </div>
                </div>

                {/* Footer Footer */}
                <div className="mt-12 text-center">
                    <p className="text-[10px] font-bold text-text-dim uppercase tracking-widest">
                        Node: <span className="text-white">US-EAST-01</span> | Status: <span className="text-success animate-pulse">Synced</span>
                    </p>
                </div>
            </motion.div>
        </div>
    );
};

export default LoginPage;

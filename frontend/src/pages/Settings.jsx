import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
    Settings as SettingsIcon, 
    Bell, 
    Shield, 
    Zap, 
    Eye, 
    Moon, 
    Sun, 
    Smartphone,
    Globe,
    Cpu,
    Lock
} from 'lucide-react';

const Settings = () => {
    const [theme, setTheme] = useState('dark');
    const [sensitivity, setSensitivity] = useState(85);

    return (
        <div className="max-w-4xl mx-auto py-8">
            <header className="mb-12">
                <div className="flex items-center gap-4 mb-2">
                    <div className="w-12 h-12 glass-panel flex items-center justify-center text-primary">
                        <SettingsIcon size={24} />
                    </div>
                    <div>
                        <h2 className="text-4xl font-black tracking-tighter uppercase italic">System Configuration</h2>
                        <p className="text-[10px] font-black tracking-[0.4em] text-text-muted uppercase">Terminal Settings // Global Preferences</p>
                    </div>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Visual Preferences */}
                <section className="glass-card p-8 space-y-8">
                    <div className="flex items-center gap-3 border-b border-white/5 pb-4">
                        <Eye className="text-primary" size={20} />
                        <h3 className="text-xs font-black uppercase tracking-widest">Visual Core</h3>
                    </div>
                    
                    <div className="space-y-6">
                        <div className="flex justify-between items-center">
                            <div>
                                <p className="text-sm font-bold uppercase tracking-tight">Interface Theme</p>
                                <p className="text-[10px] text-text-dim uppercase tracking-wider">Switch between Light / Deep mode</p>
                            </div>
                            <div className="flex p-1 glass-panel rounded-xl">
                                <button 
                                    onClick={() => setTheme('light')}
                                    className={`p-2 rounded-lg transition-all ${theme === 'light' ? 'bg-primary text-white shadow-lg' : 'text-text-muted hover:text-white'}`}
                                >
                                    <Sun size={18} />
                                </button>
                                <button 
                                    onClick={() => setTheme('dark')}
                                    className={`p-2 rounded-lg transition-all ${theme === 'dark' ? 'bg-primary text-white shadow-lg' : 'text-text-muted hover:text-white'}`}
                                >
                                    <Moon size={18} />
                                </button>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div className="flex justify-between">
                                <p className="text-sm font-bold uppercase tracking-tight">AI HUD Opacity</p>
                                <span className="text-[10px] font-black text-primary">85%</span>
                            </div>
                            <input type="range" className="w-full accent-primary bg-white/10 h-1.5 rounded-full appearance-none" />
                        </div>
                    </div>
                </section>

                {/* Biometric Sensitivity */}
                <section className="glass-card p-8 space-y-8">
                    <div className="flex items-center gap-3 border-b border-white/5 pb-4">
                        <Cpu className="text-secondary" size={20} />
                        <h3 className="text-xs font-black uppercase tracking-widest">Neural Thresholds</h3>
                    </div>
                    
                    <div className="space-y-6">
                        <div className="space-y-4">
                            <div className="flex justify-between">
                                <div>
                                    <p className="text-sm font-bold uppercase tracking-tight">Recognition Sensitivity</p>
                                    <p className="text-[10px] text-text-dim uppercase tracking-wider">Confidence required for match</p>
                                </div>
                                <span className="text-[10px] font-black text-secondary">{sensitivity}%</span>
                            </div>
                            <input 
                                type="range" 
                                value={sensitivity}
                                onChange={(e) => setSensitivity(e.target.value)}
                                className="w-full accent-secondary bg-white/10 h-1.5 rounded-full appearance-none" 
                            />
                        </div>

                        <div className="flex justify-between items-center">
                            <div>
                                <p className="text-sm font-bold uppercase tracking-tight">3D Liveness Check</p>
                                <p className="text-[10px] text-text-dim uppercase tracking-wider">Anti-spoofing protection</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" className="sr-only peer" defaultChecked />
                                <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-secondary"></div>
                            </label>
                        </div>
                    </div>
                </section>

                {/* Privacy & Trending Features */}
                <section className="glass-card p-8 space-y-8">
                    <div className="flex items-center gap-3 border-b border-white/5 pb-4">
                        <Globe className="text-emerald-500" size={20} />
                        <h3 className="text-xs font-black uppercase tracking-widest">Privacy & PII</h3>
                    </div>
                    
                    <div className="space-y-6">
                        <div className="flex justify-between items-center">
                            <div>
                                <p className="text-sm font-bold uppercase tracking-tight">Anonymized Reports</p>
                                <p className="text-[10px] text-text-dim uppercase tracking-wider">Mask names in analytics for GDPR</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" className="sr-only peer" />
                                <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
                            </label>
                        </div>

                        <div className="flex justify-between items-center">
                            <div>
                                <p className="text-sm font-bold uppercase tracking-tight">Mobile Edge Marking</p>
                                <p className="text-[10px] text-text-dim uppercase tracking-wider">Allow check-in via authorized PWA</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" className="sr-only peer" defaultChecked />
                                <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                            </label>
                        </div>
                    </div>
                </section>

                {/* Subscription & Limits */}
                <section className="glass-card p-8 space-y-8">
                    <div className="flex items-center gap-3 border-b border-white/5 pb-4">
                        <Zap className="text-amber-500" size={20} />
                        <h3 className="text-xs font-black uppercase tracking-widest">SaaS Subscription</h3>
                    </div>
                    
                    <div className="space-y-4">
                        <div className="flex justify-between items-center">
                            <span className="text-xs font-bold uppercase">Current Plan</span>
                            <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-[9px] font-black uppercase text-amber-500">Starter (Free)</span>
                        </div>
                        <div className="space-y-2">
                            <div className="flex justify-between text-[10px] font-bold uppercase text-text-dim">
                                <span>Identities Used</span>
                                <span>8 / 10 Users</span>
                            </div>
                            <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                                <div className="h-full bg-amber-500 w-[80%]" />
                            </div>
                        </div>
                        <button className="w-full mt-4 py-3 bg-amber-500/10 border border-amber-500/20 text-amber-500 text-[10px] font-black uppercase tracking-widest hover:bg-amber-500 hover:text-white transition-all rounded-xl">
                            Upgrade to Pro
                        </button>
                    </div>
                </section>

                {/* Audit & Ledger */}
                <section className="glass-card p-8 space-y-8 md:col-span-2">
                    <div className="flex items-center gap-3 border-b border-white/5 pb-4">
                        <Lock className="text-accent" size={20} />
                        <h3 className="text-xs font-black uppercase tracking-widest">Audit & Ledger Integrity</h3>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <div className="space-y-2">
                             <p className="text-[10px] font-bold text-text-dim uppercase tracking-widest">Blockchain Anchor</p>
                             <p className="text-xs font-black italic">Active on Mainnet Node-4</p>
                        </div>
                        <div className="space-y-2">
                             <p className="text-[10px] font-bold text-text-dim uppercase tracking-widest">Manual Override Access</p>
                             <p className="text-xs font-black italic text-primary">Restricted to Admin/Manager</p>
                        </div>
                        <div className="flex justify-end items-center text-right">
                             <p className="text-[9px] text-text-dim uppercase font-bold tracking-tighter">All manual edits are hashed <br/> and pinned to audit trail</p>
                        </div>
                    </div>
                </section>

            </div>

            <div className="mt-12 flex justify-end gap-4">
                <button className="px-8 py-4 glass text-[10px] font-black uppercase tracking-widest">Reset Defaults</button>
                <button className="px-12 py-4 btn-premium btn-primary text-[10px] font-black uppercase tracking-widest">Apply Systems Update</button>
            </div>
        </div>
    );
};

export default Settings;

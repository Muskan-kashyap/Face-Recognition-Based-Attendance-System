import React from 'react';
import { motion } from 'framer-motion';
import { 
    Fingerprint, 
    Zap, 
    ArrowRight, 
    ShieldCheck, 
    TrendingUp, 
    Cpu, 
    Lock, 
    Activity
} from 'lucide-react';
import { Link } from 'react-router-dom';

const LandingPage = () => {
    return (
        <div className="min-h-screen bg-bg-deep selection:bg-primary/30 text-text-main overflow-x-hidden">
            {/* Glossy Navigation */}
            <nav className="fixed top-0 w-full z-50 px-6 py-4">
                <div className="max-w-7xl mx-auto glass-panel px-8 py-3 flex justify-between items-center shadow-2xl">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 grad-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary-glow/20">
                            <Fingerprint className="text-white" size={24} />
                        </div>
                        <span className="text-xl font-bold tracking-tight text-white">VISION<span className="grad-text">CORE</span></span>
                    </div>
                    
                    <div className="hidden md:flex items-center gap-8 text-sm font-medium text-text-muted">
                        <a href="#features" className="hover:text-primary transition-colors">Platform</a>
                        <a href="#intelligence" className="hover:text-primary transition-colors">Intelligence</a>
                        <a href="#security" className="hover:text-primary transition-colors">Security</a>
                    </div>

                    <div className="flex items-center gap-4">
                        <Link to="/login" className="text-sm font-semibold hover:text-white px-4 py-2 transition-all">Sign In</Link>
                        <Link to="/signup" className="btn-premium btn-primary text-sm">
                            Get Started Free <ArrowRight size={16} />
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="relative pt-48 pb-32 px-6">
                {/* Background Glows */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-primary/10 blur-[120px] rounded-full -z-10" />
                
                <div className="max-w-6xl mx-auto text-center relative">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/10 bg-white/5 text-[10px] font-bold uppercase tracking-widest text-primary mb-8"
                    >
                        <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse" />
                        Next-Gen Workforce Intelligence
                    </motion.div>
                    
                    <motion.h1 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-6xl md:text-8xl font-bold tracking-tight mb-8 leading-[1.1]"
                    >
                        Automate Presence <br />
                        <span className="grad-text">With AI Precision.</span>
                    </motion.h1>

                    <motion.p 
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="text-lg md:text-xl text-text-muted max-w-3xl mx-auto mb-12 leading-relaxed"
                    >
                        VisionCore combines enterprise-grade facial recognition with deep workforce 
                        analytics to eliminate fraud, reduce burnout, and skyrocket productivity.
                    </motion.p>

                    <motion.div 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="flex flex-wrap justify-center gap-4 mb-20"
                    >
                        <Link to="/signup" className="btn-premium btn-primary px-10 py-5 text-lg">
                            Deploy to Your Organization
                        </Link>
                        <button className="btn-premium bg-white/5 hover:bg-white/10 text-white px-10 py-5 text-lg">
                            Watch Video Demo
                        </button>
                    </motion.div>

                    {/* Preview Dashboard Card */}
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4, duration: 0.8 }}
                        className="relative max-w-5xl mx-auto bg-bg-card rounded-[2rem] border border-white/10 p-4 shadow-2xl"
                    >
                        <div className="absolute -top-10 -right-10 w-40 h-40 bg-secondary/20 blur-[80px] -z-10" />
                        <div className="absolute -bottom-10 -left-10 w-40 h-40 bg-primary/20 blur-[80px] -z-10" />
                        <img 
                            src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=2000" 
                            alt="Dashboard Preview" 
                            className="rounded-2xl opacity-80"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-bg-card/80 to-transparent rounded-2xl" />
                    </motion.div>
                </div>
            </section>

            {/* Feature Bento Grid */}
            <section id="features" className="py-32 px-6">
                <div className="max-w-7xl mx-auto">
                    <div className="mb-20">
                        <h2 className="text-4xl font-bold mb-4">Powerful Features.</h2>
                        <p className="text-text-muted text-lg">Everything you need to manage a modern, high-performance team.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <BentoCard 
                            title="Liveness Detection" 
                            icon={ShieldCheck} 
                            desc="3D anti-spoofing technology ensures only real, physically present employees can clock in."
                            className="md:col-span-2"
                        />
                        <BentoCard 
                            title="Emotion Insights" 
                            icon={Activity} 
                            desc="Monitor workforce morale in real-time using affective computing core."
                        />
                        <BentoCard 
                            title="Predictive Analytics" 
                            icon={TrendingUp} 
                            desc="Identify burnout risks before they happen with our growth index algorithms."
                        />
                        <BentoCard 
                            title="Blockchain Integrity" 
                            icon={Lock} 
                            desc="Every attendance log is hashed and anchored to an immutable ledger for audit compliance."
                            className="md:col-span-2"
                        />
                    </div>
                </div>
            </section>

            {/* Pricing Section */}
            <section id="pricing" className="py-32 px-6 bg-white/[0.02]">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-20">
                        <h2 className="text-4xl font-bold mb-4">Enterprise-Ready Pricing.</h2>
                        <p className="text-text-muted text-lg">Scale security from 10 to 10,000+ employees.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <PriceCard 
                            tier="Starter" 
                            price="0" 
                            features={['Up to 10 Users', 'Basic Biometrics', 'Community Support']} 
                        />
                        <PriceCard 
                            tier="Pro" 
                            price="49" 
                            featured 
                            features={['Up to 100 Users', 'Liveness Detection', 'Advanced Analytics', 'Priority Support']} 
                        />
                        <PriceCard 
                            tier="Enterprise" 
                            price="Custom" 
                            features={['Unlimited Users', 'Blockchain Ledger', 'Custom AI Models', 'Whitelabeling']} 
                        />
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-32 px-6">
                <div className="max-w-5xl mx-auto glass-card p-12 md:p-20 text-center relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent" />
                    <h2 className="text-4xl md:text-5xl font-bold mb-6">Ready to upgrade your workforce?</h2>
                    <p className="text-text-muted text-lg mb-12 max-w-2xl mx-auto">
                        Join 2,000+ companies already using VisionCore to build more transparent 
                        and productive organizations.
                    </p>
                    <Link to="/signup" className="btn-premium btn-primary px-12 py-5 text-xl">
                        Start Your 14-Day Free Trial
                    </Link>
                </div>
            </section>

            <footer className="py-20 border-t border-white/5">
                <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-8">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 grad-primary rounded-lg flex items-center justify-center">
                            <Fingerprint className="text-white" size={16} />
                        </div>
                        <span className="text-lg font-bold">VISIONCORE</span>
                    </div>
                    <p className="text-text-dim text-sm">© 2026 VisionCore Biometrics Inc. All rights reserved.</p>
                    <div className="flex gap-6 text-sm text-text-dim">
                        <a href="#" className="hover:text-white">Privacy</a>
                        <a href="#" className="hover:text-white">Terms</a>
                        <a href="#" className="hover:text-white">Security</a>
                    </div>
                </div>
            </footer>
        </div>
    );
};

const BentoCard = ({ title, icon: Icon, desc, className = "" }) => (
    <div className={`glass-card p-8 group ${className}`}>
        <div className="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            <Icon className="text-primary" size={24} />
        </div>
        <h3 className="text-xl font-bold mb-4">{title}</h3>
        <p className="text-text-muted leading-relaxed">{desc}</p>
    </div>
);

const PriceCard = ({ tier, price, features, featured = false }) => (
    <div className={`glass-card p-10 flex flex-col ${featured ? 'border-primary ring-1 ring-primary/50 scale-105 z-10' : 'border-white/5'}`}>
        <h3 className="text-xl font-bold mb-2 uppercase tracking-tight">{tier}</h3>
        <div className="flex items-baseline gap-1 mb-8">
            <span className="text-4xl font-extrabold">{price === 'Custom' ? 'Custom' : `$${price}`}</span>
            {price !== 'Custom' && <span className="text-text-muted text-sm font-medium">/mo</span>}
        </div>
        <ul className="space-y-4 mb-10 flex-1">
            {features.map((f, i) => (
                <li key={i} className="flex gap-3 text-sm text-text-muted">
                    <ShieldCheck size={16} className="text-primary shrink-0" /> {f}
                </li>
            ))}
        </ul>
        <button className={`w-full py-4 rounded-xl text-sm font-bold uppercase tracking-widest transition-all ${featured ? 'btn-primary shadow-lg shadow-primary-glow/20' : 'bg-white/5 hover:bg-white/10 text-white'}`}>
            Select {tier}
        </button>
    </div>
);

export default LandingPage;


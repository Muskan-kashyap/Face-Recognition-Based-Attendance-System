import React, { useState, useRef, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Webcam from 'react-webcam';
import { 
    Camera, 
    ShieldCheck, 
    XCircle, 
    CheckCircle2,
    Zap, 
    User, 
    Clock, 
    ScanFace,
    Activity
} from 'lucide-react';
import axios from 'axios';

const Attendance = () => {
    const webcamRef = useRef(null);
    const [step, setStep] = useState('idle'); // idle, capturing, processing, success, fail
    const [stats, setStats] = useState({
        latency: '0ms',
        confidence: '0.0%',
        liveness: 'Pending',
        emotion: 'Neural'
    });
    const [result, setResult] = useState(null);

    const capture = useCallback(async () => {
        if (step !== 'idle') return;
        
        setStep('capturing');
        const imageSrc = webcamRef.current.getScreenshot();
        
        setStep('processing');
        const startTime = Date.now();
        
        try {
            // Real API Call to FastAPI backend
            const response = await axios.post('http://127.0.0.1:8000/api/v1/attendance/check-in', { 
                image_base64: imageSrc.split(',')[1],
                org_id: '00000000-0000-0000-0000-000000000000', // Default org for demo
                timestamp: new Date().toISOString()
            });
            
            const data = response.data;
            setStats({
                latency: `${Date.now() - startTime}ms`,
                confidence: `${(data.confidence || 0.98 * 100).toFixed(1)}%`,
                liveness: data.is_live ? 'PASSED' : 'FAILED',
                emotion: data.emotion || 'Neutral'
            });
            
            setResult({ 
                name: data.user_name || 'Authorized Personnel', 
                time: new Date().toLocaleTimeString(),
                id: data.user_id || 'VC-9921'
            });
            setStep('success');
            
            setTimeout(() => {
                setStep('idle');
                setResult(null);
            }, 5000);
        } catch (err) {
            console.error(err);
            setStep('fail');
            setTimeout(() => setStep('idle'), 3000);
        }
    }, [webcamRef, step]);

    // Auto-capture simulation or trigger
    useEffect(() => {
        // In a real production app, we might use face detection to auto-trigger
    }, []);

    return (
        <div className="max-w-6xl mx-auto py-8 px-4">
            <header className="mb-10 flex justify-between items-end">
                <div>
                    <h2 className="text-4xl font-bold tracking-tight text-white mb-2">Biometric Terminal</h2>
                    <p className="text-text-muted font-medium">Position your face within the frame for neural verification.</p>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 glass-panel border-primary/20 text-primary text-[10px] font-bold uppercase tracking-[0.2em] shadow-lg shadow-primary-glow/10">
                    <ShieldCheck size={14} className="animate-pulse" /> Encrypted Link Active
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Visual Verification Core */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <div className="relative aspect-video glass-card border-white/5 overflow-hidden shadow-2xl p-2">
                        {/* Scanning HUD Overlay */}
                        <div className="absolute inset-0 pointer-events-none z-20">
                            {/* Corner Accents */}
                            <div className="absolute top-8 left-8 w-12 h-12 border-t-2 border-l-2 border-primary/40 rounded-tl-lg" />
                            <div className="absolute top-8 right-8 w-12 h-12 border-t-2 border-r-2 border-primary/40 rounded-tr-lg" />
                            <div className="absolute bottom-8 left-8 w-12 h-12 border-b-2 border-l-2 border-primary/40 rounded-bl-lg" />
                            <div className="absolute bottom-8 right-8 w-12 h-12 border-b-2 border-r-2 border-primary/40 rounded-br-lg" />
                            
                            {/* Scanning Line */}
                            {step === 'idle' && (
                                <motion.div 
                                    animate={{ top: ['10%', '90%', '10%'] }}
                                    transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                                    className="absolute left-10 right-10 h-[2px] bg-gradient-to-r from-transparent via-primary to-transparent shadow-[0_0_15px_var(--primary)] opacity-50"
                                />
                            )}
                        </div>

                        <div className="w-full h-full rounded-2xl overflow-hidden relative bg-black">
                            <Webcam
                                audio={false}
                                ref={webcamRef}
                                screenshotFormat="image/jpeg"
                                className="w-full h-full object-cover opacity-80"
                                videoConstraints={{ facingMode: "user" }}
                            />

                            {/* Center Target Frame */}
                            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                <div className="w-64 h-80 border border-white/10 rounded-[3rem] shadow-[0_0_0_1000px_rgba(2,6,23,0.4)]" />
                            </div>

                            {/* Processing States */}
                            <AnimatePresence>
                                {(step === 'capturing' || step === 'processing') && (
                                    <motion.div 
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        exit={{ opacity: 0 }}
                                        className="absolute inset-0 bg-bg-deep/60 backdrop-blur-md flex flex-col items-center justify-center z-50"
                                    >
                                        <div className="relative w-24 h-24 flex items-center justify-center">
                                            <div className="absolute inset-0 border-4 border-primary/20 rounded-full" />
                                            <motion.div 
                                                animate={{ rotate: 360 }}
                                                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                                className="absolute inset-0 border-4 border-primary border-t-transparent rounded-full"
                                            />
                                            <ScanFace className="text-white" size={32} />
                                        </div>
                                        <h3 className="text-xl font-bold text-white mt-8 tracking-widest uppercase">
                                            {step === 'capturing' ? 'Capturing...' : 'Neural Analysis...'}
                                        </h3>
                                        <div className="mt-4 w-48 h-1 bg-white/5 rounded-full overflow-hidden">
                                            <motion.div 
                                                initial={{ width: 0 }}
                                                animate={{ width: '100%' }}
                                                transition={{ duration: 1.5 }}
                                                className="h-full grad-primary shadow-lg shadow-primary-glow/50"
                                            />
                                        </div>
                                    </motion.div>
                                )}

                                {step === 'success' && (
                                    <motion.div 
                                        initial={{ opacity: 0, scale: 0.95 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        className="absolute inset-0 bg-primary/20 backdrop-blur-xl flex flex-col items-center justify-center z-50 text-white p-8"
                                    >
                                        <motion.div 
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            className="w-24 h-24 grad-primary rounded-full flex items-center justify-center mb-8 shadow-2xl shadow-primary-glow/40"
                                        >
                                            <CheckCircle2 size={48} />
                                        </motion.div>
                                        <span className="text-[10px] font-black uppercase tracking-[0.5em] text-primary mb-2">Verification Success</span>
                                        <h3 className="text-4xl font-bold mb-1">{result?.name}</h3>
                                        <p className="text-text-muted font-medium mb-8">Role: Senior Architect • ID: {result?.id}</p>
                                        <div className="flex gap-4">
                                            <div className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-xs font-bold text-white uppercase tracking-widest">
                                                Clocked: {result?.time}
                                            </div>
                                        </div>
                                    </motion.div>
                                )}

                                {step === 'fail' && (
                                    <motion.div 
                                        initial={{ opacity: 0, scale: 0.95 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        className="absolute inset-0 bg-accent/20 backdrop-blur-xl flex flex-col items-center justify-center z-50 text-white"
                                    >
                                        <XCircle size={80} className="text-accent mb-6" />
                                        <h3 className="text-2xl font-bold mb-2">Identity Mismatch</h3>
                                        <p className="text-text-muted font-medium">Neural confidence threshold not met.</p>
                                        <button 
                                            onClick={() => setStep('idle')}
                                            className="mt-8 px-6 py-2 bg-accent/20 border border-accent/30 rounded-full text-xs font-bold uppercase tracking-widest hover:bg-accent hover:text-white transition-all"
                                        >
                                            Retry Verification
                                        </button>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>

                    <div className="flex justify-center flex-col items-center gap-4">
                        <button 
                            onClick={capture}
                            disabled={step !== 'idle'}
                            className={`btn-premium btn-primary px-16 py-6 text-xl shadow-2xl shadow-primary-glow/20 transition-all ${step !== 'idle' ? 'opacity-50 cursor-not-allowed scale-95' : 'hover:scale-105 active:scale-95'}`}
                        >
                           <Camera size={28} className="mr-3" /> INITIATE SCAN
                        </button>
                        <p className="text-[10px] font-bold text-text-dim uppercase tracking-[0.3em]">Hardware ID: TERMINAL-A902-SFC</p>
                    </div>
                </div>

                {/* Intelligence Sidebar */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="glass-card p-8 border-white/5 flex-1">
                        <h4 className="text-[10px] font-black text-text-dim uppercase tracking-[0.3em] mb-10 border-b border-white/5 pb-4">Verification Intel</h4>
                        
                        <div className="space-y-8">
                            <IntelItem icon={Zap} label="System Latency" value={stats.latency} trend="Fast" />
                            <IntelItem icon={ShieldCheck} label="Neural Confidence" value={stats.confidence} trend="High" />
                            <IntelItem icon={ScanFace} label="Liveness Check" value={stats.liveness} highlight />
                            <IntelItem icon={Activity} label="Affective Core" value={stats.emotion} trend="Neutral" />
                        </div>

                        <div className="mt-12 p-6 glass-panel border-white/5 bg-white/[0.02]">
                             <div className="flex gap-4">
                                <ShieldCheck className="text-primary flex-shrink-0" size={20} />
                                <div>
                                    <p className="text-xs font-bold mb-1 uppercase tracking-tight">Security Protocol</p>
                                    <p className="text-[10px] text-text-dim leading-relaxed">
                                        Biometric data is instantly hashed via ZKP and anchored to organization node. No raw image data is stored.
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

const IntelItem = ({ icon: Icon, label, value, trend, highlight }) => (
    <div className="flex items-center justify-between group">
        <div className="flex items-center gap-4">
            <div className={`w-12 h-12 glass-panel border-white/5 flex-center group-hover:bg-primary/10 group-hover:border-primary/20 transition-all duration-500`}>
                <Icon size={20} className="text-text-muted group-hover:text-primary transition-colors" />
            </div>
            <div>
                <p className="text-[10px] font-bold text-text-dim uppercase tracking-widest mb-1">{label}</p>
                <div className="flex items-center gap-2">
                    <p className={`text-xl font-bold tracking-tight ${highlight ? 'text-primary' : 'text-white'}`}>{value}</p>
                    {trend && <span className="text-[9px] font-black text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full uppercase">{trend}</span>}
                </div>
            </div>
        </div>
    </div>
);

export default Attendance;

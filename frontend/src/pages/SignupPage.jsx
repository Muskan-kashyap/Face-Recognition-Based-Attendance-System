import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, ChevronRight, Mail, Lock, User, Building, MapPin } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const SignupPage = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        name: '', email: '', password: '', role: 'Admin', organization: '', department: '', city: ''
    });

    const handleSignup = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const resp = await axios.post('http://127.0.0.1:8000/api/v1/auth/register', formData);
            if (resp.data.status === 'success') {
                navigate('/login');
            }
        } catch (err) {
            console.error(err);
            alert(err.response?.data?.detail || "Registration Failed");
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-bg-deep text-text-main flex flex-col justify-center items-center p-6 font-['Outfit']">
            <div className="fixed inset-0 pointer-events-none overflow-hidden">
                <div className="absolute top-1/4 -right-1/4 w-[500px] h-[500px] bg-primary opacity-5 blur-[120px]" />
                <div className="absolute bottom-1/4 -left-1/4 w-[500px] h-[500px] bg-secondary opacity-5 blur-[120px]" />
            </div>

            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass w-full max-w-xl relative p-12 overflow-hidden"
            >
                <div className="flex flex-col items-center gap-6 mb-12">
                    <div className="w-16 h-16 bg-primary rounded-2xl flex items-center justify-center shadow-2xl shadow-primary-glow">
                        <Shield color="white" size={32} />
                    </div>
                    <div className="text-center">
                        <h2 className="text-3xl font-black italic tracking-tighter uppercase mb-1">Establish Protocol</h2>
                        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-text-muted opacity-50 italic">System Onboarding Phase: {step} / 2</p>
                    </div>
                </div>

                <form onSubmit={handleSignup} className="space-y-8">
                    {step === 1 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <InputField 
                                label="Full Identity" 
                                icon={User} 
                                placeholder="E.g. Price" 
                                value={formData.name} 
                                onChange={(val) => setFormData({...formData, name: val})} 
                            />
                            <InputField 
                                label="Secure Email" 
                                icon={Mail} 
                                type="email" 
                                placeholder="price@hq.com" 
                                value={formData.email} 
                                onChange={(val) => setFormData({...formData, email: val})} 
                            />
                            <InputField 
                                label="Access Cipher" 
                                icon={Lock} 
                                type="password" 
                                placeholder="••••••••" 
                                value={formData.password} 
                                onChange={(val) => setFormData({...formData, password: val})} 
                            />
                            <div className="flex flex-col gap-2">
                                <label className="text-[10px] font-black uppercase text-primary tracking-widest pl-1">Primary Role</label>
                                <select 
                                    className="glass bg-transparent p-4 rounded-xl border-white border-opacity-5 outline-none text-xs font-bold appearance-none cursor-pointer hover:bg-white hover:bg-opacity-5 transition-all"
                                    value={formData.role}
                                    onChange={(e) => setFormData({...formData, role: e.target.value})}
                                >
                                    <option value="Admin">Admin (System Overlord)</option>
                                    <option value="Manager">Manager (Tactical Lead)</option>
                                    <option value="Employee">Employee (Field Agent)</option>
                                </select>
                            </div>
                            <div className="md:col-span-2">
                                <button type="button" onClick={() => setStep(2)} className="btn-primary w-full py-5 flex items-center justify-center gap-3 font-black italic tracking-tighter mt-4">
                                    CONTINUE TO DEPLOYMENT <ChevronRight size={18} />
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <InputField 
                                label="Organization" 
                                icon={Building} 
                                placeholder="E.g. SAS Task Force" 
                                value={formData.organization} 
                                onChange={(val) => setFormData({...formData, organization: val})} 
                            />
                            <InputField 
                                label="Department" 
                                icon={Shield} 
                                placeholder="E.g. Recon Team" 
                                value={formData.department} 
                                onChange={(val) => setFormData({...formData, department: val})} 
                            />
                            <InputField 
                                label="Operation Base (City)" 
                                icon={MapPin} 
                                placeholder="E.g. London" 
                                value={formData.city} 
                                onChange={(val) => setFormData({...formData, city: val})} 
                            />
                            <div className="md:col-span-2 h-12" />
                            <div className="flex gap-4 md:col-span-2">
                                <button type="button" onClick={() => setStep(1)} className="glass px-8 py-5 text-xs font-black uppercase hover:bg-opacity-10">Back</button>
                                <button type="submit" disabled={loading} className="btn-primary flex-1 py-5 flex items-center justify-center gap-3 font-black italic tracking-tighter">
                                    {loading ? "INITIALIZING..." : "FINALIZE ONBOARDING"}
                                </button>
                            </div>
                        </div>
                    )}
                </form>

                <div className="mt-12 pt-8 border-t border-white border-opacity-5 text-center">
                    <p className="text-[10px] font-bold text-text-muted uppercase tracking-widest italic">Already registered? <Link to="/login" className="text-primary hover:underline">Authorize Access</Link></p>
                </div>
            </motion.div>
        </div>
    );
};

const InputField = ({ label, icon: Icon, placeholder, value, onChange, type = "text" }) => (
    <div className="flex flex-col gap-2">
        <label className="text-[10px] font-black uppercase text-primary tracking-widest pl-1">{label}</label>
        <div className="relative">
            <Icon className="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted" size={16} />
            <input 
                type={type}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="glass bg-transparent w-full p-4 pl-12 rounded-xl border-white border-opacity-5 outline-none text-xs font-bold placeholder-text-muted focus:border-primary focus:border-opacity-30 transition-all"
                placeholder={placeholder}
            />
        </div>
    </div>
);

export default SignupPage;

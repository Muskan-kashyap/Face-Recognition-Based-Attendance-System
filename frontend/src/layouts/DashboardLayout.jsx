import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    LayoutDashboard, 
    Clock, 
    Users, 
    BarChart3, 
    Settings, 
    ShieldCheck, 
    Bell, 
    Search,
    Menu,
    X,
    LogOut,
    UserCircle,
    Activity,
    Ticket,
    CreditCard,
    Receipt
} from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

const DashboardLayout = ({ children, userRole = 'Admin' }) => {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const location = useLocation();
    const navigate = useNavigate();

    const navItems = [
        { id: 'overview', label: 'Tactical Overview', icon: LayoutDashboard, path: '/dashboard', roles: ['Admin', 'Manager', 'Employee'] },
        { id: 'attendance', label: 'Biometric Access', icon: Clock, path: '/dashboard/attendance', roles: ['Admin', 'Manager', 'Employee'] },
        { id: 'users', label: 'Identity Management', icon: Users, path: '/dashboard/users', roles: ['Admin', 'Manager'] },
        { id: 'reports', label: 'Workforce Intel', icon: Activity, path: '/dashboard/reports', roles: ['Admin', 'Manager'] },
        { id: 'ticketing', label: 'Support Terminal', icon: Ticket, path: '/dashboard/ticketing', roles: ['Admin', 'Manager', 'Employee'] },
        { id: 'payroll', label: 'Payroll Intel', icon: CreditCard, path: '/dashboard/payroll', roles: ['Admin', 'Manager', 'Employee'] },
        { id: 'reimbursements', label: 'Payout Hub', icon: Receipt, path: '/dashboard/reimbursements', roles: ['Admin', 'Manager', 'Employee'] },
        { id: 'settings', label: 'Configuration', icon: Settings, path: '/dashboard/settings', roles: ['Admin', 'Manager', 'Employee'] },
    ];

    const filteredNav = navItems.filter(item => item.roles.includes(userRole));

    return (
        <div className="min-h-screen bg-bg-deep text-text-main flex font-['Outfit'] overflow-hidden">
            {/* Sidebar */}
            <motion.aside 
                initial={false}
                animate={{ width: sidebarOpen ? 300 : 100 }}
                className="glass border-r border-white border-opacity-5 h-screen flex flex-col p-6 z-50 overflow-hidden"
            >
                <div className="flex items-center gap-4 px-2 mb-12">
                    <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary-glow shrink-0">
                        <ShieldCheck color="white" size={20} />
                    </div>
                    {sidebarOpen && (
                        <motion.span 
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-xl font-black italic uppercase tracking-tighter whitespace-nowrap"
                        >
                            Vision<span className="text-primary">Core</span>
                        </motion.span>
                    )}
                </div>

                <nav className="flex flex-col gap-2 flex-1">
                    {filteredNav.map((item) => (
                        <Link 
                            key={item.id} 
                            to={item.path}
                            className={`flex items-center gap-4 p-4 rounded-2xl transition-all relative group ${location.pathname === item.path ? 'bg-primary shadow-xl shadow-primary-glow text-white' : 'text-text-muted hover:bg-white hover:bg-opacity-5'}`}
                        >
                            <item.icon size={20} className="shrink-0" />
                            {sidebarOpen && (
                                <motion.span 
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="text-[10px] font-black uppercase tracking-[0.2em] whitespace-nowrap"
                                >
                                    {item.label}
                                </motion.span>
                            )}
                            {!sidebarOpen && (
                                <div className="absolute left-full ml-4 px-3 py-1.5 glass bg-bg-deep text-[10px] font-black uppercase tracking-widest pointer-events-none opacity-0 group-hover:opacity-100 transition-all z-[100] whitespace-nowrap">
                                    {item.label}
                                </div>
                            )}
                        </Link>
                    ))}
                </nav>

                <div className="mt-auto border-t border-white border-opacity-5 pt-6 flex flex-col gap-4">
                    <div className="flex items-center gap-4 px-2">
                        <div className="w-10 h-10 rounded-full glass border-primary border-opacity-20 flex items-center justify-center shrink-0">
                            <UserCircle size={24} className="text-primary" />
                        </div>
                        {sidebarOpen && (
                            <div className="flex flex-col overflow-hidden">
                                <span className="text-xs font-black italic uppercase truncate">Price (Admin)</span>
                                <span className="text-[9px] font-bold text-text-muted uppercase tracking-widest opacity-50 truncate">Sector 7-G</span>
                            </div>
                        )}
                    </div>
                    <button 
                        onClick={() => navigate('/')}
                        className="flex items-center gap-4 p-4 rounded-2xl text-warning hover:bg-warning hover:bg-opacity-10 transition-all"
                    >
                        <LogOut size={20} className="shrink-0" />
                        {sidebarOpen && <span className="text-[10px] font-black uppercase tracking-widest">Terminate Session</span>}
                    </button>
                </div>
            </motion.aside>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col h-screen overflow-hidden">
                {/* Topbar */}
                <header className="h-20 glass border-b border-white border-opacity-5 px-8 flex justify-between items-center z-40">
                    <div className="flex items-center gap-6">
                        <button 
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            className="p-2 hover:bg-white hover:bg-opacity-5 rounded-lg transition-all"
                        >
                            <Menu size={20} />
                        </button>
                        <div className="glass px-6 py-2 rounded-xl flex items-center gap-4 border-opacity-[0.03] hidden md:flex">
                            <Search size={16} className="text-text-muted" />
                            <input 
                                type="text" 
                                placeholder="QUERY SYSTEM..." 
                                className="bg-transparent border-none outline-none text-[10px] font-black uppercase tracking-widest text-primary placeholder-text-muted w-64"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="hidden lg:flex flex-col items-end gap-1">
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
                                <span className="text-[9px] font-black uppercase tracking-widest">Active Operatives: 124</span>
                            </div>
                            <span className="text-[8px] font-bold text-text-muted uppercase tracking-tighter italic">Last Block-Sync: 2s ago</span>
                        </div>
                        <button className="p-2.5 glass relative hover:text-primary transition-all">
                            <Bell size={18} />
                            <div className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-primary border-2 border-bg-deep rounded-full" />
                        </button>
                        <div className="h-8 w-px bg-white bg-opacity-10 mx-2" />
                        <div className="flex items-center gap-3">
                            <div className="flex flex-col items-end">
                                <span className="text-xs font-black italic uppercase">Price</span>
                                <span className="text-[9px] font-bold text-primary uppercase tracking-widest">Admin</span>
                            </div>
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary p-px">
                                <div className="w-full h-full bg-bg-deep rounded-[11px] flex items-center justify-center font-black italic">P</div>
                            </div>
                        </div>
                    </div>
                </header>

                {/* Content Area */}
                <main className="flex-1 p-8 overflow-y-auto custom-scrollbar relative">
                    <div className="absolute inset-0 pointer-events-none opacity-20 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] mix-blend-overlay" />
                    <div className="relative z-10">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
};

export default DashboardLayout;

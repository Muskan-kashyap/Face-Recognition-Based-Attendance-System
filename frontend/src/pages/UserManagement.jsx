import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { 
    Users as UsersIcon, 
    UserPlus, 
    Search, 
    MoreHorizontal, 
    Shield, 
    Clock, 
    ChevronRight,
    Edit3,
    Trash2,
    Filter
} from 'lucide-react';

const UserManagement = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                // In production, include auth header
                const res = await axios.get('http://127.0.0.1:8000/api/v1/users/');
                setUsers(res.data);
            } catch (err) {
                console.error("Failed to fetch identities:", err);
                // Fallback to mock data for demonstration if backend fails
                setUsers([
                    { id: 1, full_name: 'Captain Price', role_name: 'Admin', shift_name: 'Alpha (08:00)', org_name: 'HQ Tasks', is_active: 1 },
                    { id: 2, full_name: 'Soap MacTavish', role_name: 'Manager', shift_name: 'Bravo (09:00)', org_name: 'HQ Tasks', is_active: 1 },
                ]);
            } finally {
                setLoading(false);
            }
        };

        fetchUsers();
    }, []);

    const filteredUsers = users.filter(user => 
        user.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.username?.toLowerCase().includes(searchTerm.toLowerCase())
    );


    return (
        <div className="space-y-10">
            <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
                <div className="flex flex-col gap-1">
                    <h2 className="text-4xl font-black italic tracking-tighter uppercase">Identity Database</h2>
                    <p className="text-[10px] font-black text-text-muted tracking-[0.3em] uppercase opacity-50 italic">Total Registered Entities: {users.length}</p>
                </div>
                <div className="flex gap-4 w-full md:w-auto">
                    <div className="glass px-6 py-3 flex items-center gap-4 flex-1 md:w-80">
                        <Search size={16} className="text-text-muted" />
                        <input 
                            type="text" 
                            placeholder="SEARCH IDENTITIES..." 
                            className="bg-transparent border-none outline-none text-[10px] font-black uppercase tracking-widest text-primary placeholder-text-muted w-full"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <button className="btn-primary px-8 py-3 flex items-center gap-3 font-black italic whitespace-nowrap">
                        <UserPlus size={18} /> ADD OPERATIVE
                    </button>
                </div>
            </header>

            <div className="glass overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-white border-opacity-5">
                                <TableHead label="Identification" />
                                <TableHead label="Tactical Role" />
                                <TableHead label="Shift Assignment" />
                                <TableHead label="Organization" />
                                <TableHead label="Protocol Status" />
                                <TableHead label="Actions" align="right" />
                            </tr>
                        </thead>
                        <tbody>
                            {filteredUsers.map((user, i) => (
                                <motion.tr 
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: i * 0.05 }}
                                    key={user.id} 
                                    className="group hover:bg-white hover:bg-opacity-[0.02] transition-all border-b border-white border-opacity-[0.02]"
                                >
                                    <td className="p-6">
                                        <div className="flex items-center gap-4">
                                            <div className="w-10 h-10 rounded-xl bg-primary bg-opacity-10 flex items-center justify-center font-black italic text-primary">
                                                {user.full_name?.charAt(0)}
                                            </div>
                                            <span className="text-xs font-black uppercase tracking-tight">{user.full_name}</span>
                                        </div>
                                    </td>
                                    <td className="p-6">
                                        <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest ${user.role_name === 'Admin' ? 'bg-danger bg-opacity-10 text-danger' : user.role_name === 'Manager' ? 'bg-warning bg-opacity-10 text-warning' : 'bg-primary bg-opacity-10 text-primary'}`}>
                                            <Shield size={10} /> {user.role_name}
                                        </div>
                                    </td>
                                    <td className="p-6">
                                        <div className="flex items-center gap-2 text-text-muted">
                                            <Clock size={14} />
                                            <span className="text-[10px] font-bold uppercase tracking-widest">{user.shift_name || 'N/A'}</span>
                                        </div>
                                    </td>
                                    <td className="p-6">
                                        <span className="text-[10px] font-bold uppercase tracking-widest text-text-muted">{user.org_name || 'Global'}</span>
                                    </td>
                                    <td className="p-6">
                                        <div className="flex items-center gap-2">
                                            <div className={`w-2 h-2 rounded-full ${user.is_active ? 'bg-success shadow-[0_0_8px_var(--success)]' : 'bg-text-muted'}`} />
                                            <span className="text-[10px] font-black uppercase tracking-widest italic">{user.is_active ? 'Active' : 'Inactive'}</span>
                                        </div>
                                    </td>
                                    <td className="p-8">
                                        <div className="flex items-center justify-end gap-4">
                                            <button 
                                                onClick={() => {
                                                    setSelectedUser(user);
                                                    setEnrollModal(true);
                                                }}
                                                className="px-4 py-2 bg-primary/10 border border-primary/20 text-primary text-[10px] font-black uppercase tracking-widest hover:bg-primary hover:text-white transition-all rounded-lg"
                                            >
                                                Enroll Face
                                            </button>
                                            <MoreVertical size={16} className="text-text-muted cursor-pointer hover:text-white transition-colors" />
                                        </div>
                                    </td>
                                </motion.tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <AnimatePresence>
                {enrollModal && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
                        <motion.div 
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setEnrollModal(false)}
                            className="absolute inset-0 bg-black/80 backdrop-blur-md"
                        />
                        <motion.div 
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            className="glass w-full max-w-2xl relative p-10 overflow-hidden"
                        >
                             <div className="mb-8 border-b border-white/5 pb-6">
                                <h3 className="text-2xl font-bold italic tracking-tighter uppercase mb-1">Face Recognition Enrollment</h3>
                                <p className="text-[10px] font-black uppercase tracking-[0.3em] text-text-muted opacity-50">Identity: {selectedUser?.full_name}</p>
                             </div>

                             <div className="aspect-video bg-black rounded-2xl overflow-hidden relative mb-8 border border-white/5">
                                <Webcam
                                    audio={false}
                                    ref={webcamRef}
                                    screenshotFormat="image/jpeg"
                                    className="w-full h-full object-cover grayscale brightness-110"
                                />
                                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                    <div className="w-48 h-64 border-2 border-primary/30 border-dashed rounded-[3rem] animate-pulse" />
                                </div>
                             </div>

                             <div className="flex gap-4">
                                <button onClick={() => setEnrollModal(false)} className="glass px-8 py-4 text-xs font-black uppercase flex-1">Abort</button>
                                <button onClick={handleEnroll} disabled={loading} className="btn-primary flex-[2] py-4 text-xs font-black uppercase tracking-widest">
                                    {loading ? "PROCESSING..." : "REGISTER BIOMETRICS"}
                                </button>
                             </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
            
            <footer className="flex justify-between items-center px-4 opacity-50">
                <span className="text-[9px] font-black uppercase tracking-widest">Showing 1 to 5 of {users.length} Identities</span>
                <div className="flex gap-4">
                    <button className="glass px-4 py-2 text-[9px] font-black uppercase tracking-widest">Previous</button>
                    <button className="glass px-4 py-2 text-[9px] font-black uppercase tracking-widest text-primary border-primary border-opacity-30">Next</button>
                </div>
            </footer>
        </div>
    );
};

const TableHead = ({ label, align = 'left' }) => (
    <th className={`p-6 text-[10px] font-black uppercase tracking-[0.2em] text-text-muted italic ${align === 'right' ? 'text-right' : ''}`}>
        {label}
    </th>
);

export default UserManagement;

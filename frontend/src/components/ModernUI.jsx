import React from 'react';
import { motion } from 'framer-motion';
import { Inbox, ArrowRight, Zap } from 'lucide-react';

export const EmptyState = ({ title, message, actionText, onAction, icon: Icon = Inbox }) => (
    <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col items-center justify-center p-12 glass-panel border-dashed border-2 border-white/5 bg-transparent"
    >
        <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mb-6 text-text-dim">
            <Icon size={32} />
        </div>
        <h3 className="text-xl font-black italic uppercase tracking-tighter text-white mb-2">{title}</h3>
        <p className="text-text-muted text-xs font-medium uppercase tracking-widest text-center max-w-xs mb-8">
            {message}
        </p>
        {actionText && (
            <button 
                onClick={onAction}
                className="btn-premium btn-primary text-[10px]"
            >
                {actionText} <ArrowRight size={14} />
            </button>
        )}
    </motion.div>
);

export const SmartTooltip = ({ text, children }) => (
    <div className="group relative inline-block">
        {children}
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-primary text-white text-[10px] font-black uppercase tracking-widest rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 shadow-2xl">
            {text}
            <div className="absolute top-full left-1/2 -translate-x-1/2 border-8 border-transparent border-t-primary" />
        </div>
    </div>
);

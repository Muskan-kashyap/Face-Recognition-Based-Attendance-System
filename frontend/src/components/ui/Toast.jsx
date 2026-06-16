/**
 * Toast Notification System
 * Enterprise-grade, animated toast notifications with 4 semantic variants.
 * Usage: import { useToast, Toaster } from './Toast';
 */
import React, { createContext, useContext, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, XCircle, AlertTriangle, Info, X } from 'lucide-react';
import { cn } from '../../lib/utils';

const ToastContext = createContext(null);

const icons = {
  success: <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />,
  error:   <XCircle      className="h-5 w-5 text-red-400 shrink-0"     />,
  warning: <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0"  />,
  info:    <Info          className="h-5 w-5 text-sky-400 shrink-0"    />,
};

const styles = {
  success: 'border-emerald-500/30 bg-emerald-950/80',
  error:   'border-red-500/30    bg-red-950/80',
  warning: 'border-amber-500/30  bg-amber-950/80',
  info:    'border-sky-500/30    bg-gray-900/90',
};

let _id = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback(({ message, type = 'info', duration = 4000 }) => {
    const id = ++_id;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      {/* Portal */}
      <div
        className="fixed bottom-6 right-6 z-[9999] flex flex-col gap-3 w-full max-w-sm pointer-events-none"
        aria-live="polite"
        aria-label="Notifications"
      >
        <AnimatePresence>
          {toasts.map((toast) => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 16, scale: 0.95 }}
              animate={{ opacity: 1, y: 0,  scale: 1    }}
              exit={{    opacity: 0, y: 8,   scale: 0.95 }}
              transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
              className={cn(
                'pointer-events-auto flex items-start gap-3 px-4 py-3.5 rounded-xl border shadow-xl backdrop-blur-xl',
                styles[toast.type]
              )}
              role="alert"
            >
              {icons[toast.type]}
              <p className="text-sm font-medium text-gray-100 flex-1 leading-snug">
                {toast.message}
              </p>
              <button
                onClick={() => removeToast(toast.id)}
                className="ml-1 text-gray-500 hover:text-gray-300 transition-colors shrink-0 mt-0.5"
                aria-label="Dismiss"
              >
                <X className="h-4 w-4" />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx.addToast;
}

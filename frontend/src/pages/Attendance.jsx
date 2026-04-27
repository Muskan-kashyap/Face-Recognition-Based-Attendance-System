import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import { motion } from 'framer-motion';
import { Camera, CheckCircle2, XCircle, Clock, RefreshCw, Activity } from 'lucide-react';
import { attendanceService } from '../services/attendanceService';
import { useAuthStore } from '../store/authStore';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Spinner } from '../components/ui/Spinner';
import { formatTime, formatDate, titleCase } from '../lib/utils';

export default function Attendance() {
  const webcamRef = useRef(null);
  const [step, setStep] = useState('idle'); // idle | capturing | processing | success | fail
  const [logs, setLogs] = useState([]);
  const [cameraReady, setCameraReady] = useState(false);
  const [result, setResult] = useState(null);
  const { user } = useAuthStore();
  const timeoutRef = useRef(null);

  useEffect(() => {
    fetchLogs();
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const fetchLogs = async () => {
    try {
      const res = await attendanceService.getLogs({ limit: 10 });
      setLogs(res.data || []);
    } catch {
      // silent
    }
  };

  const reset = useCallback(() => {
    setStep('idle');
    setResult(null);
  }, []);

  const capture = useCallback(async () => {
    if (step !== 'idle') return;
    setStep('capturing');

    const imageSrc = webcamRef.current?.getScreenshot();
    if (!imageSrc) {
      setStep('idle');
      return;
    }

    setStep('processing');

    try {
      const response = await attendanceService.checkIn({
        user_id: user?.id,
        image_base64: imageSrc.split(',')[1],
        timestamp: new Date().toISOString(),
        is_live: 0,
        emotion: null,
        source: 'ai',
      });

      const data = response.data;
      setResult({
        name: user?.full_name || 'User',
        time: new Date(data.check_in).toLocaleTimeString(),
        status: data.status,
      });
      setStep('success');
      await fetchLogs();
      timeoutRef.current = setTimeout(reset, 4000);
    } catch {
      setStep('fail');
      timeoutRef.current = setTimeout(reset, 3000);
    }
  }, [step, user, reset]);

  return (
    <motion.div 
      className="space-y-6 lg:space-y-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">Biometric Kiosk</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Secure, frictionless AI attendance tracking
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Webcam Section */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="lg:col-span-2">
          <Card className="h-full border-0 overflow-hidden bg-slate-900 shadow-2xl p-0 flex flex-col">
            <div className="relative aspect-video w-full bg-black/60 rounded-t-[1.5rem] overflow-hidden">
              <Webcam
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                className="w-full h-full object-cover"
                videoConstraints={{ facingMode: 'user' }}
                onUserMedia={() => setCameraReady(true)}
                onUserMediaError={() => setCameraReady(false)}
              />

              {/* Overlay states */}
              {step === 'processing' && (
                <div className="absolute inset-0 bg-black/50 backdrop-blur-md flex flex-col items-center justify-center text-white z-10">
                  <Spinner size="xl" className="text-indigo-400" />
                  <p className="mt-4 text-sm font-medium animate-pulse">Running neural identification...</p>
                </div>
              )}

              {step === 'success' && (
                <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="absolute inset-0 bg-emerald-500/80 backdrop-blur-md flex flex-col items-center justify-center text-white z-10">
                  <CheckCircle2 className="h-20 w-20 mb-4" />
                  <p className="text-2xl font-bold tracking-tight">Identity Verified</p>
                  <p className="text-sm opacity-90 mt-2">{result?.name}</p>
                  <p className="text-xs opacity-75">{result?.time}</p>
                  <Badge className="mt-4 bg-white/20 hover:bg-white/30 text-white border-0 py-1.5 px-4 rounded-full text-sm">
                    {titleCase(result?.status)}
                  </Badge>
                </motion.div>
              )}

              {step === 'fail' && (
                <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="absolute inset-0 bg-red-600/80 backdrop-blur-md flex flex-col items-center justify-center text-white z-10">
                  <XCircle className="h-20 w-20 mb-4" />
                  <p className="text-2xl font-bold tracking-tight">Access Denied</p>
                  <p className="text-sm opacity-90 mt-2">Could not match neural template.</p>
                  <Button variant="secondary" className="mt-6 shadow-lg text-red-600 font-semibold" onClick={reset}>
                    <RefreshCw className="mr-2 h-4 w-4" /> Try Again
                  </Button>
                </motion.div>
              )}

              {/* Face Guide */}
              {step === 'idle' && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-0">
                  <div className="w-48 h-64 border-2 border-white/20 border-dashed rounded-[3rem] shadow-[0_0_0_9999px_rgba(0,0,0,0.4)]" />
                  <div className="absolute bottom-6 bg-black/60 backdrop-blur-sm text-white px-4 py-2 rounded-full text-xs font-medium border border-white/10 flex items-center gap-2">
                    <Activity className="h-3 w-3 text-emerald-400" />
                    Align face within frame
                  </div>
                </div>
              )}
            </div>

            <CardContent className="p-6 bg-slate-900 rounded-b-[1.5rem]">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-2 text-slate-400 bg-slate-800/50 px-4 py-2 rounded-lg border border-slate-700/50">
                  <Clock className="h-4 w-4" />
                  <span className="font-mono text-sm font-medium tracking-wider">{new Date().toLocaleTimeString()}</span>
                </div>
                <Button
                  onClick={capture}
                  disabled={step !== 'idle' || !cameraReady}
                  className="w-full sm:w-auto px-8 py-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-lg shadow-xl shadow-indigo-500/20 transition-all active:scale-95"
                >
                  <Camera className="mr-3 h-5 w-5" />
                  Authenticate
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Logs Sidebar */}
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}>
          <Card className="h-full flex flex-col">
            <CardHeader className="border-b border-slate-100 dark:border-slate-800 pb-4">
              <CardTitle>Live Feed</CardTitle>
              <CardDescription>Recent successful check-ins</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-0 hide-scrollbar">
              {logs.length === 0 ? (
                <div className="p-8 text-center text-slate-500">
                  <Clock className="h-8 w-8 mx-auto mb-3 opacity-20" />
                  <p className="text-sm">Awaiting activity...</p>
                </div>
              ) : (
                <div className="divide-y divide-slate-100 dark:divide-slate-800">
                  {logs.map((log) => (
                    <div key={log.id} className="p-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 flex items-center justify-center text-sm font-bold shadow-sm">
                          {(log.user_name || '?')[0].toUpperCase()}
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-slate-900 dark:text-white">{log.user_name || `User #${log.user_id}`}</p>
                          <p className="text-xs text-slate-500 dark:text-slate-400">{formatDate(log.check_in)}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge variant={log.status === 'on_time' ? 'success' : log.status === 'late' ? 'warning' : 'default'} className="mb-1">
                          {titleCase(log.status)}
                        </Badge>
                        <p className="text-[10px] font-mono text-slate-400 block">{formatTime(log.check_in)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}

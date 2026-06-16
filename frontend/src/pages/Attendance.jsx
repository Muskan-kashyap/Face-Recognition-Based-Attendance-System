/**
 * Attendance / Biometric Kiosk Page
 * Fixes: live clock (interval), consistent dark design, toast on success/fail.
 */
import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import { motion } from 'framer-motion';
import { Camera, CheckCircle2, XCircle, Clock, RefreshCw, Activity, Calendar } from 'lucide-react';
import { attendanceService } from '../services/attendanceService';
import { useAuthStore } from '../store/authStore';
import { useToast } from '../components/ui/Toast';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Spinner } from '../components/ui/Spinner';
import { formatTime, formatDate, titleCase } from '../lib/utils';

export default function Attendance() {
  const webcamRef  = useRef(null);
  const timeoutRef = useRef(null);
  const clockRef   = useRef(null);

  const [step,        setStep]        = useState('idle'); // idle | processing | success | fail
  const [logs,        setLogs]        = useState([]);
  const [cameraReady, setCameraReady] = useState(false);
  const [result,      setResult]      = useState(null);
  const [clock,       setClock]       = useState(new Date()); // ← live clock

  const { user }  = useAuthStore();
  const toast     = useToast();

  /* Live clock — updates every second */
  useEffect(() => {
    clockRef.current = setInterval(() => setClock(new Date()), 1000);
    return () => clearInterval(clockRef.current);
  }, []);

  useEffect(() => {
    fetchLogs();
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const fetchLogs = async () => {
    try {
      const res = await attendanceService.getLogs({ limit: 12 });
      setLogs(res.data || []);
    } catch { /* silent */ }
  };

  const reset = useCallback(() => {
    setStep('idle');
    setResult(null);
  }, []);

  const capture = useCallback(async () => {
    if (step !== 'idle') return;
    setStep('processing');

    const imageSrc = webcamRef.current?.getScreenshot();
    if (!imageSrc) { setStep('idle'); return; }

    try {
      const response = await attendanceService.checkIn({
        user_id:      user?.id,
        image_base64: imageSrc.split(',')[1],
        timestamp:    new Date().toISOString(),
        is_live:      0,
        emotion:      null,
        source:       'ai',
      });
      const data = response.data;
      setResult({
        name:   user?.full_name || 'User',
        time:   new Date(data.check_in).toLocaleTimeString(),
        status: data.status,
      });
      setStep('success');
      toast({
        message: `✅ Welcome, ${user?.full_name || 'User'}! Logged as ${titleCase(data.status)}.`,
        type: 'success',
        duration: 4000,
      });
      await fetchLogs();
      timeoutRef.current = setTimeout(reset, 4000);
    } catch (err) {
      setStep('fail');
      const msg = err?.response?.data?.detail || 'Face not recognized. Please try again.';
      toast({ message: msg, type: 'error' });
      timeoutRef.current = setTimeout(reset, 3000);
    }
  }, [step, user, reset, toast]);

  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Biometric Kiosk</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Secure, frictionless AI attendance tracking
          </p>
        </div>
        {/* Live clock badge */}
        <div className="flex items-center gap-2 bg-gray-800/70 border border-gray-700/50 rounded-xl px-4 py-2 self-start sm:self-auto">
          <Calendar className="h-4 w-4 text-gray-500" />
          <span className="text-sm text-gray-300 font-medium">
            {clock.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })}
          </span>
          <span className="h-3 w-px bg-gray-700 mx-1" />
          <Clock className="h-4 w-4 text-indigo-400" />
          <span className="font-mono text-sm font-semibold text-indigo-300 tracking-wide tabular-nums">
            {clock.toLocaleTimeString()}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* ── Webcam Section ───────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-2"
        >
          <Card className="overflow-hidden border-gray-800/60 bg-gray-900 p-0 flex flex-col">
            {/* Camera viewport */}
            <div className="relative aspect-video w-full bg-black rounded-t-xl overflow-hidden">
              <Webcam
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                className="w-full h-full object-cover"
                videoConstraints={{ facingMode: 'user' }}
                onUserMedia={()      => setCameraReady(true)}
                onUserMediaError={() => setCameraReady(false)}
              />

              {/* Processing overlay */}
              {step === 'processing' && (
                <div className="absolute inset-0 bg-black/60 backdrop-blur-md flex flex-col items-center justify-center text-white z-10">
                  <Spinner size="xl" className="text-indigo-400" />
                  <p className="mt-4 text-sm font-medium animate-pulse">Running neural identification…</p>
                </div>
              )}

              {/* Success overlay */}
              {step === 'success' && (
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="absolute inset-0 bg-emerald-600/85 backdrop-blur-md flex flex-col items-center justify-center text-white z-10"
                >
                  <CheckCircle2 className="h-20 w-20 mb-3 drop-shadow-xl" />
                  <p className="text-2xl font-bold tracking-tight">Identity Verified</p>
                  <p className="text-sm opacity-90 mt-1">{result?.name}</p>
                  <p className="text-xs opacity-70 mt-0.5">{result?.time}</p>
                  <Badge className="mt-3 bg-white/20 text-white border-0 py-1 px-4 text-sm">
                    {titleCase(result?.status)}
                  </Badge>
                </motion.div>
              )}

              {/* Fail overlay */}
              {step === 'fail' && (
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="absolute inset-0 bg-red-700/85 backdrop-blur-md flex flex-col items-center justify-center text-white z-10"
                >
                  <XCircle className="h-20 w-20 mb-3 drop-shadow-xl" />
                  <p className="text-2xl font-bold tracking-tight">Access Denied</p>
                  <p className="text-sm opacity-80 mt-1">Could not match neural template.</p>
                  <Button variant="secondary" className="mt-5 font-semibold" onClick={reset}>
                    <RefreshCw className="mr-2 h-4 w-4" /> Try Again
                  </Button>
                </motion.div>
              )}

              {/* Idle face guide */}
              {step === 'idle' && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="w-44 h-60 border-2 border-white/20 border-dashed rounded-[3rem] shadow-[0_0_0_9999px_rgba(0,0,0,0.35)]" />
                  <div className="absolute bottom-5 bg-black/60 backdrop-blur-sm text-white px-4 py-1.5 rounded-full text-xs font-medium border border-white/10 flex items-center gap-2">
                    <Activity className="h-3 w-3 text-emerald-400" />
                    Align face within the frame
                  </div>
                </div>
              )}
            </div>

            {/* Capture controls */}
            <CardContent className="p-5 bg-gray-900 rounded-b-xl">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                {/* Camera status */}
                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-medium
                  ${cameraReady
                    ? 'border-emerald-800/50 bg-emerald-950/40 text-emerald-400'
                    : 'border-gray-700 bg-gray-800/40 text-gray-500'}`
                }>
                  <span className={`h-2 w-2 rounded-full ${cameraReady ? 'bg-emerald-400 animate-pulse' : 'bg-gray-600'}`} />
                  {cameraReady ? 'Camera ready' : 'Waiting for camera…'}
                </div>

                <Button
                  onClick={capture}
                  disabled={step !== 'idle' || !cameraReady}
                  className="w-full sm:w-auto px-8 py-5 text-base font-semibold rounded-xl bg-indigo-600 hover:bg-indigo-500 shadow-xl shadow-indigo-500/20 active:scale-95 transition-all"
                >
                  <Camera className="mr-2 h-5 w-5" />
                  Authenticate
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* ── Live Feed Sidebar ─────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, x: 16 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="h-full flex flex-col border-gray-800/60">
            <CardHeader className="border-b border-gray-800/60 pb-4">
              <CardTitle className="text-white text-base">Live Feed</CardTitle>
              <CardDescription className="text-gray-500 text-xs">Recent successful check-ins</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-0 hide-scrollbar">
              {logs.length === 0 ? (
                <div className="p-8 text-center text-gray-600">
                  <Clock className="h-7 w-7 mx-auto mb-2 opacity-25" />
                  <p className="text-sm">Awaiting activity…</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-800/60">
                  {logs.map((log) => (
                    <div key={log.id} className="px-4 py-3 flex items-center justify-between hover:bg-gray-800/30 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="h-9 w-9 rounded-full bg-gray-800 text-gray-300 flex items-center justify-center text-sm font-bold shrink-0">
                          {(log.user_name || '?')[0].toUpperCase()}
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-white leading-tight">{log.user_name || `User #${log.user_id}`}</p>
                          <p className="text-[11px] text-gray-500 mt-0.5">{formatDate(log.check_in)}</p>
                        </div>
                      </div>
                      <div className="text-right shrink-0 ml-2">
                        <Badge variant={log.status === 'on_time' ? 'success' : log.status === 'late' ? 'warning' : 'default'}
                          className="text-[10px] px-1.5 py-0.5">
                          {titleCase(log.status)}
                        </Badge>
                        <p className="text-[10px] font-mono text-gray-500 mt-0.5 block">{formatTime(log.check_in)}</p>
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

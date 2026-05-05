import React from "react";
import { Link } from "react-router-dom";
import {
  ShieldCheck,
  Zap,
  Globe,
  Users,
  ArrowRight,
  Check,
  Cpu,
  Lock,
  LineChart,
  ChevronRight,
} from "lucide-react";
import { motion } from "framer-motion";
import { AppLayout } from "../components/layout/AppLayout";

/* ── Feature Card ───────────────────────────────────────────── */
const FeatureCard = ({ icon: Icon, title, desc, delay }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.5, delay }}
    className="p-6 rounded-2xl bg-gray-900 border border-gray-800 shadow-lg hover:scale-105 hover:border-gray-700 transition-all duration-300 group"
  >
    <div className="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
      <Icon className="text-indigo-400" size={24} />
    </div>
    <h3 className="text-xl font-semibold text-white mb-3 tracking-tight">{title}</h3>
    <p className="text-gray-400 leading-relaxed">{desc}</p>
  </motion.div>
);

/* ── Pricing Card ───────────────────────────────────────────── */
const PricingCard = ({ name, price, description, features, featured }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.5 }}
    className={`relative rounded-2xl border p-8 flex flex-col overflow-hidden transition-all duration-300 hover:scale-105 ${featured
      ? "bg-indigo-500/10 border-indigo-500 scale-105 shadow-xl shadow-indigo-500/20 z-10"
      : "bg-gray-900 border-gray-800 hover:border-gray-700 shadow-lg"
      }`}
  >
    {featured && (
      <div className="absolute top-0 right-0">
        <div className="bg-indigo-500 text-white text-xs font-bold px-3 py-1 rounded-bl-lg">
          MOST POPULAR
        </div>
      </div>
    )}
    <h3 className="text-xl font-bold text-white mb-2">{name}</h3>
    <p className="text-sm text-gray-400 mb-6">{description}</p>
    <div className="flex items-baseline gap-1 mb-8">
      <span className="text-4xl font-extrabold text-white">
        {price === "Custom" ? "Custom" : `$${price}`}
      </span>
      {price !== "Custom" && <span className="text-gray-500">/mo</span>}
    </div>
    <ul className="space-y-4 mb-8 flex-1">
      {features.map((f, i) => (
        <li key={i} className="flex items-start gap-3 text-sm text-gray-300">
          <Check className="h-5 w-5 text-indigo-400 shrink-0" />
          {f}
        </li>
      ))}
    </ul>
    <Link to="/signup" className="mt-auto">
      <button
        className={`w-full py-3 rounded-xl font-semibold transition-all duration-200 ${featured
          ? "bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/25"
          : "bg-gray-800 hover:bg-gray-700 text-white border border-gray-700"
          }`}
      >
        Get Started
      </button>
    </Link>
  </motion.div>
);

/* ── Main Landing Page ──────────────────────────────────────── */
export default function LandingPage() {
  return (
    <AppLayout>
      {/* ── Hero Section ─────────────────────────────────────── */}
      <section className="relative h-[600px] md:h-[700px] flex items-center justify-center overflow-hidden">
        {/* Background Image */}
        <img
          src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=2400"
          alt="Hero Background"
          className="absolute inset-0 w-full h-full object-cover"
        />
        {/* Overlay */}
        <div className="absolute inset-0 bg-black/60" />
        {/* Glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] bg-indigo-600/20 rounded-full blur-[120px] pointer-events-none" />

        <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Link
              to="/signup"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-sm font-medium text-indigo-300 mb-8 hover:bg-indigo-500/20 transition-colors duration-200"
            >
              <Zap className="h-4 w-4" />
              <span>VisionCore 2.0 is now live</span>
              <ChevronRight className="h-4 w-4" />
            </Link>

            <h1 className="text-5xl md:text-7xl font-bold text-white tracking-tight leading-[1.1] mb-6">
              The AI workforce platform <br className="hidden md:block" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
                built for scale.
              </span>
            </h1>

            <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
              Secure biometric attendance, automated payroll, and predictive
              workforce analytics powered by state-of-the-art liveness detection
              and blockchain trails.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/signup">
                <button className="px-8 py-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40">
                  Start Free Trial <ArrowRight size={18} />
                </button>
              </Link>
              <Link to="/login">
                <button className="px-8 py-4 rounded-xl bg-gray-800 hover:bg-gray-700 border border-gray-700 text-white font-semibold transition-all duration-200">
                  Sign In
                </button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── Features Section ─────────────────────────────────── */}
      {/* <section id="features" className="py-24 border-t border-white/5"> */}
      <section id="features" className="py-24 border-t border-white/5">
        {/* <div id="security" className="absolute -top-24" /> */}
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-6 tracking-tight">
              Enterprise-grade architecture
            </h2>
            <p className="text-lg text-gray-400">
              Everything you need to manage attendance, payroll, and tickets from
              a single pane of glass.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={Cpu}
              title="AI Biometrics"
              desc="Face recognition with advanced anti-spoofing and liveness detection powered by neural networks."
              delay={0.1}
            />
            <FeatureCard
              icon={LineChart}
              title="Real-time Analytics"
              desc="Monitor workforce productivity and predict burnout with zero-latency data streaming."
              delay={0.2}
            />
            <FeatureCard
              icon={Lock}
              title="Blockchain Audit"
              desc="Immutable cryptographic ledgers guarantee that attendance logs can never be tampered with."
              delay={0.3}
            />
            <FeatureCard
              icon={Users}
              title="Multi-tenant Org"
              desc="Easily manage multiple departments, shifts, and nested organizational structures."
              delay={0.4}
            />
            <FeatureCard
              icon={Zap}
              title="Auto Payroll"
              desc="Instantly calculate salaries, deductions, and reimbursements based on real-time clock data."
              delay={0.5}
            />
            <FeatureCard
              icon={Globe}
              title="Global Scale"
              desc="Built on edge infrastructure to deliver lightning-fast responses no matter where your team is."
              delay={0.6}
            />
          </div>
        </div>
      </section>

      {/* ── Product Preview Section ──────────────────────────── */}
      <section className="py-24 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-6 tracking-tight">
              Built for modern teams
            </h2>
            <p className="text-lg text-gray-400">
              A unified dashboard that gives you complete visibility and control.
            </p>
          </div>
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="relative mx-auto max-w-5xl"
          >
            <div className="relative rounded-2xl border border-gray-800 bg-gray-900/50 backdrop-blur-xl p-2 shadow-2xl shadow-indigo-500/10">
              <img
                src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=2400"
                alt="Dashboard Preview"
                className="rounded-xl border border-gray-800 w-full opacity-90 object-cover aspect-[16/9]"
              />
              <div className="absolute inset-0 rounded-xl ring-1 ring-inset ring-white/10 pointer-events-none" />
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── Security Section ──────────────────────────────────── */}
      <section id="security" className="py-24 border-t border-white/5 bg-indigo-500/5 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h2 className="text-3xl md:text-5xl font-bold text-white mb-6 tracking-tight">
                Privacy-first Biometrics
              </h2>
              <p className="text-lg text-gray-400 mb-8 leading-relaxed">
                We utilize decentralized identity protocols and zero-knowledge proofs.
                Biometric templates are never stored as raw data—only as irreversible cryptographic hashes
                anchored to an immutable blockchain ledger.
              </p>
              <div className="space-y-4">
                {[
                  "End-to-End Encryption (AES-256)",
                  "Blockchain-verified Audit Trails",
                  "Neural Liveness Detection",
                  "GDPR & SOC2 Compliant"
                ].map((feature, i) => (
                  <div key={i} className="flex items-center gap-3 text-gray-300">
                    <div className="h-6 w-6 rounded-full bg-indigo-500/20 flex items-center justify-center">
                      <ShieldCheck className="h-4 w-4 text-indigo-400" />
                    </div>
                    <span className="font-medium">{feature}</span>
                  </div>
                ))}
              </div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              className="relative group"
            >
              <div className="absolute inset-0 bg-indigo-500/20 blur-3xl rounded-full group-hover:bg-indigo-500/30 transition-all duration-500" />
              <img
                src="https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&q=80&w=1200"
                alt="Security Protocols"
                className="relative rounded-2xl border border-gray-800 shadow-2xl transition-transform duration-500 group-hover:rotate-1"
              />
            </motion.div>
          </div>
        </div>
      </section>


      {/* ── Pricing Section ──────────────────────────────────── */}
      <section id="pricing" className="py-24 bg-gray-900/50 border-t border-white/5 relative">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-transparent to-transparent pointer-events-none" />
        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-6 tracking-tight">
              Simple, transparent pricing
            </h2>
            <p className="text-lg text-gray-400">
              Start free and upgrade when you need to scale.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto items-center">
            <PricingCard
              name="Starter"
              price="0"
              description="For small teams getting started."
              features={[
                "Up to 10 employees",
                "Basic biometric check-in",
                "Community support",
                "Standard reporting",
              ]}
              featured={false}
            />
            <PricingCard
              name="Professional"
              price="49"
              description="For growing organizations."
              features={[
                "Up to 100 employees",
                "Liveness detection AI",
                "Priority email support",
                "Advanced analytics & payroll",
              ]}
              featured={true}
            />
            <PricingCard
              name="Enterprise"
              price="Custom"
              description="For large-scale deployments."
              features={[
                "Unlimited employees",
                "Blockchain audit logs",
                "Dedicated success manager",
                "Custom integrations",
              ]}
              featured={false}
            />
          </div>
        </div>
      </section>

      {/* ── CTA Section ──────────────────────────────────────── */}
      <section className="py-24 border-t border-white/5 relative overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-600/10 rounded-full blur-[100px] pointer-events-none" />
        <div className="max-w-4xl mx-auto text-center relative z-10 px-6">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 tracking-tight">
            Ready to transform your workforce?
          </h2>
          <p className="text-gray-400 mb-10 text-lg md:text-xl">
            Join leading companies using VisionCore to build the future of work.
          </p>
          <Link to="/signup">
            <button className="px-8 py-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold transition-all duration-200 shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40">
              Start your free trial
            </button>
          </Link>
        </div>
      </section>
    </AppLayout>
  );
}


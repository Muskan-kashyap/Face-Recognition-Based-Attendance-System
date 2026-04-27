import React, { useState } from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, Zap, Menu, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export const Navbar = () => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const navLinks = [
    { label: "Features", href: "#features" },
    { label: "Security", href: "#security" },
    { label: "Pricing", href: "#pricing" },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-gray-950/70 border-b border-white/5">
      <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center">
            <ShieldCheck className="h-5 w-5 text-white" />
          </div>
          <span className="text-white font-bold text-xl tracking-tight">VisionCore</span>
        </Link>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-400">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="hover:text-white transition-colors duration-200"
            >
              {link.label}
            </a>
          ))}
        </div>

        {/* Desktop Auth */}
        <div className="hidden md:flex items-center gap-4">
          <Link
            to="/login"
            className="text-sm font-medium text-gray-400 hover:text-white transition-colors duration-200"
          >
            Sign In
          </Link>
          <Link to="/signup">
            <button className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold transition-all duration-200 hover:shadow-[0_0_15px_rgba(99,102,241,0.5)]">
              Start Free Trial
            </button>
          </Link>
        </div>

        {/* Mobile Toggle */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden p-2 text-gray-400 hover:text-white transition-colors"
        >
          {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-white/5 bg-gray-950/95"
          >
            <div className="px-6 py-4 space-y-4">
              {navLinks.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className="block text-sm font-medium text-gray-400 hover:text-white transition-colors"
                >
                  {link.label}
                </a>
              ))}
              <div className="pt-4 border-t border-white/10 flex flex-col gap-3">
                <Link
                  to="/login"
                  onClick={() => setMobileOpen(false)}
                  className="text-sm font-medium text-gray-400 hover:text-white transition-colors"
                >
                  Sign In
                </Link>
                <Link to="/signup" onClick={() => setMobileOpen(false)}>
                  <button className="w-full px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold transition-all duration-200">
                    Start Free Trial
                  </button>
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};


import React from "react";
import { Link } from "react-router-dom";
import { ShieldCheck } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="py-12 border-t border-gray-800 bg-gray-950">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-6">
          <Link to="/" className="flex items-center gap-2">
            <div className="h-6 w-6 rounded border border-indigo-500/50 bg-indigo-500/10 flex items-center justify-center">
              <ShieldCheck className="h-3 w-3 text-indigo-400" />
            </div>
            <span className="text-white font-semibold tracking-tight">VisionCore</span>
          </Link>

          <div className="flex gap-6 text-sm text-gray-500">
            <a href="#" className="hover:text-white transition-colors duration-200">Privacy</a>
            <a href="#" className="hover:text-white transition-colors duration-200">Terms</a>
            <a href="#" className="hover:text-white transition-colors duration-200">Security</a>
          </div>

          <p className="text-sm text-gray-600">
            © 2026 VisionCore Inc. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};


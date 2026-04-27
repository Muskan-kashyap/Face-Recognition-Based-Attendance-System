import React from "react";
import { Navbar } from "./Navbar";
import { Footer } from "./Footer";

export const AppLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 font-sans">
      <Navbar />
      <main className="pt-16">{children}</main>
      <Footer />
    </div>
  );
};


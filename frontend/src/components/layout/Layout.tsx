import React from 'react';
import { Sidebar } from './Sidebar';
import { Toaster } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import { useLocation } from 'react-router-dom';

interface LayoutProps {
    children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
    const location = useLocation();

    return (
        <div className="flex h-screen bg-hsl(var(--background)) text-hsl(var(--foreground)) font-sans antialiased overflow-hidden relative transition-colors duration-500">
            {/* Background Blobs for Glassmorphism */}
            <div className="fixed top-[-10%] right-[-10%] w-[40%] h-[40%] bg-hsl(var(--primary)/0.1) rounded-full blur-[120px] pointer-events-none z-0 animate-pulse" />
            <div className="fixed bottom-[-10%] left-[20%] w-[30%] h-[30%] bg-hsl(var(--secondary)/0.1) rounded-full blur-[100px] pointer-events-none z-0 animate-pulse"
                style={{ animationDelay: '1s' }} />

            <Sidebar />

            <main className="flex-1 overflow-y-auto p-4 md:p-8 relative z-10">
                <div className="max-w-7xl mx-auto h-full">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={location.pathname}
                            initial={{ opacity: 0, y: 10, scale: 0.98 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: -10, scale: 0.98 }}
                            transition={{ duration: 0.3, ease: "easeOut" }}
                            className="h-full"
                        >
                            {children}
                        </motion.div>
                    </AnimatePresence>
                </div>
            </main>

            <Toaster position="top-right" richColors />
        </div>
    );
}

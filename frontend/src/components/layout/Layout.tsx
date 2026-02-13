import React from 'react';
import { Sidebar } from './Sidebar';
import { Toaster } from 'sonner';

interface LayoutProps {
    children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
    return (
        <div className="flex h-screen bg-slate-50 text-slate-900 font-sans antialiased overflow-hidden relative">
            {/* Background Blobs for Glassmorphism */}
            <div className="fixed top-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-400/20 rounded-full blur-[120px] pointer-events-none z-[-1]" />
            <div className="fixed bottom-[-10%] left-[20%] w-[30%] h-[30%] bg-indigo-400/20 rounded-full blur-[100px] pointer-events-none z-[-1]" />

            <Sidebar />
            <main className="flex-1 overflow-y-auto p-4 md:p-8 relative z-0">
                <div className="max-w-7xl mx-auto">
                    {children}
                </div>
            </main>
            <Toaster position="top-right" richColors />
        </div>
    );
}

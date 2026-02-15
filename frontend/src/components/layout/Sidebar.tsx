import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Briefcase, Database, MessageSquare, Settings, FileText, User } from 'lucide-react';

export function Sidebar() {
    const navItems = [
        { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { to: '/jobs', icon: Briefcase, label: 'Jobs' },
        { to: '/scrape', icon: Database, label: 'Scrapers' },
        { to: '/chat', icon: MessageSquare, label: 'Assistant' },
        { to: '/profile', icon: User, label: 'Profile' },
        { to: '/documents', icon: FileText, label: 'Documents' },
        { to: '/settings', icon: Settings, label: 'Settings' },
    ];

    return (
        <aside className="w-64 glass-dark text-white flex-shrink-0 hidden md:flex flex-col h-full border-r border-white/10 relative z-10">
            <div className="p-6">
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-300 to-cyan-200 bg-clip-text text-transparent">
                    Job Search AI
                </h1>
                <p className="text-xs text-slate-300/80 mt-1">Automated Application System</p>
            </div>

            <nav className="flex-1 px-4 space-y-1">
                {navItems.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        className={({ isActive }) =>
                            `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${isActive
                                ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50'
                                : 'text-slate-200/70 hover:bg-white/10 hover:text-white'
                            }`
                        }
                    >
                        <item.icon className="w-5 h-5 mr-3" />
                        {item.label}
                    </NavLink>
                ))}
            </nav>

            <div className="p-4 border-t border-slate-800">
                <div className="flex items-center">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-500 to-pink-500 flex items-center justify-center text-xs font-bold">
                        PL
                    </div>
                    <div className="ml-3">
                        <p className="text-sm font-medium text-white">Pratik Lad</p>
                        <p className="text-xs text-slate-400">Free Tier</p>
                    </div>
                </div>
            </div>
        </aside>
    );
}

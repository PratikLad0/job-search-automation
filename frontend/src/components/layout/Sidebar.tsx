import { NavLink } from 'react-router-dom';
import {
    LayoutDashboard, Briefcase, Database, MessageSquare, Settings,
    FileText, User, Mail, Search, Moon, Sun,
    Star, TreePine, Sunrise, Waves, CupSoda, Flower2,
    Sparkles, Circle, Ghost, Zap
} from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

export function Sidebar() {
    const { theme, setTheme } = useTheme();
    const navItems = [
        { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { to: '/emails', icon: Mail, label: 'Inbox' },
        { to: '/jobs', icon: Briefcase, label: 'Jobs' },
        { to: '/search', icon: Search, label: 'Search' },
        { to: '/scrape', icon: Database, label: 'Scrapers' },
        { to: '/chat', icon: MessageSquare, label: 'Assistant' },
        { to: '/profile', icon: User, label: 'Profile' },
        { to: '/documents', icon: FileText, label: 'Documents' },
        { to: '/settings', icon: Settings, label: 'Settings' },
    ];

    const themes: { id: any; icon: any; label: string }[] = [
        { id: 'light', icon: Sun, label: 'Light' },
        { id: 'dark', icon: Moon, label: 'Dark' },
        { id: 'cyberpunk', icon: Zap, label: 'Cyber' },
        { id: 'midnight', icon: Star, label: 'Mid' },
        { id: 'forest', icon: TreePine, label: 'Forest' },
        { id: 'sunset', icon: Sunrise, label: 'Sunset' },
        { id: 'ocean', icon: Waves, label: 'Ocean' },
        { id: 'coffee', icon: CupSoda, label: 'Coffee' },
        { id: 'sakura', icon: Flower2, label: 'Sakura' },
        { id: 'aurora', icon: Sparkles, label: 'Aurora' },
        { id: 'monochrome', icon: Circle, label: 'Mono' },
        { id: 'dracula', icon: Ghost, label: 'Drac' },
    ];

    return (
        <aside className="w-64 glass-card border-r border-hsl(var(--border)/0.2) text-hsl(var(--foreground)) flex-shrink-0 hidden md:flex flex-col h-full relative z-20 transition-all duration-500 overflow-hidden">
            <div className="p-6">
                <h1 className="text-2xl font-black text-gradient">
                    JobSearch AI
                </h1>
                <p className="text-[10px] uppercase tracking-widest text-hsl(var(--foreground)/0.4) mt-1 font-black">
                    Enterprise v1.2
                </p>
            </div>

            <nav className="flex-1 px-4 space-y-1 overflow-y-auto scrollbar-hide">
                {navItems.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        className={({ isActive }) =>
                            `flex items-center px-4 py-2.5 text-sm font-bold rounded-xl transition-all duration-300 ${isActive
                                ? 'bg-hsl(var(--primary)) text-hsl(var(--primary-foreground)) shadow-xl shadow-hsl(var(--primary)/0.2) translate-x-1'
                                : 'text-hsl(var(--foreground)/0.6) hover:bg-hsl(var(--primary)/0.1) hover:text-hsl(var(--primary))'
                            }`
                        }
                    >
                        <item.icon className="w-4 h-4 mr-3" />
                        {item.label}
                    </NavLink>
                ))}
            </nav>

            <div className="p-4 border-t border-hsl(var(--border)/0.2) space-y-6">
                {/* Theme Switcher Grid */}
                <div className="space-y-3">
                    <p className="text-[9px] font-black uppercase tracking-[0.2em] text-hsl(var(--foreground)/0.3) ml-1">
                        Systems Theme
                    </p>
                    <div className="grid grid-cols-4 gap-2 bg-hsl(var(--background)/0.5) p-2 rounded-2xl border border-hsl(var(--border)/0.2)">
                        {themes.map((t) => (
                            <button
                                key={t.id}
                                onClick={() => setTheme(t.id)}
                                className={`flex items-center justify-center py-2 rounded-lg transition-all duration-300 ${theme === t.id
                                    ? 'bg-hsl(var(--primary)) text-hsl(var(--primary-foreground)) shadow-lg'
                                    : 'text-hsl(var(--foreground)/0.4) hover:bg-hsl(var(--primary)/0.1) hover:text-hsl(var(--primary))'
                                    }`}
                                title={t.label}
                            >
                                <t.icon className="w-3.5 h-3.5" />
                            </button>
                        ))}
                    </div>
                </div>

                <div className="flex items-center px-2">
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-500 to-indigo-600 flex items-center justify-center text-xs font-bold text-white shadow-md">
                        PL
                    </div>
                    <div className="ml-3 overflow-hidden">
                        <p className="text-sm font-bold truncate">Pratik Lad</p>
                        <p className="text-[10px] text-[rgb(var(--foreground))]/50">Professional Tier</p>
                    </div>
                </div>
            </div>
        </aside>
    );
}

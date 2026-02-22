import { useState, useEffect } from 'react';
import type { Stats } from '../types';
import { statsApi } from '../api/client';
import { TrendingUp, Users, Activity, Target, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie } from 'recharts';

export default function Dashboard() {
    const [stats, setStats] = useState<Stats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadStats();
    }, []);

    const loadStats = async () => {
        try {
            const data = await statsApi.get();
            setStats(data);
        } catch (e) {
            console.error("Failed to load stats", e);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col h-full items-center justify-center text-hsl(var(--foreground)/0.5) space-y-4">
                <div className="w-12 h-12 border-4 border-hsl(var(--primary)/0.2) border-t-hsl(var(--primary)) rounded-full animate-spin" />
                <p className="animate-pulse font-medium">Analyzing your progress...</p>
            </div>
        );
    }

    const sourceData = Object.entries(stats?.by_source || {}).map(([name, value]) => ({ name, value }));
    const statusData = Object.entries(stats?.by_status || {}).map(([name, value]) => ({ name, value }));

    // Dynamic colors based on theme if possible, otherwise consistent palette
    const COLORS = [
        'hsl(var(--primary))',
        'hsl(var(--primary)/0.8)',
        'hsl(var(--primary)/0.6)',
        'hsl(var(--primary)/0.4)',
        'hsl(var(--primary)/0.2)'
    ];

    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    const item = {
        hidden: { opacity: 0, scale: 0.95 },
        show: { opacity: 1, scale: 1 }
    };

    return (
        <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="space-y-8 relative z-10"
        >
            <header className="flex justify-between items-end">
                <div>
                    <h2 className="text-4xl font-black text-gradient uppercase tracking-tight">Analytics Console</h2>
                    <p className="text-hsl(var(--foreground)/0.6) font-bold text-sm tracking-wide">Welcome back, Pratik! System pulse is stable.</p>
                </div>
                <div className="hidden md:block">
                    <button onClick={loadStats} className="px-6 py-2.5 bg-hsl(var(--primary)/0.1) text-hsl(var(--primary)) rounded-xl font-black text-xs uppercase tracking-widest hover:bg-hsl(var(--primary)/0.2) transition-all flex items-center border border-hsl(var(--primary)/0.2)">
                        <Zap className="w-4 h-4 mr-2" />
                        Sync Data
                    </button>
                </div>
            </header>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard title="Total Stream" value={stats?.total || 0} icon={Activity} delay={0.1} />
                <StatCard title="Targeted" value={stats?.by_status.applied || 0} icon={Target} delay={0.2} />
                <StatCard title="Engaged" value={stats?.by_status.interview || 0} icon={Users} delay={0.3} />
                <StatCard title="Efficiency" value={`${stats?.avg_score || 0}%`} icon={Zap} delay={0.4} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Analytics Chart */}
                <motion.div variants={item} className="lg:col-span-2 glass-card p-10 rounded-[40px] border border-hsl(var(--border)/0.1)">
                    <div className="flex items-center justify-between mb-10">
                        <div>
                            <h3 className="font-black text-2xl uppercase tracking-tighter flex items-center">
                                <TrendingUp className="w-6 h-6 mr-3 text-hsl(var(--primary))" />
                                Discovery Distribution
                            </h3>
                            <p className="text-sm font-bold text-hsl(var(--foreground)/0.4) mt-1">Platform-specific contribution to the job stream</p>
                        </div>
                    </div>

                    <div className="h-[350px] w-full">
                        {sourceData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={sourceData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.8} />
                                            <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0.1} />
                                        </linearGradient>
                                    </defs>
                                    <CartGrid vertical={false} strokeDasharray="3 3" stroke="hsl(var(--border)/0.2)" />
                                    <XAxis
                                        dataKey="name"
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: 'hsl(var(--foreground)/0.4)', fontSize: 10, fontWeight: 900 }}
                                    />
                                    <YAxis axisLine={false} tickLine={false} tick={{ fill: 'hsl(var(--foreground)/0.4)', fontSize: 10, fontWeight: 900 }} />
                                    <Tooltip
                                        cursor={{ fill: 'hsl(var(--primary)/0.03)' }}
                                        contentStyle={{
                                            backgroundColor: 'hsl(var(--popover))',
                                            borderRadius: '20px',
                                            border: '1px solid hsl(var(--border)/0.1)',
                                            boxShadow: '0 20px 50px rgba(0,0,0,0.2)',
                                            padding: '12px 16px'
                                        }}
                                        itemStyle={{ color: 'hsl(var(--foreground))', fontWeight: 900, fontSize: '12px' }}
                                        labelStyle={{ color: 'hsl(var(--foreground)/0.5)', fontWeight: 900, marginBottom: '4px', fontSize: '10px', textTransform: 'uppercase' }}
                                    />
                                    <Bar dataKey="value" fill="url(#barGradient)" radius={[12, 12, 0, 0]} barSize={45} />
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex h-full items-center justify-center text-hsl(var(--foreground)/0.2) font-black uppercase tracking-widest text-xs">
                                No discovery metrics available
                            </div>
                        )}
                    </div>
                </motion.div>

                {/* Status Distribution */}
                <motion.div variants={item} className="glass-card p-10 rounded-[40px] flex flex-col border border-hsl(var(--border)/0.1)">
                    <h3 className="font-black text-2xl uppercase tracking-tighter mb-8">Pipeline Matrix</h3>
                    <div className="flex-1 min-h-[250px] relative">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={statusData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={70}
                                    outerRadius={90}
                                    paddingAngle={10}
                                    dataKey="value"
                                    stroke="none"
                                >
                                    {statusData.map((_, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'hsl(var(--popover))',
                                        borderRadius: '20px',
                                        border: '1px solid hsl(var(--border)/0.1)',
                                        boxShadow: '0 20px 50px rgba(0,0,0,0.2)',
                                        padding: '12px 16px'
                                    }}
                                    itemStyle={{ color: 'hsl(var(--foreground))', fontWeight: 900, fontSize: '12px' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                            <div className="text-center">
                                <p className="text-4xl font-black text-hsl(var(--primary))">{stats?.total || 0}</p>
                                <p className="text-[10px] uppercase font-black tracking-widest text-hsl(var(--foreground)/0.3) mt-1">Vector Scale</p>
                            </div>
                        </div>
                    </div>
                    <div className="mt-8 grid grid-cols-2 gap-4">
                        {statusData.slice(0, 4).map((entry, index) => (
                            <div key={entry.name} className="flex items-center space-x-3 p-2 rounded-xl bg-hsl(var(--foreground)/0.02)">
                                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length].replace('hsl(', '').replace(')', '') }} />
                                <span className="text-[10px] font-black text-hsl(var(--foreground)/0.5) uppercase tracking-wider truncate">{entry.name}</span>
                            </div>
                        ))}
                    </div>
                </motion.div>
            </div>
        </motion.div>
    );
}

function StatCard({ title, value, icon: Icon, delay }: any) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay, duration: 0.5, type: 'spring' }}
            className="glass-card p-8 rounded-[32px] border border-hsl(var(--border)/0.1) flex flex-col justify-between group overflow-hidden relative"
        >
            <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:scale-125 transition-transform duration-1000 group-hover:opacity-10">
                <Icon className="w-32 h-32" />
            </div>
            <div className="p-4 rounded-2xl w-fit bg-hsl(var(--primary)/0.1) text-hsl(var(--primary)) border border-hsl(var(--primary)/0.1) group-hover:scale-110 transition-transform duration-500">
                <Icon className="w-7 h-7" />
            </div>
            <div className="mt-8">
                <p className="text-[10px] font-black text-hsl(var(--foreground)/0.3) uppercase tracking-[0.2em]">{title}</p>
                <p className="text-4xl font-black mt-2 tracking-tight">{value}</p>
            </div>
        </motion.div>
    );
}

function CartGrid({ vertical, strokeDasharray, stroke }: any) {
    return <CartesianGrid vertical={vertical} strokeDasharray={strokeDasharray} stroke={stroke} />;
}

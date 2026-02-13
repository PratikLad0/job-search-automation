import React, { useState, useEffect } from 'react';
import type { Stats } from '../types';
import { statsApi } from '../api/client';
import { BarChart3, TrendingUp, Users, CheckCircle, Briefcase, Activity } from 'lucide-react';

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
        return <div className="flex h-full items-center justify-center text-slate-500">Loading dashboard...</div>;
    }

    const sourceData = stats?.by_source || {};
    const maxSourceCount = Math.max(...Object.values(sourceData), 10);

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <header>
                <h2 className="text-3xl font-bold text-slate-900">Dashboard</h2>
                <p className="text-slate-500">Overview of your job search progress</p>
            </header>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard title="Total Jobs" value={stats?.total || 0} icon={Briefcase} color="blue" />
                <StatCard title="Applied" value={stats?.by_status.applied || 0} icon={CheckCircle} color="green" />
                <StatCard title="Interviews" value={stats?.by_status.interview || 0} icon={Users} color="purple" />
                <StatCard title="Avg Match Score" value={stats?.avg_score || 0} icon={TrendingUp} color="orange" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Application Trend / Source Chart */}
                <div className="lg:col-span-2 glass-card p-6 rounded-xl relative overflow-hidden">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="font-bold text-lg text-slate-800 flex items-center">
                            <BarChart3 className="w-5 h-5 mr-2 text-slate-500" />
                            Jobs by Source
                        </h3>
                    </div>

                    <div className="space-y-4">
                        {Object.entries(sourceData).map(([source, count]) => (
                            <div key={source} className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="capitalize font-medium text-slate-700">{source}</span>
                                    <span className="text-slate-500">{count} jobs</span>
                                </div>
                                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-blue-600 rounded-full transition-all duration-1000 ease-out"
                                        style={{ width: `${(count / maxSourceCount) * 100}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                        {Object.keys(sourceData).length === 0 && (
                            <div className="text-center text-slate-400 py-8">No data available</div>
                        )}
                    </div>
                </div>

                {/* Action Items */}
                <div className="glass-card p-6 rounded-xl relative overflow-hidden">
                    <h3 className="font-bold text-lg text-slate-800 mb-4 flex items-center">
                        <Activity className="w-5 h-5 mr-2 text-slate-500" />
                        Action Items
                    </h3>
                    <div className="space-y-4">
                        <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                            <h4 className="font-semibold text-blue-900 text-sm mb-1">Apply to Top Matches</h4>
                            <p className="text-xs text-blue-700">You have {stats?.by_status.scored || 0} scored jobs waiting for application.</p>
                        </div>
                        <div className="p-4 bg-orange-50 rounded-lg border border-orange-100">
                            <h4 className="font-semibold text-orange-900 text-sm mb-1">Follow Up</h4>
                            <p className="text-xs text-orange-700">Check status of {stats?.by_status.applied || 0} applied jobs.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatCard({ title, value, icon: Icon, color }: any) {
    const colors: any = {
        blue: "bg-blue-50 text-blue-600",
        green: "bg-green-50 text-green-600",
        purple: "bg-purple-50 text-purple-600",
        orange: "bg-orange-50 text-orange-600",
    };

    return (
        <div className="glass-card p-6 rounded-xl flex items-center">
            <div className={`p-3 rounded-lg ${colors[color] || colors.blue} mr-4`}>
                <Icon className="w-6 h-6" />
            </div>
            <div>
                <p className="text-sm font-medium text-slate-500">{title}</p>
                <p className="text-2xl font-bold text-slate-900">{value}</p>
            </div>
        </div>
    );
}

import React, { useState } from 'react';
import { api } from '../api/client';
import { toast } from 'sonner';
import { Play, Database, Search, MapPin, Loader2, Sparkles, Zap, ShieldCheck } from 'lucide-react';
import { motion } from 'framer-motion';

export default function ScrapePage() {
    const [loading, setLoading] = useState(false);
    const [source, setSource] = useState('');
    const [query, setQuery] = useState('');
    const [location, setLocation] = useState('');

    const sources = [
        { id: '', name: 'Discovery Engine (Auto)' },
        { id: 'linkedin', name: 'LinkedIn Professional' },
        { id: 'indeed', name: 'Indeed Global' },
        { id: 'naukri', name: 'Naukri India' },
        { id: 'wellfound', name: 'Wellfound (Startup)' },
        { id: 'glassdoor', name: 'Glassdoor Insights' },
    ];

    const targetLocations = [
        'Remote', 'India', 'Germany', 'USA', 'Singapore', 'Netherlands'
    ];

    const handleScrape = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await api.post('/scrapers/run', {
                source: source || null,
                query: query || null,
                location: location || null,
            });
            toast.success('Extraction sequence initiated in background!');
        } catch (error) {
            toast.error('Failed to start extraction');
        } finally {
            setLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto space-y-10"
        >
            <header className="text-center space-y-4">
                <div className="inline-flex items-center px-4 py-1.5 rounded-full bg-hsl(var(--primary)/0.1) text-hsl(var(--primary)) text-xs font-black uppercase tracking-widest border border-hsl(var(--primary)/0.2)">
                    <Sparkles className="w-3.5 h-3.5 mr-2" />
                    AI-Powered Discovery
                </div>
                <h2 className="text-5xl font-black text-gradient">Scrape Opportunities</h2>
                <p className="text-hsl(var(--foreground)/0.6) font-medium max-w-xl mx-auto">
                    Deploy intelligent agents across global job boards to find your next career move.
                </p>
            </header>

            <div className="glass-card p-10 rounded-[40px] relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-64 h-64 bg-hsl(var(--primary)/0.05) blur-[100px] rounded-full -mr-32 -mt-32" />

                <form onSubmit={handleScrape} className="relative z-10 space-y-8">
                    <div className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <FormSection label="Target Source" icon={Database}>
                                <div className="relative">
                                    <select
                                        className="w-full px-5 py-4 bg-hsl(var(--background)/0.5) border border-hsl(var(--border)/0.2) rounded-2xl text-sm font-bold outline-none cursor-pointer focus:ring-2 focus:ring-hsl(var(--primary)) transition-all appearance-none"
                                        value={source}
                                        onChange={(e) => setSource(e.target.value)}
                                    >
                                        {sources.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                                    </select>
                                    <div className="absolute right-5 top-1/2 -translate-y-1/2 pointer-events-none opacity-40">
                                        <Zap className="w-4 h-4" />
                                    </div>
                                </div>
                            </FormSection>

                            <FormSection label="Job Role / Query" icon={Search}>
                                <input
                                    type="text"
                                    placeholder="e.g. Senior Product Designer"
                                    className="w-full px-5 py-4 bg-hsl(var(--background)/0.5) border border-hsl(var(--border)/0.2) rounded-2xl text-sm font-bold outline-none focus:ring-2 focus:ring-hsl(var(--primary)) transition-all"
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                />
                            </FormSection>
                        </div>

                        <FormSection label="Preferred Location" icon={MapPin}>
                            <div className="space-y-4">
                                <input
                                    type="text"
                                    placeholder="e.g. London, Tokyo or Remote"
                                    className="w-full px-5 py-4 bg-hsl(var(--background)/0.5) border border-hsl(var(--border)/0.2) rounded-2xl text-sm font-bold outline-none focus:ring-2 focus:ring-hsl(var(--primary)) transition-all"
                                    value={location}
                                    onChange={(e) => setLocation(e.target.value)}
                                />
                                <div className="flex flex-wrap gap-2">
                                    {targetLocations.map(loc => (
                                        <button
                                            key={loc}
                                            type="button"
                                            onClick={() => setLocation(loc)}
                                            className={`text-[10px] font-black uppercase tracking-widest px-4 py-2 rounded-xl border transition-all ${location === loc
                                                ? 'bg-hsl(var(--primary)) border-hsl(var(--primary)) text-hsl(var(--primary-foreground)) shadow-lg shadow-hsl(var(--primary)/0.2)'
                                                : 'bg-hsl(var(--background)/0.5) border-hsl(var(--border)/0.2) text-hsl(var(--foreground)/0.4) hover:bg-hsl(var(--primary)/0.05) hover:text-hsl(var(--primary))'
                                                }`}
                                        >
                                            {loc}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </FormSection>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full group/btn relative overflow-hidden bg-hsl(var(--primary)) text-hsl(var(--primary-foreground)) font-black py-5 rounded-2xl transition-all hover:scale-[1.02] active:scale-95 shadow-2xl shadow-hsl(var(--primary)/0.3)"
                    >
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover/btn:translate-x-full transition-transform duration-1000" />
                        <div className="relative flex items-center justify-center gap-3">
                            {loading ? (
                                <>
                                    <Loader2 className="w-6 h-6 animate-spin" />
                                    <span>Deploying Agents...</span>
                                </>
                            ) : (
                                <>
                                    <Play className="w-5 h-5 fill-current" />
                                    <span className="uppercase tracking-[0.2em] text-sm">Initiate Discovery Sequence</span>
                                </>
                            )}
                        </div>
                    </button>
                </form>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <InfoCard
                    icon={ShieldCheck}
                    title="Anti-Bot Protocol"
                    desc="We use advanced fingerprinting and proxy rotation to ensure 99.9% uptime."
                />
                <InfoCard
                    icon={Zap}
                    title="Real-time Updates"
                    desc="Dashboard will automatically sync as soon as new matching opportunities are extracted."
                />
            </div>
        </motion.div>
    );
}

function FormSection({ label, icon: Icon, children }: any) {
    return (
        <div className="space-y-4">
            <label className="flex items-center text-xs font-black uppercase tracking-[0.15em] text-hsl(var(--foreground)/0.4) ml-1">
                <Icon className="w-4 h-4 mr-2" />
                {label}
            </label>
            {children}
        </div>
    );
}

function InfoCard({ icon: Icon, title, desc }: any) {
    return (
        <div className="glass-card p-6 rounded-3xl border border-hsl(var(--border)/0.1) flex items-start gap-4">
            <div className="p-3 bg-hsl(var(--primary)/0.1) rounded-2xl text-hsl(var(--primary))">
                <Icon className="w-5 h-5" />
            </div>
            <div>
                <h4 className="font-black text-sm uppercase tracking-wide">{title}</h4>
                <p className="text-xs text-hsl(var(--foreground)/0.5) mt-1 leading-relaxed font-medium">{desc}</p>
            </div>
        </div>
    );
}

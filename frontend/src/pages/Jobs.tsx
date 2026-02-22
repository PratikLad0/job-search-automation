import { useEffect, useState } from 'react';
import { jobsApi } from '../api/client';
import type { Job } from '../types';
import { GenerateButton } from '../components/jobs/GenerateButton';
import { Search, MapPin, Building, Calendar, Star, Filter, X, ExternalLink, RefreshCw, BarChart3 } from 'lucide-react';
import { useWebSocket } from '../context/WebSocketProvider';
import { toast } from 'sonner';
import { API_BASE_URL } from '../config';
import { motion, AnimatePresence } from 'framer-motion';

export default function JobsPage() {
    const { lastEvent } = useWebSocket();
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        query: '',
        location: '',
        status: '',
        job_type: '',
        source: ''
    });
    const [showFilters, setShowFilters] = useState(false);

    useEffect(() => {
        if (lastEvent?.type === "task_finished") {
            const taskType = lastEvent.data.task.type;
            if (["resume_generation", "cover_letter_generation", "document_generation", "scraping", "job_scoring", "bulk_scoring"].includes(taskType)) {
                toast.success(`${taskType.replace('_', ' ')} complete!`);
                loadJobs();
            } else if (taskType === "job_application") {
                if (lastEvent.data.result?.status === "success") {
                    toast.success("Successfully applied for the job!");
                } else {
                    toast.error(`Application failed: ${lastEvent.data.result?.message || 'Unknown error'}`);
                }
                loadJobs();
            }
        }
    }, [lastEvent]);

    useEffect(() => {
        const timer = setTimeout(() => {
            loadJobs();
        }, 300);
        return () => clearTimeout(timer);
    }, [filters]);

    const loadJobs = async () => {
        try {
            setLoading(true);
            const params = Object.fromEntries(
                Object.entries(filters).filter(([_, v]) => v !== '')
            );
            const data = await jobsApi.list(params);
            setJobs(data);
        } catch (e) {
            console.error("Failed to load jobs", e);
            setJobs([]);
        } finally {
            setLoading(false);
        }
    };

    const handleFilterChange = (key: string, value: string) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const handleApply = async (jobId: number) => {
        try {
            const response = await fetch(`${API_BASE_URL}/generators/${jobId}/apply`, { method: 'POST' });
            if (response.ok) toast.info("Automated application started...");
            else toast.error("Failed to start automation");
        } catch (error) {
            toast.error("Error starting automated application");
        }
    };

    const handleScore = async (jobId: number) => {
        try {
            const response = await fetch(`${API_BASE_URL}/generators/${jobId}/score`, { method: 'POST' });
            if (response.ok) toast.info("Scoring job in background...");
            else toast.error("Failed to start scoring");
        } catch (error) {
            toast.error("Error starting job scoring");
        }
    };

    const handleScoreAll = async () => {
        const unscoredCount = jobs.filter(j => j.status === 'scraped').length;
        if (unscoredCount === 0) return toast.info("No unscored jobs found.");
        try {
            const response = await fetch(`${API_BASE_URL}/generators/score_all`, { method: 'POST' });
            if (response.ok) toast.info(`Starting bulk scoring...`);
            else toast.error("Failed to start bulk scoring");
        } catch (error) {
            toast.error("Error starting bulk scoring");
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-6rem)] relative z-10">
            <header className="mb-8 flex justify-between items-end">
                <div>
                    <h2 className="text-4xl font-black text-gradient uppercase tracking-tight">Job Board</h2>
                    <p className="text-hsl(var(--foreground)/0.6) font-bold text-sm">Pipeline of potential career opportunities</p>
                </div>
                <div className="flex items-center gap-4">
                    <button
                        onClick={handleScoreAll}
                        className="hidden md:flex items-center gap-2 px-6 py-2.5 bg-hsl(var(--primary)) text-hsl(var(--primary-foreground)) rounded-xl font-black text-xs uppercase tracking-widest hover:scale-105 active:scale-95 transition-all shadow-xl shadow-hsl(var(--primary)/0.2)"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Score All
                    </button>
                    <button
                        onClick={() => setShowFilters(!showFilters)}
                        className="md:hidden glass-card p-3 rounded-xl border border-hsl(var(--border)/0.2)"
                    >
                        <Filter className="w-5 h-5" />
                    </button>
                </div>
            </header>

            <div className="flex gap-8 flex-1 overflow-hidden relative z-10">
                {/* Sidebar Filters */}
                <aside className={`
                    w-72 glass-card p-8 rounded-[32px] flex-shrink-0
                    overflow-y-auto relative z-20 border border-hsl(var(--border)/0.2)
                    ${showFilters ? 'fixed inset-0 m-4 shadow-2xl z-50' : 'hidden md:block shadow-sm'}
                `}>
                    <div className="flex justify-between items-center mb-10 md:hidden">
                        <h3 className="font-black text-2xl uppercase tracking-tighter">Refine</h3>
                        <button onClick={() => setShowFilters(false)} className="p-3 bg-hsl(var(--primary)/0.1) text-hsl(var(--primary)) rounded-2xl transition-all">
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="space-y-8">
                        <FilterSection label="Keyword" icon={Search}>
                            <input
                                type="text"
                                placeholder="Role, Company..."
                                className="w-full px-5 py-3.5 bg-hsl(var(--background)/0.5) border border-hsl(var(--border)/0.2) rounded-2xl text-sm font-bold focus:ring-2 focus:ring-hsl(var(--primary)) outline-none transition-all placeholder:text-hsl(var(--foreground)/0.2)"
                                value={filters.query}
                                onChange={(e) => handleFilterChange('query', e.target.value)}
                            />
                        </FilterSection>

                        <FilterSection label="Location" icon={MapPin}>
                            <input
                                type="text"
                                placeholder="City or Country"
                                className="w-full px-5 py-3.5 bg-hsl(var(--background)/0.5) border border-hsl(var(--border)/0.2) rounded-2xl text-sm font-bold focus:ring-2 focus:ring-hsl(var(--primary)) outline-none transition-all placeholder:text-hsl(var(--foreground)/0.2)"
                                value={filters.location}
                                onChange={(e) => handleFilterChange('location', e.target.value)}
                            />
                        </FilterSection>

                        <FilterSection label="Application Status">
                            <select
                                className="w-full px-5 py-3.5 bg-hsl(var(--background)/0.5) border border-hsl(var(--border)/0.2) rounded-2xl text-sm font-bold outline-none cursor-pointer focus:ring-2 focus:ring-hsl(var(--primary)) appearance-none"
                                value={filters.status}
                                onChange={(e) => handleFilterChange('status', e.target.value)}
                            >
                                <option value="">All Status</option>
                                <option value="scraped">Scraped</option>
                                <option value="scored">Scored</option>
                                <option value="applied">Applied</option>
                                <option value="interview">Interview</option>
                            </select>
                        </FilterSection>

                        <FilterSection label="Job Source">
                            <select
                                className="w-full px-5 py-3.5 bg-hsl(var(--background)/0.5) border border-hsl(var(--border)/0.2) rounded-2xl text-sm font-bold outline-none cursor-pointer focus:ring-2 focus:ring-hsl(var(--primary)) appearance-none"
                                value={filters.source}
                                onChange={(e) => handleFilterChange('source', e.target.value)}
                            >
                                <option value="">All Sources</option>
                                <option value="linkedin">LinkedIn</option>
                                <option value="indeed">Indeed</option>
                                <option value="naukri">Naukri</option>
                            </select>
                        </FilterSection>
                    </div>
                </aside>

                {/* Main Content */}
                <main className="flex-1 overflow-y-auto space-y-6 pr-4 scrollbar-hide pb-10">
                    <AnimatePresence mode="popLayout">
                        {loading && jobs.length === 0 ? (
                            <motion.div
                                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                                className="flex flex-col items-center justify-center h-96 text-hsl(var(--foreground)/0.3)"
                            >
                                <div className="w-12 h-12 border-4 border-hsl(var(--primary)/0.1) border-t-hsl(var(--primary)) rounded-full animate-spin mb-6" />
                                <span className="font-black uppercase tracking-widest text-xs">Syncing Discovery Stream...</span>
                            </motion.div>
                        ) : jobs.length === 0 ? (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
                                className="text-center py-32 glass-card rounded-[40px] border border-hsl(var(--border)/0.2)"
                            >
                                <Search className="w-20 h-20 text-hsl(var(--foreground)/0.05) mx-auto mb-6" />
                                <h3 className="text-3xl font-black uppercase tracking-tighter">Empty Stream</h3>
                                <p className="text-hsl(var(--foreground)/0.4) font-bold">Try broadening your discovery criteria.</p>
                            </motion.div>
                        ) : (
                            jobs.map((job, idx) => (
                                <JobCard
                                    key={job.id}
                                    job={job}
                                    index={idx}
                                    onApply={() => job.id && handleApply(job.id)}
                                    onScore={() => job.id && handleScore(job.id)}
                                    onStatusUpdate={loadJobs}
                                />
                            ))
                        )}
                    </AnimatePresence>
                </main>
            </div>
        </div>
    );
}

function FilterSection({ label, icon: Icon, children }: any) {
    return (
        <div className="space-y-4">
            <label className="flex items-center text-[10px] font-black uppercase tracking-[0.2em] text-hsl(var(--foreground)/0.4) ml-1">
                {Icon && <Icon className="w-3.5 h-3.5 mr-2 opacity-50" />}
                {label}
            </label>
            {children}
        </div>
    );
}

function JobCard({ job, index, onApply, onScore, onStatusUpdate }: any) {
    const handleStatusChange = async (newStatus: string) => {
        if (!job.id) return;
        try {
            const response = await fetch(`${API_BASE_URL}/jobs/${job.id}/status?status=${newStatus}`, { method: 'PUT' });
            if (response.ok) {
                toast.success(`Status updated to ${newStatus}`);
                onStatusUpdate?.();
            }
        } catch (e) { toast.error("Error updating status"); }
    };

    const isHighMatch = (job.match_score || 0) >= 8;

    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05, type: 'spring', damping: 20 }}
            className={`glass-card p-8 rounded-[32px] group relative overflow-hidden border border-hsl(var(--border)/0.1) ${job.status === 'cancelled' ? 'opacity-50 grayscale' : ''}`}
        >
            {isHighMatch && (
                <div className="absolute top-0 right-0 w-64 h-64 bg-hsl(var(--primary)/0.05) blur-[100px] rounded-full -mr-32 -mt-32 pointer-events-none transition-transform group-hover:scale-150 duration-1000" />
            )}

            <div className="flex flex-col md:flex-row justify-between gap-8 relative z-10">
                <div className="flex-1 space-y-6">
                    <div className="flex flex-wrap items-center gap-4">
                        <h3 className="text-3xl font-black text-hsl(var(--foreground)) group-hover:text-hsl(var(--primary)) transition-colors leading-tight">
                            <a href={job.url} target="_blank" rel="noopener noreferrer">{job.title}</a>
                        </h3>
                        {job.match_score ? (
                            <div className={`flex items-center px-4 py-1.5 rounded-full text-[10px] font-black border uppercase tracking-widest ${isHighMatch ? 'bg-hsl(var(--primary)/0.1) text-hsl(var(--primary)) border-hsl(var(--primary)/0.2)' : 'bg-hsl(var(--foreground)/0.05) text-hsl(var(--foreground)/0.4) border-hsl(var(--border)/0.2)'
                                }`}>
                                <Star className={`w-3.5 h-3.5 mr-2 ${isHighMatch ? 'fill-hsl(var(--primary))' : ''}`} />
                                {job.match_score.toFixed(1)} Match
                            </div>
                        ) : (
                            <button onClick={onScore} className="text-[10px] font-black uppercase tracking-widest text-hsl(var(--primary)) hover:bg-hsl(var(--primary)/0.1) px-3 py-1 rounded-lg transition-all flex items-center">
                                <BarChart3 className="w-3.5 h-3.5 mr-2" /> Score Required
                            </button>
                        )}
                        <span className="px-4 py-1.5 rounded-full text-[10px] font-black bg-hsl(var(--foreground)/0.05) text-hsl(var(--foreground)/0.4) border border-hsl(var(--border)/0.2) uppercase tracking-widest">
                            {job.source}
                        </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-y-3 gap-x-8 text-hsl(var(--foreground)/0.5) font-bold text-xs">
                        <div className="flex items-center group/meta hover:text-hsl(var(--foreground)) transition-colors"><Building className="w-4 h-4 mr-2.5 opacity-30 group-hover/meta:opacity-100 transition-opacity" /> {job.company}</div>
                        <div className="flex items-center group/meta hover:text-hsl(var(--foreground)) transition-colors"><MapPin className="w-4 h-4 mr-2.5 opacity-30 group-hover/meta:opacity-100 transition-opacity" /> {job.location || 'Remote'}</div>
                        <div className="flex items-center group/meta hover:text-hsl(var(--foreground)) transition-colors"><Calendar className="w-4 h-4 mr-2.5 opacity-30 group-hover/meta:opacity-100 transition-opacity" /> {job.posted_date || 'New'}</div>
                    </div>
                </div>

                <div className="flex flex-wrap md:flex-col gap-3 min-w-[180px]">
                    <button
                        onClick={() => job.resume_path ? onApply?.() : toast.error("Generate documents first")}
                        disabled={job.status === 'applied' || job.status === 'cancelled'}
                        className={`w-full py-4 rounded-2xl text-xs font-black uppercase tracking-[0.2em] transition-all relative overflow-hidden group/btn ${job.status === 'applied'
                            ? 'bg-hsl(var(--primary)/0.1) text-hsl(var(--primary)) cursor-default'
                            : 'bg-hsl(var(--primary)) text-hsl(var(--primary-foreground)) shadow-2xl shadow-hsl(var(--primary)/0.3) hover:scale-[1.02] active:scale-95'
                            }`}
                    >
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover/btn:translate-x-full transition-transform duration-700" />
                        <span className="relative">{job.status === 'applied' ? 'Applied √' : 'Auto Apply'}</span>
                    </button>

                    <div className="grid grid-cols-2 gap-2 w-full">
                        <a href={job.url} target="_blank" className="flex items-center justify-center py-3 rounded-xl border border-hsl(var(--border)/0.2) hover:bg-hsl(var(--primary)/0.1) hover:text-hsl(var(--primary)) hover:border-hsl(var(--primary)/0.2) transition-all">
                            <ExternalLink className="w-4 h-4" />
                        </a>
                        <GenerateButton
                            jobId={job.id || 0}
                            status={job.status}
                            resumePath={job.resume_path}
                            coverLetterPath={job.cover_letter_path}
                        />
                    </div>
                </div>
            </div>

            <div className="mt-8 flex flex-wrap gap-4 items-center justify-between border-t border-hsl(var(--border)/0.1) pt-6">
                <div className="flex items-center gap-4">
                    <span className="text-[10px] font-black text-hsl(var(--foreground)/0.3) uppercase tracking-widest">Pipeline Matrix</span>
                    <select
                        value={job.status}
                        onChange={(e) => handleStatusChange(e.target.value)}
                        className="text-[10px] font-black uppercase bg-hsl(var(--primary)/0.1) text-hsl(var(--primary)) px-4 py-2 rounded-xl outline-none cursor-pointer border border-hsl(var(--primary)/0.2) hover:bg-hsl(var(--primary)/0.2) transition-all appearance-none text-center min-w-[120px]"
                    >
                        <option value="scraped">Discovery</option>
                        <option value="scored">Qualified</option>
                        <option value="applied">Targeted</option>
                        <option value="interview">Engaged</option>
                        <option value="cancelled">Paused</option>
                    </select>
                </div>
                {job.salary_text && (
                    <div className="text-[11px] font-black text-hsl(var(--primary)) bg-hsl(var(--primary)/0.05) px-5 py-2.5 rounded-2xl border border-hsl(var(--primary)/0.2) shadow-sm">
                        EST. <span className="text-hsl(var(--foreground)) ml-1">{job.salary_text}</span>
                    </div>
                )}
            </div>
        </motion.div>
    );
}

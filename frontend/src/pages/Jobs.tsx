import { useEffect, useState } from 'react';
import { jobsApi } from '../api/client';
import type { Job } from '../types';
import { GenerateButton } from '../components/jobs/GenerateButton';
import { Search, MapPin, Building, Calendar, Star, Filter, X, ExternalLink, RefreshCw, BarChart3 } from 'lucide-react';
import { useWebSocket } from '../context/WebSocketProvider';
import { toast } from 'sonner';
import { API_BASE_URL } from '../config';

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

    // Listen for background job updates from WebSocket
    useEffect(() => {
        if (lastEvent?.type === "task_finished") {
            const taskType = lastEvent.data.task.type;

            if (taskType === "resume_generation") {
                toast.success("Resume generated successfully!");
                loadJobs(); // Refresh the list to get new paths
            } else if (taskType === "cover_letter_generation") {
                toast.success("Cover letter generated successfully!");
                loadJobs(); // Refresh the list to get new paths
            } else if (taskType === "document_generation") {
                toast.success("Documents generated successfully!");
                loadJobs(); // Refresh the list to get new paths
            } else if (taskType === "scraping") {
                toast.success("Job scraping complete!");
                loadJobs(); // Refresh the list
            } else if (taskType === "job_application") {
                if (lastEvent.data.result?.status === "success") {
                    toast.success("Successfully applied for the job!");
                } else {
                    toast.error(`Application failed: ${lastEvent.data.result?.message || 'Unknown error'}`);
                }
                loadJobs();
            } else if (taskType === "job_scoring") {
                toast.success("Job scored successfully!");
                loadJobs();
            } else if (taskType === "bulk_scoring") {
                toast.success(lastEvent.data.result?.message || "Bulk scoring complete!");
                loadJobs();
            }
        }
    }, [lastEvent]);

    useEffect(() => {
        const timer = setTimeout(() => {
            loadJobs();
        }, 300); // Debounce
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
            const response = await fetch(`${API_BASE_URL}/generators/${jobId}/apply`, {
                method: 'POST',
            });
            if (response.ok) {
                toast.info("Automated application started in background...");
            } else {
                const data = await response.json();
                toast.error(data.detail || "Failed to start automation");
            }
        } catch (error) {
            console.error(error);
            toast.error("Error starting automated application");
        }
    };

    const handleScore = async (jobId: number) => {
        try {
            const response = await fetch(`${API_BASE_URL}/generators/${jobId}/score`, {
                method: 'POST',
            });
            if (response.ok) {
                toast.info("Scoring job in background...");
            } else {
                const data = await response.json();
                toast.error(data.detail || "Failed to start scoring");
            }
        } catch (error) {
            console.error(error);
            toast.error("Error starting job scoring");
        }
    };

    const handleScoreAll = async () => {
        const unscoredCount = jobs.filter(j => j.status === 'scraped').length;
        if (unscoredCount === 0) {
            toast.info("No unscored jobs found.");
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/generators/score_all`, {
                method: 'POST',
            });
            if (response.ok) {
                toast.info(`Starting bulk scoring for ${unscoredCount} jobs...`);
            } else {
                toast.error("Failed to start bulk scoring");
            }
        } catch (error) {
            console.error(error);
            toast.error("Error starting bulk scoring");
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-6rem)]">
            <header className="mb-6 flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold text-slate-900">Job Board</h2>
                    <p className="text-slate-500">Find and track your ideal positions</p>
                </div>
                <button
                    onClick={() => setShowFilters(!showFilters)}
                    className="md:hidden bg-white border border-slate-200 p-2 rounded-lg shadow-sm"
                >
                    <Filter className="w-5 h-5 text-slate-600" />
                </button>
            </header>

            <div className="flex gap-6 flex-1 overflow-hidden">
                {/* Sidebar Filters */}
                <aside className={`
                    w-64 bg-white p-5 rounded-xl border border-slate-100 flex-shrink-0
                    overflow-y-auto shadow-sm
                    ${showFilters ? 'absolute inset-0 z-50 md:static' : 'hidden md:block'}
                `}>
                    <div className="flex justify-between items-center mb-4 md:hidden">
                        <h3 className="font-bold text-lg">Filters</h3>
                        <button onClick={() => setShowFilters(false)} className="p-1 hover:bg-slate-100 rounded-full transition-colors">
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">Search</label>
                            <div className="relative">
                                <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                                <input
                                    type="text"
                                    placeholder="Role, Company..."
                                    className="w-full pl-9 pr-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                                    value={filters.query}
                                    onChange={(e) => handleFilterChange('query', e.target.value)}
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">Location</label>
                            <div className="relative">
                                <MapPin className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                                <input
                                    type="text"
                                    placeholder="City or Country"
                                    className="w-full pl-9 pr-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                                    value={filters.location}
                                    onChange={(e) => handleFilterChange('location', e.target.value)}
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">Status</label>
                            <select
                                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none bg-white cursor-pointer"
                                value={filters.status}
                                onChange={(e) => handleFilterChange('status', e.target.value)}
                            >
                                <option value="">All Status</option>
                                <option value="scraped">Scraped</option>
                                <option value="scored">Scored</option>
                                <option value="applied">Applied</option>
                                <option value="interview">Interview</option>
                                <option value="offer">Offer</option>
                                <option value="rejected">Rejected</option>
                                <option value="cancelled">Cancelled</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">Job Type</label>
                            <select
                                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none bg-white cursor-pointer"
                                value={filters.job_type}
                                onChange={(e) => handleFilterChange('job_type', e.target.value)}
                            >
                                <option value="">Any Type</option>
                                <option value="remote">Remote</option>
                                <option value="hybrid">Hybrid</option>
                                <option value="onsite">On-site</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">Job Source</label>
                            <select
                                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none bg-white cursor-pointer"
                                value={filters.source}
                                onChange={(e) => handleFilterChange('source', e.target.value)}
                            >
                                <option value="">All Sources</option>
                                <option value="linkedin">LinkedIn</option>
                                <option value="indeed">Indeed</option>
                                <option value="naukri">Naukri</option>
                                <option value="adzuna">Adzuna</option>
                                <option value="findwork">Findwork</option>
                                <option value="instahyre">Instahyre</option>
                                <option value="wellfound">Wellfound</option>
                                <option value="glassdoor">Glassdoor</option>
                            </select>
                        </div>

                        <div className="pt-4 border-t border-slate-100">
                            <button
                                onClick={handleScoreAll}
                                className="w-full py-2.5 px-4 bg-slate-900 text-white rounded-lg text-sm font-semibold hover:bg-slate-800 transition-colors flex items-center justify-center gap-2 shadow-sm"
                            >
                                <RefreshCw className="w-4 h-4" />
                                Rate All Unscored
                            </button>
                        </div>
                    </div>
                </aside>

                {/* Main Content */}
                <main className="flex-1 overflow-y-auto space-y-4 pr-1">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center h-64 text-slate-400">
                            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mb-4"></div>
                            <span className="font-medium">Searching for opportunities...</span>
                        </div>
                    ) : jobs.length === 0 ? (
                        <div className="text-center py-20 bg-white rounded-xl border border-slate-100 shadow-sm">
                            <Search className="w-16 h-16 text-slate-200 mx-auto mb-4" />
                            <h3 className="text-xl font-semibold text-slate-900">No jobs found</h3>
                            <p className="text-slate-500 mt-1">Try adjusting your filters or keywords</p>
                        </div>
                    ) : (
                        jobs.map(job => (
                            <JobCard
                                key={job.id}
                                job={job}
                                onApply={() => job.id && handleApply(job.id)}
                                onScore={() => job.id && handleScore(job.id)}
                                onStatusUpdate={loadJobs}
                            />
                        ))
                    )}
                </main>
            </div>
        </div>
    );
}

function JobCard({ job, onApply, onScore, onStatusUpdate }: { job: Job, onApply?: () => void, onScore?: () => void, onStatusUpdate?: () => void }) {
    const handleStatusChange = async (newStatus: string) => {
        if (!job.id) return;
        try {
            const response = await fetch(`${API_BASE_URL}/jobs/${job.id}/status?status=${newStatus}`, { // Using query param as per API update
                method: 'PUT',
            });
            if (response.ok) {
                toast.success(`Status updated to ${newStatus}`);
                onStatusUpdate?.(); // Refresh list
            } else {
                toast.error("Failed to update status");
            }
        } catch (e) {
            console.error(e);
            toast.error("Error updating status");
        }
    };

    const scoreColor = (job.match_score || 0) >= 8 ? 'text-green-600 bg-green-50 border-green-100' :
        (job.match_score || 0) >= 6 ? 'text-yellow-600 bg-yellow-50 border-yellow-100' :
            'text-slate-600 bg-slate-50 border-slate-100';

    return (
        <div className={`bg-white p-6 rounded-xl shadow-sm border border-slate-100 hover:shadow-md hover:border-blue-100 transition-all duration-300 group ${job.status === 'cancelled' ? 'opacity-60' : ''}`}>
            <div className="flex justify-between items-start">
                <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                        <h3 className={`font-bold text-xl text-slate-900 group-hover:text-blue-600 transition-colors truncate ${job.status === 'cancelled' ? 'line-through text-slate-400' : ''}`}>
                            <a href={job.url} target="_blank" rel="noopener noreferrer">{job.title}</a>
                        </h3>
                        {job.match_score && (
                            <span className={`px-2 py-0.5 rounded-full text-xs font-bold flex items-center border ${scoreColor}`}>
                                <Star className="w-3 h-3 mr-1 fill-current" />
                                {job.match_score.toFixed(1)}/10
                            </span>
                        )}

                        {/* Status Dropdown */}
                        <select
                            value={job.status}
                            onChange={(e) => handleStatusChange(e.target.value)}
                            className={`px-2 py-0.5 rounded-full text-xs font-medium border capitalize cursor-pointer outline-none focus:ring-1 focus:ring-blue-500 ${job.status === 'applied' ? 'border-green-200 text-green-700 bg-green-50' :
                                    job.status === 'interview' ? 'border-blue-200 text-blue-700 bg-blue-50' :
                                        job.status === 'rejected' ? 'border-red-200 text-red-700 bg-red-50' :
                                            job.status === 'offer' ? 'border-purple-200 text-purple-700 bg-purple-50' :
                                                job.status === 'cancelled' ? 'border-slate-200 text-slate-500 bg-slate-100' :
                                                    'border-slate-200 text-slate-600 bg-slate-50'
                                }`}
                        >
                            <option value="scraped">Scraped</option>
                            <option value="scored">Scored</option>
                            <option value="resume_generated">Resume Generated</option>
                            <option value="applied">Applied</option>
                            <option value="interview">Interview</option>
                            <option value="offer">Offer</option>
                            <option value="rejected">Rejected</option>
                            <option value="cancelled">Cancelled</option>
                        </select>

                        {job.source && (
                            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200 uppercase tracking-wider">
                                {job.source}
                            </span>
                        )}
                    </div>
                    <div className="flex flex-wrap items-center text-slate-500 text-sm gap-y-2 gap-x-5">
                        <span className="flex items-center"><Building className="w-4 h-4 mr-1.5 text-slate-400" /> {job.company}</span>
                        <span className="flex items-center"><MapPin className="w-4 h-4 mr-1.5 text-slate-400" /> {job.location || 'Remote'}</span>
                        <span className="flex items-center capitalize"><Calendar className="w-4 h-4 mr-1.5 text-slate-400" /> {job.posted_date || 'Recently'}</span>
                    </div>
                </div>
                <div className="flex flex-col gap-2 ml-4">
                    <button
                        onClick={() => job.resume_path ? onApply?.() : toast.error("Generate resume first")}
                        disabled={job.status === 'applied' || job.status === 'cancelled'}
                        className={`px-5 py-2.5 rounded-lg text-sm font-semibold transition-all shadow-sm text-center active:scale-95 ${job.status === 'applied' || job.status === 'cancelled'
                            ? 'bg-slate-100 text-slate-400 cursor-default shadow-none'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                            }`}
                    >
                        {job.status === 'applied' ? 'Applied' : job.status === 'cancelled' ? 'Cancelled' : 'Auto Apply'}
                    </button>
                    <a
                        href={job.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-5 py-2.5 rounded-lg text-sm font-semibold transition-all border border-slate-200 text-slate-600 hover:bg-slate-50 text-center active:scale-95 flex items-center justify-center gap-1.5"
                    >
                        <ExternalLink className="w-3.5 h-3.5" />
                        Manual Apply
                    </a>
                    {!job.match_score && (
                        <button
                            onClick={onScore}
                            className="px-5 py-2.5 rounded-lg text-sm font-semibold transition-all border border-blue-200 text-blue-600 hover:bg-blue-50 text-center active:scale-95 flex items-center justify-center gap-1.5"
                        >
                            <BarChart3 className="w-3.5 h-3.5" />
                            Score Job
                        </button>
                    )}
                    <GenerateButton
                        jobId={job.id || 0}
                        status={job.status}
                        resumePath={job.resume_path}
                        coverLetterPath={job.cover_letter_path}
                    />
                </div>
            </div>
            {job.salary_text && (
                <div className="mt-4 text-sm font-medium text-slate-700 bg-slate-50 inline-flex items-center px-3 py-1.5 rounded-lg border border-slate-100">
                    <span className="mr-1.5">💰</span> {job.salary_text}
                </div>
            )}
        </div>
    );
}

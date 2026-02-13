import { useEffect, useState } from 'react';
import { jobsApi } from '../api/client';
import type { Job } from '../types';
import { GenerateButton } from '../components/jobs/GenerateButton';
import { Search, MapPin, Building, Calendar, Star, Filter, X } from 'lucide-react';
import { useWebSocket } from '../context/WebSocketProvider';
import { toast } from 'sonner';

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
                                <option value="rejected">Rejected</option>
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
                            <JobCard key={job.id} job={job} />
                        ))
                    )}
                </main>
            </div>
        </div>
    );
}

function JobCard({ job }: { job: Job }) {
    const scoreColor = (job.match_score || 0) >= 8 ? 'text-green-600 bg-green-50 border-green-100' :
        (job.match_score || 0) >= 6 ? 'text-yellow-600 bg-yellow-50 border-yellow-100' :
            'text-slate-600 bg-slate-50 border-slate-100';

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 hover:shadow-md hover:border-blue-100 transition-all duration-300 group">
            <div className="flex justify-between items-start">
                <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                        <h3 className="font-bold text-xl text-slate-900 group-hover:text-blue-600 transition-colors truncate">
                            <a href={job.url} target="_blank" rel="noopener noreferrer">{job.title}</a>
                        </h3>
                        {job.match_score && (
                            <span className={`px-2 py-0.5 rounded-full text-xs font-bold flex items-center border ${scoreColor}`}>
                                <Star className="w-3 h-3 mr-1 fill-current" />
                                {job.match_score.toFixed(1)}/10
                            </span>
                        )}
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium border capitalize ${job.status === 'applied' ? 'border-green-200 text-green-700 bg-green-50' :
                            job.status === 'interview' ? 'border-blue-200 text-blue-700 bg-blue-50' :
                                'border-slate-200 text-slate-600 bg-slate-50'
                            }`}>
                            {job.status}
                        </span>
                    </div>
                    <div className="flex flex-wrap items-center text-slate-500 text-sm gap-y-2 gap-x-5">
                        <span className="flex items-center"><Building className="w-4 h-4 mr-1.5 text-slate-400" /> {job.company}</span>
                        <span className="flex items-center"><MapPin className="w-4 h-4 mr-1.5 text-slate-400" /> {job.location || 'Remote'}</span>
                        <span className="flex items-center capitalize"><Calendar className="w-4 h-4 mr-1.5 text-slate-400" /> {job.posted_date || 'Recently'}</span>
                    </div>
                </div>
                <div className="flex flex-col gap-2 ml-4">
                    <a
                        href={job.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="bg-blue-600 text-white px-5 py-2.5 rounded-lg text-sm font-semibold hover:bg-blue-700 transition-all shadow-sm text-center active:scale-95"
                    >
                        Apply Now
                    </a>
                    <GenerateButton
                        jobId={job.id}
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

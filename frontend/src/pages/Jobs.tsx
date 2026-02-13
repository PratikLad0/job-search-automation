import { useEffect, useState } from 'react';
import { jobsApi } from '../api/client';
import type { Job } from '../types';
import { GenerateButton } from '../components/jobs/GenerateButton';
import { Search, MapPin, Building, Calendar, Star, Filter, X } from 'lucide-react';

export default function JobsPage() {
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
            // Fallback mock
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
                    className="md:hidden bg-white border border-slate-200 p-2 rounded-lg"
                >
                    <Filter className="w-5 h-5 text-slate-600" />
                </button>
            </header>

            <div className="flex gap-6 flex-1 overflow-hidden">
                {/* Sidebar Filters */}
                <aside className={`
                    w-64 bg-white p-5 rounded-xl border border-slate-100 flex-shrink-0
                    overflow-y-auto
                    ${showFilters ? 'absolute inset-0 z-50 md:static' : 'hidden md:block'}
                `}>
                    <div className="flex justify-between items-center mb-4 md:hidden">
                        <h3 className="font-bold text-lg">Filters</h3>
                        <button onClick={() => setShowFilters(false)}><X className="w-5 h-5" /></button>
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
                                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none bg-white"
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
                                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none bg-white"
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
                            <label className="block text-sm font-medium text-slate-700 mb-2">Source</label>
                            <select
                                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none bg-white"
                                value={filters.source}
                                onChange={(e) => handleFilterChange('source', e.target.value)}
                            >
                                <option value="">All Sources</option>
                                <option value="linkedin">LinkedIn</option>
                                <option value="indeed">Indeed</option>
                                <option value="naukri">Naukri</option>
                                <option value="arbeitnow">ArbeitNow</option>
                                <option value="jobicy">Jobicy</option>
                                <option value="hn_hiring">HackerNews Hiring</option>
                                <option value="glassdoor">Glassdoor</option>
                                <option value="wellfound">Wellfound</option>
                                <option value="weworkremotely">We Work Remotely</option>
                                <option value="findwork">FindWork</option>
                                <option value="adzuna">Adzuna</option>
                                <option value="greenhouse">Greenhouse</option>
                            </select>
                        </div>
                    </div>
                </aside>

                {/* Main Content */}
                <main className="flex-1 overflow-y-auto space-y-4 pr-1">
                    {loading ? (
                        <div className="flex items-center justify-center h-64 text-slate-500">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-3"></div>
                            Loading jobs...
                        </div>
                    ) : jobs.length === 0 ? (
                        <div className="text-center py-12 bg-white rounded-xl border border-slate-100">
                            <Search className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                            <h3 className="text-lg font-medium text-slate-900">No jobs found</h3>
                            <p className="text-slate-500">Try adjusting your filters</p>
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
    const scoreColor = (job.match_score || 0) >= 8 ? 'text-green-600 bg-green-50' : (job.match_score || 0) >= 6 ? 'text-yellow-600 bg-yellow-50' : 'text-slate-600 bg-slate-50';

    return (
        <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-100 hover:shadow-md transition-all duration-200 group">
            <div className="flex justify-between items-start">
                <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-1">
                        <h3 className="font-bold text-lg text-slate-900 group-hover:text-blue-600 transition-colors">
                            <a href={job.url} target="_blank" rel="noopener noreferrer">{job.title}</a>
                        </h3>
                        {job.match_score && (
                            <span className={`px-2 py-0.5 rounded text-xs font-bold flex items-center ${scoreColor}`}>
                                <Star className="w-3 h-3 mr-1" />
                                {job.match_score}/10
                            </span>
                        )}
                        <span className={`px-2 py-0.5 rounded text-xs border ${job.status === 'applied' ? 'border-green-200 text-green-700 bg-green-50' : 'border-slate-200 text-slate-600'}`}>
                            {job.status}
                        </span>
                    </div>
                    <div className="flex items-center text-slate-500 text-sm space-x-4 mt-2">
                        <span className="flex items-center"><Building className="w-4 h-4 mr-1.5" /> {job.company}</span>
                        <span className="flex items-center"><MapPin className="w-4 h-4 mr-1.5" /> {job.location || 'Remote'}</span>
                        <span className="flex items-center capitalize"><Calendar className="w-4 h-4 mr-1.5" /> {job.posted_date || 'Recently'}</span>
                    </div>
                </div>
                <div className="flex flex-col space-y-2">
                    <button className="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors shadow-sm">
                        Apply Now
                    </button>
                    <GenerateButton
                        jobId={job.id}
                        status={job.status}
                        resumePath={job.resume_path}
                        coverLetterPath={job.cover_letter_path}
                    />
                </div>
            </div>
            {job.salary_text && (
                <div className="mt-3 text-sm text-slate-600 bg-slate-50 inline-block px-2 py-1 rounded">
                    💰 {job.salary_text}
                </div>
            )}
        </div>
    );
}

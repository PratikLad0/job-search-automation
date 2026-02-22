
import React, { useState } from 'react';
import { Search, MapPin, Building, Globe, Briefcase, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import type { Job } from '../types';
import { API_BASE_URL } from '../config';

export default function CompanySearchPage() {
    const [company, setCompany] = useState('');
    const [locations, setLocations] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [results, setResults] = useState<Job[]>([]);
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!company.trim()) return;

        setIsLoading(true);
        setError('');
        setMessage('');
        setResults([]);

        try {
            const locList = locations.split(',').map(l => l.trim()).filter(l => l);
            const response = await fetch(`${API_BASE_URL}/company/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    company_name: company,
                    locations: locList.length > 0 ? locList : [], // Empty means general search (handled by backend)
                    user_id: 1 // TODO: Get from context/auth
                })
            });

            if (!response.ok) {
                throw new Error('Search failed');
            }

            const data = await response.json();
            setResults(data.jobs || []);
            setMessage(data.message || 'Search completed');
        } catch (err) {
            setError('Failed to search jobs. Please try again.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            <header className="mb-8">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                    Company Search
                </h1>
                <p className="text-slate-400 mt-2">
                    Directly crawl company career pages using AI to find relevant roles.
                </p>
            </header>

            {/* Search Form */}
            <div className="bg-slate-800/90 backdrop-blur-xl border border-slate-700 rounded-xl p-6 shadow-xl">
                <form onSubmit={handleSearch} className="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
                    <div className="md:col-span-4 space-y-2">
                        <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                            <Building className="w-4 h-4 text-blue-400" />
                            Company Name
                        </label>
                        <input
                            type="text"
                            value={company}
                            onChange={(e) => setCompany(e.target.value)}
                            placeholder="e.g. Anthropic, Google"
                            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all outline-none"
                            required
                        />
                    </div>

                    <div className="md:col-span-6 space-y-2">
                        <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                            <MapPin className="w-4 h-4 text-purple-400" />
                            Locations (comma separated)
                        </label>
                        <input
                            type="text"
                            value={locations}
                            onChange={(e) => setLocations(e.target.value)}
                            placeholder="e.g. Remote, San Francisco, London (Leave empty for general search)"
                            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all outline-none"
                        />
                    </div>

                    <div className="md:col-span-2">
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 px-6 rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-900/20"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Scanning...
                                </>
                            ) : (
                                <>
                                    <Search className="w-5 h-5" />
                                    Search Jobs
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>

            {/* Results */}
            <div className="space-y-4">
                {error && (
                    <div className="bg-red-500/10 border border-red-500/20 text-red-200 p-4 rounded-lg flex items-center gap-3">
                        <AlertCircle className="w-5 h-5" />
                        {error}
                    </div>
                )}

                {message && !isLoading && !error && (
                    <div className="bg-green-500/10 border border-green-500/20 text-green-200 p-4 rounded-lg flex items-center gap-3">
                        <CheckCircle className="w-5 h-5" />
                        {message}
                    </div>
                )}

                {results.length > 0 && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {results.map((job, idx) => (
                            <div key={idx} className="bg-slate-800/90 border border-slate-700 rounded-xl p-5 hover:border-slate-600 transition-all group relative overflow-hidden shadow-lg">
                                <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-blue-500/10 to-transparent rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110" />

                                <div className="space-y-4 relative z-10">
                                    <div>
                                        <h3 className="font-semibold text-lg text-white group-hover:text-blue-300 transition-colors line-clamp-1" title={job.title}>
                                            {job.title}
                                        </h3>
                                        <div className="flex items-center gap-2 text-slate-300 text-sm mt-1">
                                            <Building className="w-3 h-3" />
                                            {job.company}
                                        </div>
                                    </div>

                                    <div className="flex flex-wrap gap-2">
                                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-700 text-xs text-slate-200 border border-slate-600">
                                            <MapPin className="w-3 h-3" />
                                            {job.location}
                                        </span>
                                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-700 text-xs text-slate-200 border border-slate-600">
                                            <Globe className="w-3 h-3" />
                                            {job.source}
                                        </span>
                                    </div>

                                    {job.description && (
                                        <p className="text-xs text-slate-300 line-clamp-3">
                                            {job.description}
                                        </p>
                                    )}

                                    <div className="pt-2 flex justify-between items-center">
                                        <span className="text-xs text-slate-400">
                                            {new Date().toLocaleDateString()}
                                        </span>
                                        <a
                                            href={job.url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="ml-auto inline-flex items-center gap-1.5 text-xs font-medium text-blue-400 hover:text-blue-300 transition-colors"
                                        >
                                            View Job <Briefcase className="w-3 h-3" />
                                        </a>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

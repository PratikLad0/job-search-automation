import React, { useState } from 'react';
import { api } from '../api/client';
import { toast } from 'sonner';
import { Play, Database, Search, MapPin, Loader2 } from 'lucide-react';

export default function ScrapePage() {
    const [loading, setLoading] = useState(false);
    const [source, setSource] = useState('');
    const [query, setQuery] = useState('');
    const [location, setLocation] = useState('');

    const sources = [
        { id: '', name: 'All Sources' },
        { id: 'linkedin', name: 'LinkedIn' },
        { id: 'indeed', name: 'Indeed' },
        { id: 'remoteok', name: 'RemoteOK' },
        { id: 'naukri', name: 'Naukri' },
        { id: 'arbeitnow', name: 'ArbeitNow' },
        { id: 'jobicy', name: 'Jobicy' },
        { id: 'hn_hiring', name: 'HackerNews Hiring' },
        { id: 'glassdoor', name: 'Glassdoor' },
        { id: 'wellfound', name: 'Wellfound' },
        { id: 'weworkremotely', name: 'We Work Remotely' },
        { id: 'findwork', name: 'FindWork' },
        { id: 'adzuna', name: 'Adzuna' },
        { id: 'greenhouse', name: 'Greenhouse' },
    ];

    const targetLocations = [
        'India', 'Germany', 'Netherlands', 'UK', 'Singapore', 'UAE', 'Remote'
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
            toast.success('Scraper started in background!');
        } catch (error) {
            toast.error('Failed to start scraper');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <header>
                <h2 className="text-3xl font-bold text-slate-900">Scrape Jobs</h2>
                <p className="text-slate-500">Trigger scrapers to find new job listings</p>
            </header>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                <form onSubmit={handleScrape} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Source</label>
                        <div className="relative">
                            <Database className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                            <select
                                className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                                value={source}
                                onChange={(e) => setSource(e.target.value)}
                            >
                                {sources.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                            </select>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Job Role / Query</label>
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <input
                                    type="text"
                                    placeholder="e.g. Backend Engineer"
                                    className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Location</label>
                            <div className="relative">
                                <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <input
                                    type="text"
                                    placeholder="e.g. Berlin, Remote"
                                    className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    value={location}
                                    onChange={(e) => setLocation(e.target.value)}
                                />
                            </div>
                            <div className="mt-2 flex flex-wrap gap-2">
                                {targetLocations.map(loc => (
                                    <button
                                        key={loc}
                                        type="button"
                                        onClick={() => setLocation(loc)}
                                        className={`text-xs px-2 py-1 rounded-md border ${location === loc
                                                ? 'bg-blue-100 border-blue-300 text-blue-800'
                                                : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                                            }`}
                                    >
                                        {loc}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg transition-colors flex items-center justify-center"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                Starting Scraper...
                            </>
                        ) : (
                            <>
                                <Play className="w-5 h-5 mr-2" />
                                Run Scraper
                            </>
                        )}
                    </button>
                </form>
            </div>

            <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 text-sm text-blue-800">
                <p className="font-semibold mb-1">Note:</p>
                <p>Scraping runs in the background. It may take several minutes to complete depending on the source. Check the Dashboard for new jobs.</p>
            </div>
        </div>
    );
}

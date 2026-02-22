import { useState, useEffect } from 'react';
import { Mail, CheckCircle, XCircle, Loader2 } from 'lucide-react';

import { API_BASE_URL } from '../../config';

export default function GoogleSignIn() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        checkAuthStatus();
    }, []);

    const checkAuthStatus = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/status`);
            const data = await response.json();
            setIsAuthenticated(data.authenticated);
        } catch (err) {
            console.error('Failed to check auth status:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSignIn = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`);
            const data = await response.json();
            if (data.url) {
                window.location.href = data.url;
            } else {
                setError('Failed to get login URL');
            }
        } catch (err) {
            setError('Connection error. Is the backend running?');
            console.error('Sign-in error:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center space-x-2 text-slate-500 py-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Checking status...</span>
            </div>
        );
    }

    return (
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${isAuthenticated ? 'bg-green-100 text-green-600' : 'bg-slate-200 text-slate-600'}`}>
                        <Mail className="w-5 h-5" />
                    </div>
                    <div>
                        <h4 className="font-semibold text-slate-900 text-sm">Gmail Integration</h4>
                        <p className="text-xs text-slate-500">
                            {isAuthenticated
                                ? 'Connected! Crawler will check for recruiter emails.'
                                : 'Connect your Gmail to enable email crawling and replies tracking.'}
                        </p>
                    </div>
                </div>

                {isAuthenticated ? (
                    <div className="flex items-center space-x-1 text-green-600">
                        <CheckCircle className="w-4 h-4" />
                        <span className="text-xs font-medium">Active</span>
                    </div>
                ) : (
                    <button
                        onClick={handleSignIn}
                        disabled={loading}
                        className="bg-white border border-slate-300 text-slate-700 px-4 py-1.5 rounded-lg text-xs font-bold flex items-center hover:bg-slate-50 transition-colors shadow-sm"
                    >
                        <img
                            src="https://www.google.com/favicon.ico"
                            alt="Google"
                            className="w-3 h-3 mr-2"
                        />
                        Sign in with Google
                    </button>
                )}
            </div>

            {error && (
                <div className="mt-2 flex items-center space-x-1 text-red-500 text-xs">
                    <XCircle className="w-3 h-3" />
                    <span>{error}</span>
                </div>
            )}
        </div>
    );
}

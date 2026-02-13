import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo);
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-slate-50">
                    <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 border border-red-100">
                        <div className="text-center">
                            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                            </div>
                            <h2 className="text-2xl font-bold text-slate-900 mb-2">Something went wrong</h2>
                            <p className="text-slate-600 mb-6">
                                The page encountered an error. Please try refreshing.
                            </p>
                            {this.state.error && (
                                <details className="text-left mb-6">
                                    <summary className="cursor-pointer text-sm text-slate-500 hover:text-slate-700 mb-2">
                                        Error details
                                    </summary>
                                    <pre className="text-xs bg-slate-50 p-3 rounded border border-slate-200 overflow-auto max-h-40">
                                        {this.state.error.toString()}
                                    </pre>
                                </details>
                            )}
                            <button
                                onClick={() => window.location.reload()}
                                className="bg-blue-600 text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-sm"
                            >
                                Reload Page
                            </button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

import { useState, useEffect } from 'react';
import { emailsApi } from '../api/client';
import type { Email } from '../types/Email';
import { Mail, ChevronDown, ChevronUp, Sparkles, Clock } from 'lucide-react';
import { toast } from 'sonner';

export default function EmailsPage() {
    const [emails, setEmails] = useState<Email[]>([]);
    const [loading, setLoading] = useState(true);
    const [expandedId, setExpandedId] = useState<number | null>(null);
    const [generatingId, setGeneratingId] = useState<number | null>(null);
    const [replies, setReplies] = useState<{ [key: number]: string }>({});

    useEffect(() => {
        loadEmails();
    }, []);

    const loadEmails = async () => {
        try {
            setLoading(true);
            const data = await emailsApi.list();
            setEmails(data);
        } catch (e) {
            console.error(e);
            toast.error("Failed to load emails");
        } finally {
            setLoading(false);
        }
    };

    const toggleExpand = (id: number) => {
        setExpandedId(expandedId === id ? null : id);
    };

    const handleGenerateReply = async (e: React.MouseEvent, id: number) => {
        e.stopPropagation();
        try {
            setGeneratingId(id);
            const data = await emailsApi.reply(id);
            setReplies(prev => ({ ...prev, [id]: data.reply }));
            toast.success("Reply generated!");
            if (expandedId !== id) setExpandedId(id);
        } catch (error) {
            console.error(error);
            toast.error("Failed to generate reply");
        } finally {
            setGeneratingId(null);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-6rem)]">
            <header className="mb-6">
                <h2 className="text-3xl font-bold text-slate-900">Inbox</h2>
                <p className="text-slate-500">Important job-related emails</p>
            </header>

            <div className="flex-1 overflow-y-auto pr-2 space-y-4">
                {loading ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    </div>
                ) : emails.length === 0 ? (
                    <div className="text-center py-20 bg-white rounded-xl border border-slate-100">
                        <Mail className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-slate-900">No emails found</h3>
                        <p className="text-slate-500">Wait for the crawler to find job-related emails.</p>
                    </div>
                ) : (
                    emails.map(email => (
                        <div
                            key={email.id}
                            className={`bg-white rounded-xl border transition-all duration-200 overflow-hidden ${expandedId === email.id ? 'shadow-md border-blue-200' : 'shadow-sm border-slate-100 hover:border-blue-100'
                                }`}
                        >
                            {/* Header / Summary Row */}
                            <div
                                onClick={() => toggleExpand(email.id)}
                                className="p-4 cursor-pointer flex items-center gap-4 hover:bg-slate-50/50 transition-colors"
                            >
                                <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${email.is_read ? 'bg-slate-100 text-slate-400' : 'bg-blue-100 text-blue-600'
                                    }`}>
                                    <Mail className="w-5 h-5" />
                                </div>

                                <div className="flex-1 min-w-0">
                                    <div className="flex justify-between items-start">
                                        <h3 className={`font-semibold text-slate-900 truncate ${!email.is_read && 'font-bold'}`}>
                                            {email.subject}
                                        </h3>
                                        <span className="text-xs text-slate-400 whitespace-nowrap flex items-center">
                                            <Clock className="w-3 h-3 mr-1" />
                                            {new Date(email.received_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center mt-1">
                                        <p className="text-sm text-slate-600 truncate flex items-center">
                                            <span className="font-medium mr-2 text-slate-800">{email.sender}</span>
                                            <span className="text-slate-400">- {email.snippet}</span>
                                        </p>
                                        <div className="text-slate-400">
                                            {expandedId === email.id ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Expanded Content */}
                            {expandedId === email.id && (
                                <div className="p-6 pt-0 border-t border-slate-100 bg-slate-50/30">
                                    <div className="mt-4 p-4 bg-white rounded-lg border border-slate-100 text-sm text-slate-700 whitespace-pre-wrap">
                                        {email.body}
                                    </div>

                                    {/* Action Bar */}
                                    <div className="mt-4 flex items-center justify-between">
                                        <div className="flex gap-2">
                                            <button
                                                onClick={(e) => handleGenerateReply(e, email.id)}
                                                disabled={generatingId === email.id}
                                                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg text-sm font-medium hover:from-blue-700 hover:to-indigo-700 transition-all shadow-sm flex items-center gap-2 disabled:opacity-70"
                                            >
                                                {generatingId === email.id ? (
                                                    <>
                                                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white"></div>
                                                        Generating...
                                                    </>
                                                ) : (
                                                    <>
                                                        <Sparkles className="w-4 h-4" />
                                                        Generate AI Reply
                                                    </>
                                                )}
                                            </button>
                                        </div>
                                    </div>

                                    {/* Generated Reply Area */}
                                    {(replies[email.id] || email.reply_content) && (
                                        <div className="mt-4 animate-in fade-in slide-in-from-top-2">
                                            <div className="flex items-center gap-2 mb-2 text-sm font-semibold text-indigo-900">
                                                <Sparkles className="w-4 h-4 text-indigo-500" />
                                                Suggested Reply
                                            </div>
                                            <div className="relative">
                                                <textarea
                                                    className="w-full h-48 p-4 rounded-lg border border-indigo-100 bg-indigo-50/30 text-slate-800 text-sm focus:ring-2 focus:ring-indigo-500 outline-none resize-none font-sans"
                                                    value={replies[email.id] || email.reply_content}
                                                    readOnly
                                                />
                                                <div className="absolute bottom-4 right-4 flex gap-2">
                                                    <button
                                                        onClick={() => {
                                                            navigator.clipboard.writeText(replies[email.id] || email.reply_content);
                                                            toast.success("Copied to clipboard!");
                                                        }}
                                                        className="px-3 py-1.5 bg-white text-slate-600 rounded-md text-xs font-medium border border-slate-200 hover:bg-slate-50 shadow-sm"
                                                    >
                                                        Copy Text
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

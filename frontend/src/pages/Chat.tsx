import React, { useState, useRef, useEffect } from 'react';
import { useWebSocket } from '../context/WebSocketProvider';
import { Send, Bot, Loader2, Download, CheckCircle2, Clock } from 'lucide-react';

interface Message {
    id?: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    status?: 'queued' | 'processing' | 'completed' | 'failed';
    type?: string;
    links?: { label: string; url: string }[];
}

export default function ChatPage() {
    const { connected, sendMessage, lastEvent, queueStatus } = useWebSocket();
    const [messages, setMessages] = useState<Message[]>([
        { role: 'assistant', content: "Hello! I'm your job search assistant. I can help you analyze jobs, tailor resumes, and manage your applications. Ask me anything!" }
    ]);
    const [input, setInput] = useState('');
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll on new messages
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    // Handle incoming WebSocket events
    useEffect(() => {
        if (!lastEvent) return;

        const { type, data } = lastEvent;

        if (type === "task_queued" && data.task.type === "chat") {
            // Check if this chat message is already in our state (from our optimistic update)
            // If not, it means it's from another tab/broadcast
            setMessages(prev => {
                const exists = prev.find(m => m.id === data.task.id);
                if (exists) return prev;
                return [...prev, {
                    id: data.task.id,
                    role: 'user',
                    content: "Requested a task...", // We might not have the original message for broadcasted tasks from other tabs
                    status: 'queued'
                }];
            });
        }

        if (type === "task_started") {
            setMessages(prev => prev.map(m =>
                m.id === data.task.id ? { ...m, status: 'processing' } : m
            ));
        }

        if (type === "task_finished") {
            setMessages(prev => {
                const task = data.task;
                const result = data.result;

                // If it was a chat task, update the content with the response
                if (task.type === "chat" && result) {
                    return prev.map(m =>
                        m.id === task.id ? {
                            ...m,
                            role: 'assistant',
                            content: result.response || 'No response received',
                            status: 'completed'
                        } : m
                    );
                }

                // Handle resume generation
                if (task.type === "resume_generation") {
                    if (!result || task.status === 'failed') {
                        return [...prev, {
                            role: 'system',
                            content: `❌ Resume generation failed${task.error ? ': ' + task.error : ''}`,
                            status: 'failed',
                            type: 'notification'
                        }];
                    }

                    const links = [];
                    if (result.resume_url) links.push({ label: "Download Resume", url: `http://localhost:8000${result.resume_url}` });

                    return [...prev, {
                        role: 'system',
                        content: `✅ Resume generated for Job #${result.job_id}`,
                        status: 'completed',
                        type: 'notification',
                        links
                    }];
                }

                // Handle cover letter generation
                if (task.type === "cover_letter_generation") {
                    if (!result || task.status === 'failed') {
                        return [...prev, {
                            role: 'system',
                            content: `❌ Cover letter generation failed${task.error ? ': ' + task.error : ''}`,
                            status: 'failed',
                            type: 'notification'
                        }];
                    }

                    const links = [];
                    if (result.cover_letter_url) links.push({ label: "Download Cover Letter", url: `http://localhost:8000${result.cover_letter_url}` });

                    return [...prev, {
                        role: 'system',
                        content: `✅ Cover letter generated for Job #${result.job_id}`,
                        status: 'completed',
                        type: 'notification',
                        links
                    }];
                }

                // Legacy: If it was a document generation (both), add a notification message
                if (task.type === "document_generation") {
                    // Check if task failed
                    if (!result || task.status === 'failed') {
                        return [...prev, {
                            role: 'system',
                            content: `❌ Document generation failed${task.error ? ': ' + task.error : ''}`,
                            status: 'failed',
                            type: 'notification'
                        }];
                    }

                    const links = [];
                    if (result.resume_url) links.push({ label: "Download Resume", url: `http://localhost:8000${result.resume_url}` });
                    if (result.cover_letter_url) links.push({ label: "Download Cover Letter", url: `http://localhost:8000${result.cover_letter_url}` });

                    return [...prev, {
                        role: 'system',
                        content: `✅ Documents generated for Job #${result.job_id}`,
                        status: 'completed',
                        type: 'notification',
                        links
                    }];
                }

                if (task.type === "profile_update") {
                    // Check if task failed
                    if (!result || task.status === 'failed') {
                        return [...prev, {
                            role: 'system',
                            content: `❌ Profile update failed${task.error ? ': ' + task.error : ''}`,
                            status: 'failed',
                            type: 'notification'
                        }];
                    }

                    return [...prev, {
                        role: 'system',
                        content: `✅ Profile updated successfully for ${result.full_name}`,
                        status: 'completed',
                        type: 'notification'
                    }];
                }

                return prev;
            });
        }
    }, [lastEvent]);

    const handleSend = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || !connected) return;

        const userMsg = input.trim();
        const optimisticId = `pending-${Date.now()}`;

        // Add user message optimistically
        setMessages(prev => [...prev, {
            id: optimisticId, // This will be replaced once we get task_queued
            role: 'user',
            content: userMsg,
            status: 'queued'
        }]);

        sendMessage({
            type: "chat",
            message: userMsg
        });

        setInput('');
    };

    // Replace optimistic ID with real task ID from broadcast
    useEffect(() => {
        if (lastEvent?.type === "task_queued" && lastEvent.data.task.type === "chat") {
            setMessages(prev => {
                const lastUserMsgIndex = [...prev].reverse().findIndex(m => m.role === 'user' && m.id?.startsWith('pending-'));
                if (lastUserMsgIndex !== -1) {
                    const realIndex = prev.length - 1 - lastUserMsgIndex;
                    const newArr = [...prev];
                    newArr[realIndex] = { ...newArr[realIndex], id: lastEvent.data.task.id };
                    return newArr;
                }
                return prev;
            });
        }
    }, [lastEvent]);

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)] bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
            {/* Connection Status Header */}
            <div className="px-4 py-2 border-b border-slate-100 bg-slate-50 flex items-center justify-between text-xs font-medium">
                <div className="flex items-center gap-2 text-slate-500">
                    <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                    {connected ? 'Connected to AI Engine' : 'Reconnecting...'}
                </div>
                {queueStatus.size > 0 && (
                    <div className="flex items-center gap-2 text-blue-600">
                        <Clock className="w-3 h-3" />
                        {queueStatus.size} tasks in queue
                    </div>
                )}
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`relative group max-w-[85%] rounded-2xl px-4 py-3 ${msg.role === 'user' ? 'bg-blue-600 text-white' :
                            msg.role === 'system' ? 'bg-slate-50 border border-slate-200 text-slate-600 w-full italic' :
                                'bg-slate-100 text-slate-800'
                            }`}>
                            <div className="flex items-start gap-2">
                                {msg.role === 'assistant' && <Bot className="w-5 h-5 flex-shrink-0 mt-0.5" />}
                                {msg.role === 'system' && <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5 text-green-500" />}
                                <div className="space-y-2">
                                    <span className="whitespace-pre-wrap">{msg.content}</span>

                                    {/* Links for system notifications (Downloads) */}
                                    {msg.links && (
                                        <div className="flex flex-wrap gap-2 mt-2 not-italic">
                                            {msg.links.map((link, lIdx) => (
                                                <a
                                                    key={lIdx}
                                                    href={link.url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-semibold text-blue-600 hover:bg-blue-50 transition-colors shadow-sm"
                                                >
                                                    <Download className="w-3.5 h-3.5" />
                                                    {link.label}
                                                </a>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Status Indicators */}
                            {msg.role === 'user' && msg.status !== 'completed' && (
                                <div className="absolute -left-12 bottom-0 flex flex-col items-center gap-1">
                                    {msg.status === 'queued' ? (
                                        <div title="Queued" className="p-1 bg-slate-100 rounded-full text-slate-400">
                                            <Clock className="w-3 h-3" />
                                        </div>
                                    ) : (
                                        <div title="Processing" className="p-1 bg-blue-100 rounded-full text-blue-500">
                                            <Loader2 className="w-3 h-3 animate-spin" />
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* Input Form */}
            <div className="p-4 border-t border-slate-100 bg-slate-50">
                <form onSubmit={handleSend} className="flex gap-2">
                    <input
                        type="text"
                        className="flex-1 border border-slate-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                        placeholder={connected ? "Ask about jobs, career advice..." : "Connecting..."}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={!connected}
                    />
                    <button
                        type="submit"
                        disabled={!connected || !input.trim()}
                        className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm transition-all active:scale-95"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </form>
            </div>
        </div>
    );
}

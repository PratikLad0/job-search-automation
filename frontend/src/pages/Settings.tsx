import React from 'react';
import { Save } from 'lucide-react';

export default function SettingsPage() {
    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <header>
                <h2 className="text-3xl font-bold text-slate-900">Settings</h2>
                <p className="text-slate-500">Configure your job search preferences and notifications.</p>
            </header>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 space-y-6">
                <div className="border-b border-slate-100 pb-4">
                    <h3 className="tex-lg font-bold text-slate-800 mb-2">Notifications</h3>
                    <p className="text-sm text-slate-500 mb-4">
                        Setup your notification channels. Note: These require editing the <code>.env</code> file in the project root.
                    </p>

                    <div className="space-y-4">
                        <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                            <h4 className="font-semibold text-blue-900 text-sm mb-2">Telegram Setup</h4>
                            <ol className="list-decimal list-inside text-sm text-blue-800 space-y-1">
                                <li>Create a bot with <a href="https://t.me/BotFather" className="underline" target="_blank" rel="noreferrer">@BotFather</a></li>
                                <li>Get your <code>Context ID</code> (Chat ID)</li>
                                <li>Add to .env: <code>TELEGRAM_BOT_TOKEN</code> and <code>TELEGRAM_CHAT_ID</code></li>
                            </ol>
                        </div>

                        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-100">
                            <h4 className="font-semibold text-yellow-900 text-sm mb-2">Email Setup</h4>
                            <p className="text-sm text-yellow-800 mb-2">Add your SMTP credentials to .env:</p>
                            <pre className="bg-white p-2 rounded text-xs overflow-x-auto border border-yellow-200 text-yellow-900">
                                {`SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password`}
                            </pre>
                        </div>
                    </div>
                </div>

                <div>
                    <h3 className="tex-lg font-bold text-slate-800 mb-4">Job Preferences</h3>
                    <p className="text-sm text-slate-500 mb-4">
                        Defaults for scrapers and matching. (Edit <code>config.py</code> or <code>.env</code> to persist).
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Target Role</label>
                            <input type="text" disabled value="Backend Engineer" className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-500" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Minimum Salary (Annual)</label>
                            <input type="text" disabled value="$70,000" className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-500" />
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex justify-end">
                <button className="bg-slate-900 text-white px-6 py-2 rounded-lg font-medium flex items-center hover:bg-slate-800 opacity-50 cursor-not-allowed">
                    <Save className="w-4 h-4 mr-2" />
                    Save Changes (Coming Soon)
                </button>
            </div>
        </div>
    );
}

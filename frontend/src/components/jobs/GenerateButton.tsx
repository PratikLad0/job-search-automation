import { useState } from 'react';
import { FileText, FileType, Loader2, Download } from 'lucide-react';
import { toast } from 'sonner';

interface GenerateButtonProps {
    jobId: number;
    status: string;
    resumePath?: string;
    coverLetterPath?: string;
    onGenerateComplete?: () => void;
}

export function GenerateButton({ jobId, resumePath, coverLetterPath, onGenerateComplete }: GenerateButtonProps) {
    const [generating, setGenerating] = useState(false);
    const [showMenu, setShowMenu] = useState(false);

    const handleGenerate = async (format: 'pdf' | 'docx') => {
        setGenerating(true);
        setShowMenu(false);
        try {
            const response = await fetch(`http://localhost:8000/generate/${jobId}?format=${format}`, {
                method: 'POST',
            });
            if (response.ok) {
                toast.success(`Generating ${format.toUpperCase()} documents...`);
                // Poll or wait? Ideally we rely on status update via websocket or refresh
                // For now, just timeout to simulate
                setTimeout(() => {
                    onGenerateComplete?.();
                }, 3000);
            } else {
                toast.error('Failed to start generation');
            }
        } catch (error) {
            console.error(error);
            toast.error('Error generating documents');
        } finally {
            setGenerating(false);
        }
    };

    const downloadFile = (path: string) => {
        if (!path) return;
        // The path is absolute on server, we need a download endpoint
        window.open(`http://localhost:8000/generate/download?path=${encodeURIComponent(path)}`, '_blank');
    };

    if (generating) {
        return (
            <button disabled className="flex items-center space-x-2 px-3 py-1.5 bg-gray-100 text-gray-500 rounded-md cursor-not-allowed">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-xs">Generating...</span>
            </button>
        );
    }

    const hasDocs = resumePath || coverLetterPath;

    return (
        <div className="relative">
            {hasDocs ? (
                <div className="flex space-x-2">
                    {resumePath && (
                        <button
                            onClick={() => downloadFile(resumePath)}
                            className="flex items-center space-x-1 px-3 py-1.5 bg-green-50 text-green-700 hover:bg-green-100 rounded-md border border-green-200"
                            title="Download Resume"
                        >
                            <Download className="h-3 w-3" />
                            <span className="text-xs font-medium">Resume</span>
                        </button>
                    )}
                    {coverLetterPath && (
                        <button
                            onClick={() => downloadFile(coverLetterPath)}
                            className="flex items-center space-x-1 px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded-md border border-blue-200"
                            title="Download Cover Letter"
                        >
                            <Download className="h-3 w-3" />
                            <span className="text-xs font-medium">Letter</span>
                        </button>
                    )}
                    <button
                        onClick={() => setShowMenu(!showMenu)}
                        className="p-1.5 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100"
                        title="Regenerate"
                    >
                        <FileType className="h-4 w-4" />
                    </button>
                </div>
            ) : (
                <button
                    onClick={() => setShowMenu(!showMenu)}
                    className="flex items-center space-x-2 px-3 py-1.5 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded-md border border-indigo-200 transition-colors"
                >
                    <FileText className="h-3 w-3" />
                    <span className="text-xs font-medium">Generate Docs</span>
                </button>
            )}

            {showMenu && (
                <div className="absolute top-full mt-1 right-0 w-32 bg-white rounded-lg shadow-xl border border-gray-100 z-50 overflow-hidden">
                    <button
                        onClick={() => handleGenerate('pdf')}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center"
                    >
                        <span className="w-8">PDF</span>
                        <span className="text-xs text-gray-400 ml-auto">Best for Email</span>
                    </button>
                    <button
                        onClick={() => handleGenerate('docx')}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center border-t border-gray-50"
                    >
                        <span className="w-8">DOCX</span>
                        <span className="text-xs text-gray-400 ml-auto">Editable</span>
                    </button>
                </div>
            )}

            {showMenu && (
                <div
                    className="fixed inset-0 z-40"
                    onClick={() => setShowMenu(false)}
                ></div>
            )}
        </div>
    );
}

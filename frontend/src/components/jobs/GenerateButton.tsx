import { useState } from 'react';
import { FileText, Mail, Loader2, Download } from 'lucide-react';
import { toast } from 'sonner';
import { API_BASE_URL } from '../../config';

interface GenerateButtonProps {
    jobId: number;
    status: string;
    resumePath?: string;
    coverLetterPath?: string;
    onGenerateComplete?: () => void;
}

type DocumentType = 'resume' | 'cover_letter';
type GeneratingState = {
    resume: boolean;
    cover_letter: boolean;
};

export function GenerateButton({ jobId, resumePath, coverLetterPath }: GenerateButtonProps) {
    const [generating, setGenerating] = useState<GeneratingState>({
        resume: false,
        cover_letter: false
    });
    const [showFormatMenu, setShowFormatMenu] = useState<DocumentType | null>(null);

    const handleGenerate = async (docType: DocumentType, format: 'pdf' | 'docx') => {
        setGenerating(prev => ({ ...prev, [docType]: true }));
        setShowFormatMenu(null);

        try {
            const response = await fetch(`${API_BASE_URL}/generators/${jobId}/${docType}?format=${format}`, {
                method: 'POST',
            });

            if (response.ok) {
                const data = await response.json();
                const docName = docType === 'resume' ? 'Resume' : 'Cover Letter';
                if (data.status === 'queued') {
                    toast.info(`${docName} queued for ${format.toUpperCase()} generation.`);
                } else {
                    toast.success(`Generating ${docName} in ${format.toUpperCase()}...`);
                }
            } else {
                toast.error('Failed to queue generation');
            }
        } catch (error) {
            console.error(error);
            toast.error('Error generating document');
        } finally {
            setGenerating(prev => ({ ...prev, [docType]: false }));
        }
    };

    const downloadFile = (path: string) => {
        if (!path) return;
        window.open(`${API_BASE_URL}/generators/download?path=${encodeURIComponent(path)}`, '_blank');
    };

    const isGenerating = generating.resume || generating.cover_letter;

    return (
        <div className="flex flex-col gap-2">
            {/* Resume Button */}
            <div className="relative">
                {resumePath ? (
                    <div className="flex items-center gap-1">
                        <button
                            onClick={() => downloadFile(resumePath)}
                            className="flex items-center space-x-1 px-3 py-1.5 bg-green-50 text-green-700 hover:bg-green-100 rounded-md border border-green-200 transition-colors"
                            title="Download Resume"
                        >
                            <Download className="h-3 w-3" />
                            <span className="text-xs font-medium">Resume</span>
                        </button>
                        <button
                            onClick={() => setShowFormatMenu(showFormatMenu === 'resume' ? null : 'resume')}
                            disabled={isGenerating}
                            className="p-1.5 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100 disabled:opacity-50"
                            title="Regenerate Resume"
                        >
                            <FileText className="h-3.5 w-3.5" />
                        </button>
                    </div>
                ) : (
                    <button
                        onClick={() => setShowFormatMenu(showFormatMenu === 'resume' ? null : 'resume')}
                        disabled={generating.resume}
                        className="flex items-center space-x-1.5 px-3 py-1.5 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded-md border border-indigo-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {generating.resume ? (
                            <>
                                <Loader2 className="h-3 w-3 animate-spin" />
                                <span className="text-xs font-medium">Generating...</span>
                            </>
                        ) : (
                            <>
                                <FileText className="h-3 w-3" />
                                <span className="text-xs font-medium">Generate Resume</span>
                            </>
                        )}
                    </button>
                )}

                {/* Resume Format Menu */}
                {showFormatMenu === 'resume' && (
                    <div className="absolute top-full mt-1 right-0 w-36 bg-white rounded-lg shadow-xl border border-gray-100 z-50 overflow-hidden">
                        <button
                            onClick={() => handleGenerate('resume', 'pdf')}
                            className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center"
                        >
                            <span className="w-8 font-medium">PDF</span>
                            <span className="text-xs text-gray-400 ml-auto">Best</span>
                        </button>
                        <button
                            onClick={() => handleGenerate('resume', 'docx')}
                            className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center border-t border-gray-50"
                        >
                            <span className="w-8 font-medium">DOCX</span>
                            <span className="text-xs text-gray-400 ml-auto">Edit</span>
                        </button>
                    </div>
                )}
            </div>

            {/* Cover Letter Button */}
            <div className="relative">
                {coverLetterPath ? (
                    <div className="flex items-center gap-1">
                        <button
                            onClick={() => downloadFile(coverLetterPath)}
                            className="flex items-center space-x-1 px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded-md border border-blue-200 transition-colors"
                            title="Download Cover Letter"
                        >
                            <Download className="h-3 w-3" />
                            <span className="text-xs font-medium">Cover Letter</span>
                        </button>
                        <button
                            onClick={() => setShowFormatMenu(showFormatMenu === 'cover_letter' ? null : 'cover_letter')}
                            disabled={isGenerating}
                            className="p-1.5 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100 disabled:opacity-50"
                            title="Regenerate Cover Letter"
                        >
                            <Mail className="h-3.5 w-3.5" />
                        </button>
                    </div>
                ) : (
                    <button
                        onClick={() => setShowFormatMenu(showFormatMenu === 'cover_letter' ? null : 'cover_letter')}
                        disabled={generating.cover_letter}
                        className="flex items-center space-x-1.5 px-3 py-1.5 bg-purple-50 text-purple-700 hover:bg-purple-100 rounded-md border border-purple-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {generating.cover_letter ? (
                            <>
                                <Loader2 className="h-3 w-3 animate-spin" />
                                <span className="text-xs font-medium">Generating...</span>
                            </>
                        ) : (
                            <>
                                <Mail className="h-3 w-3" />
                                <span className="text-xs font-medium">Generate Letter</span>
                            </>
                        )}
                    </button>
                )}

                {/* Cover Letter Format Menu */}
                {showFormatMenu === 'cover_letter' && (
                    <div className="absolute top-full mt-1 right-0 w-36 bg-white rounded-lg shadow-xl border border-gray-100 z-50 overflow-hidden">
                        <button
                            onClick={() => handleGenerate('cover_letter', 'pdf')}
                            className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center"
                        >
                            <span className="w-8 font-medium">PDF</span>
                            <span className="text-xs text-gray-400 ml-auto">Best</span>
                        </button>
                        <button
                            onClick={() => handleGenerate('cover_letter', 'docx')}
                            className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center border-t border-gray-50"
                        >
                            <span className="w-8 font-medium">DOCX</span>
                            <span className="text-xs text-gray-400 ml-auto">Edit</span>
                        </button>
                    </div>
                )}
            </div>

            {/* Backdrop to close menus */}
            {showFormatMenu && (
                <div
                    className="fixed inset-0 z-40"
                    onClick={() => setShowFormatMenu(null)}
                ></div>
            )}
        </div>
    );
}

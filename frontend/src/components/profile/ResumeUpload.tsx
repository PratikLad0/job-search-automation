import { useState } from 'react';
import { Upload, AlertCircle } from 'lucide-react';

interface ResumeUploadProps {
    onUploadSuccess: (data: any) => void;
}

export function ResumeUpload({ onUploadSuccess }: ResumeUploadProps) {
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = async (file: File) => {
        // Validate file type
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
        if (!validTypes.includes(file.type)) {
            setError('Please upload a PDF or DOCX file.');
            return;
        }

        setIsUploading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/profile/upload-resume', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const data = await response.json();
            onUploadSuccess(data);
        } catch (err) {
            setError('Failed to upload and parse resume. Please try again.');
            console.error(err);
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="w-full">
            <div
                className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
                    }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    onChange={handleChange}
                    accept=".pdf,.docx,.doc"
                />

                <div className="flex flex-col items-center justify-center space-y-3">
                    {isUploading ? (
                        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
                    ) : (
                        <Upload className="h-10 w-10 text-gray-400" />
                    )}

                    <div className="text-sm text-gray-600">
                        {isUploading ? (
                            <span>Parsing resume... This uses AI and may take a moment.</span>
                        ) : (
                            <>
                                <span className="font-semibold text-blue-600">Click to upload</span> or drag and drop
                                <p className="text-xs text-gray-500 mt-1">PDF or DOCX (max 10MB)</p>
                            </>
                        )}
                    </div>
                </div>
            </div>

            {error && (
                <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg flex items-center text-sm">
                    <AlertCircle className="h-4 w-4 mr-2" />
                    {error}
                </div>
            )}
        </div>
    );
}

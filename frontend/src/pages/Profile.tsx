import { useState, useEffect } from 'react';
import { User, Briefcase, GraduationCap, Code, FileText, Save, Plus, Trash2, Award, Heart, BookOpen, Globe } from 'lucide-react';
import { toast } from 'sonner';
import { ResumeUpload } from '../components/profile/ResumeUpload';
import type { UserProfile } from '../types';

const TABS = [
    { id: 'personal', label: 'Personal Info', icon: User },
    { id: 'skills', label: 'Skills', icon: Code },
    { id: 'experience', label: 'Experience', icon: Briefcase },
    { id: 'education', label: 'Education', icon: GraduationCap },
    { id: 'projects', label: 'Projects', icon: FileText },
    { id: 'other', label: 'Other', icon: Globe },
];

export default function Profile() {
    const [activeTab, setActiveTab] = useState('personal');
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [profile, setProfile] = useState<UserProfile>({
        id: 1,
        full_name: '',
        email: '',
        phone: '',
        location: '',
        linkedin_url: '',
        github_url: '',
        portfolio_url: '',
        about_me: '',
        skills: [],
        experience: [],
        education: [],
        projects: [],
        certifications: [],
        achievements: [],
        hobbies: [],
        interests: [],
        languages: [],
        volunteering: [],
        publications: [],
        awards: [],
        references: [],
        resume_path: '',
    });

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            const response = await fetch('http://localhost:8000/profile/');
            if (response.ok) {
                const data = await response.json();
                setProfile(data);
            }
        } catch (error) {
            console.error('Failed to fetch profile:', error);
            toast.error('Failed to load profile');
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            const response = await fetch('http://localhost:8000/profile/', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profile),
            });

            if (response.ok) {
                const data = await response.json();
                setProfile(data);
                toast.success('Profile saved successfully');
            } else {
                throw new Error('Failed to save');
            }
        } catch (error) {
            console.error('Failed to save profile:', error);
            toast.error('Failed to save profile');
        } finally {
            setSaving(false);
        }
    };

    const handleResumeParsed = (data: Partial<UserProfile>) => {
        setProfile(prev => ({ ...prev, ...data }));
        toast.success('Resume parsed! Please review and save your profile.');
    };

    const updateField = (field: keyof UserProfile, value: any) => {
        setProfile(prev => ({ ...prev, [field]: value }));
    };

    const addArrayItem = (field: keyof UserProfile, item: any) => {
        setProfile(prev => ({
            ...prev,
            [field]: [...(prev[field] as any[]), item]
        }));
    };

    const removeArrayItem = (field: keyof UserProfile, index: number) => {
        setProfile(prev => ({
            ...prev,
            [field]: (prev[field] as any[]).filter((_, i) => i !== index)
        }));
    };

    const updateArrayItem = (field: keyof UserProfile, index: number, key: string, value: any) => {
        setProfile(prev => {
            const newArray = [...(prev[field] as any[])];
            newArray[index] = { ...newArray[index], [key]: value };
            return { ...prev, [field]: newArray };
        });
    };

    if (loading) {
        return <div className="p-8 text-center">Loading profile...</div>;
    }

    return (
        <div className="max-w-5xl mx-auto p-6 space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
                <button
                    onClick={handleSave}
                    disabled={saving}
                    className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                    <Save className="h-4 w-4" />
                    <span>{saving ? 'Saving...' : 'Save Profile'}</span>
                </button>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-6 bg-gray-50 border-b border-gray-200">
                    <h2 className="text-lg font-semibold mb-4">Resume Upload</h2>
                    <ResumeUpload onUploadSuccess={handleResumeParsed} />
                </div>

                <div className="flex border-b border-gray-200" role="tablist" aria-label="Profile Sections">
                    {TABS.map(tab => (
                        <button
                            key={tab.id}
                            role="tab"
                            aria-selected={activeTab === tab.id}
                            aria-controls={`${tab.id}-panel`}
                            id={`${tab.id}-tab`}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex-1 py-4 px-6 text-sm font-medium flex items-center justify-center space-x-2 border-b-2 transition-colors ${activeTab === tab.id
                                ? 'border-blue-500 text-blue-600 bg-blue-50'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                                }`}
                        >
                            <tab.icon className="h-4 w-4" aria-hidden="true" />
                            <span>{tab.label}</span>
                        </button>
                    ))}
                </div>

                <div className="p-8">
                    {/* PERSONAL INFO TAB */}
                    {activeTab === 'personal' && (
                        <div id="personal-panel" role="tabpanel" aria-labelledby="personal-tab" className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                                    <input
                                        type="text"
                                        value={profile.full_name}
                                        onChange={e => updateField('full_name', e.target.value)}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500 font-bold"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                                    <input
                                        type="email"
                                        value={profile.email}
                                        onChange={e => updateField('email', e.target.value)}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                                    <input
                                        type="text"
                                        value={profile.phone}
                                        onChange={e => updateField('phone', e.target.value)}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                                    <input
                                        type="text"
                                        value={profile.location}
                                        onChange={e => updateField('location', e.target.value)}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">LinkedIn URL</label>
                                    <input
                                        type="text"
                                        value={profile.linkedin_url}
                                        onChange={e => updateField('linkedin_url', e.target.value)}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">GitHub URL</label>
                                    <input
                                        type="text"
                                        value={profile.github_url}
                                        onChange={e => updateField('github_url', e.target.value)}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Portfolio URL</label>
                                    <input
                                        type="text"
                                        value={profile.portfolio_url}
                                        onChange={e => updateField('portfolio_url', e.target.value)}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Summary / About Me</label>
                                    <textarea
                                        rows={4}
                                        value={profile.about_me}
                                        onChange={e => updateField('about_me', e.target.value)}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500 text-lg"
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* SKILLS TAB */}
                    {activeTab === 'skills' && (
                        <div id="skills-panel" role="tabpanel" aria-labelledby="skills-tab" className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Technologes & Skills (Enter comma separated)</label>
                                <textarea
                                    rows={4}
                                    value={profile.skills.join(', ')}
                                    onChange={e => updateField('skills', e.target.value.split(',').map(s => s.trim()))}
                                    className="w-full p-4 border rounded-md focus:ring-2 focus:ring-blue-500 text-lg"
                                    placeholder="Python, React, TypeScript, FastAP..."
                                />
                            </div>
                            <div className="flex flex-wrap gap-2 mt-4">
                                {profile.skills.map((skill, i) => (
                                    <span key={i} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                                        {skill}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* EXPERIENCE TAB */}
                    {activeTab === 'experience' && (
                        <div className="space-y-6">
                            <button
                                onClick={() => addArrayItem('experience', { title: '', company: '', duration: '', description: '' })}
                                className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 mb-4"
                            >
                                <Plus className="h-4 w-4" />
                                <span>Add Experience</span>
                            </button>

                            {profile.experience.map((exp, index) => (
                                <div key={index} className="border p-4 rounded-lg bg-gray-50 relative group">
                                    <button
                                        onClick={() => removeArrayItem('experience', index)}
                                        aria-label={`Remove experience ${index + 1}`}
                                        className="absolute top-4 right-4 text-red-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </button>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <input
                                            placeholder="Job Title"
                                            value={exp.title}
                                            onChange={e => updateArrayItem('experience', index, 'title', e.target.value)}
                                            className="p-2 border rounded"
                                        />
                                        <input
                                            placeholder="Company"
                                            value={exp.company}
                                            onChange={e => updateArrayItem('experience', index, 'company', e.target.value)}
                                            className="p-2 border rounded"
                                        />
                                        <input
                                            placeholder="Duration (e.g. 2020 - Present)"
                                            value={exp.duration}
                                            onChange={e => updateArrayItem('experience', index, 'duration', e.target.value)}
                                            className="p-2 border rounded"
                                        />
                                        <textarea
                                            placeholder="Description"
                                            value={exp.description}
                                            onChange={e => updateArrayItem('experience', index, 'description', e.target.value)}
                                            className="md:col-span-2 p-2 border rounded h-24"
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* EDUCATION TAB */}
                    {activeTab === 'education' && (
                        <div className="space-y-6">
                            <button
                                onClick={() => addArrayItem('education', { degree: '', institution: '', year: '' })}
                                className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 mb-4"
                            >
                                <Plus className="h-4 w-4" />
                                <span>Add Education</span>
                            </button>

                            {profile.education.map((edu, index) => (
                                <div key={index} className="border p-4 rounded-lg bg-gray-50 relative group">
                                    <button
                                        onClick={() => removeArrayItem('education', index)}
                                        aria-label={`Remove education ${index + 1}`}
                                        className="absolute top-4 right-4 text-red-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </button>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <input
                                            placeholder="Degree"
                                            value={edu.degree}
                                            onChange={e => updateArrayItem('education', index, 'degree', e.target.value)}
                                            className="p-2 border rounded"
                                        />
                                        <input
                                            placeholder="Institution"
                                            value={edu.institution}
                                            onChange={e => updateArrayItem('education', index, 'institution', e.target.value)}
                                            className="p-2 border rounded"
                                        />
                                        <input
                                            placeholder="Year"
                                            value={edu.year}
                                            onChange={e => updateArrayItem('education', index, 'year', e.target.value)}
                                            className="p-2 border rounded"
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* PROJECTS TAB */}
                    {activeTab === 'projects' && (
                        <div className="space-y-6">
                            <button
                                onClick={() => addArrayItem('projects', { name: '', description: '', link: '', tech_stack: [] })}
                                className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 mb-4"
                            >
                                <Plus className="h-4 w-4" />
                                <span>Add Project</span>
                            </button>

                            {profile.projects.map((proj, index) => (
                                <div key={index} className="border p-4 rounded-lg bg-gray-50 relative group">
                                    <button
                                        onClick={() => removeArrayItem('projects', index)}
                                        aria-label={`Remove project ${index + 1}`}
                                        className="absolute top-4 right-4 text-red-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </button>
                                    <div className="grid grid-cols-1 gap-4">
                                        <div className="grid grid-cols-2 gap-4">
                                            <input
                                                placeholder="Project Name"
                                                value={proj.name}
                                                onChange={e => updateArrayItem('projects', index, 'name', e.target.value)}
                                                className="p-2 border rounded font-semibold"
                                            />
                                            <input
                                                placeholder="Link URL"
                                                value={proj.link}
                                                onChange={e => updateArrayItem('projects', index, 'link', e.target.value)}
                                                className="p-2 border rounded"
                                            />
                                        </div>
                                        <textarea
                                            placeholder="Description"
                                            value={proj.description}
                                            onChange={e => updateArrayItem('projects', index, 'description', e.target.value)}
                                            className="p-2 border rounded h-20"
                                        />
                                        <input
                                            placeholder="Tech Stack (comma separated)"
                                            value={proj.tech_stack.join(', ')}
                                            onChange={e => updateArrayItem('projects', index, 'tech_stack', e.target.value.split(',').map((s: string) => s.trim()))}
                                            className="p-2 border rounded"
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* OTHER TAB (Hobbies, Languages, etc) */}
                    {activeTab === 'other' && (
                        <div className="space-y-8">
                            {/* Hobbies */}
                            <div className="space-y-2">
                                <h3 className="text-md font-semibold flex items-center"><Heart className="h-4 w-4 mr-2" /> Hobbies</h3>
                                <textarea
                                    rows={2}
                                    value={profile.hobbies.join(', ')}
                                    onChange={e => updateField('hobbies', e.target.value.split(',').map(s => s.trim()))}
                                    className="w-full p-2 border rounded-md"
                                    placeholder="Photography, Hiking, Chess..."
                                />
                            </div>

                            {/* Interests */}
                            <div className="space-y-2">
                                <h3 className="text-md font-semibold flex items-center"><BookOpen className="h-4 w-4 mr-2" /> Interests</h3>
                                <textarea
                                    rows={2}
                                    value={profile.interests.join(', ')}
                                    onChange={e => updateField('interests', e.target.value.split(',').map(s => s.trim()))}
                                    className="w-full p-2 border rounded-md"
                                    placeholder="AI, Blockchain, Space Travel..."
                                />
                            </div>

                            {/* Languages */}
                            <div className="space-y-2">
                                <h3 className="text-md font-semibold flex items-center"><Globe className="h-4 w-4 mr-2" /> Languages</h3>
                                <textarea
                                    rows={2}
                                    value={profile.languages.join(', ')}
                                    onChange={e => updateField('languages', e.target.value.split(',').map(s => s.trim()))}
                                    className="w-full p-2 border rounded-md"
                                    placeholder="English, Spanish, French..."
                                />
                            </div>

                            {/* Achievements */}
                            <div className="space-y-2">
                                <h3 className="text-md font-semibold flex items-center"><Award className="h-4 w-4 mr-2" /> Achievements</h3>
                                <button
                                    onClick={() => addArrayItem('achievements', '')}
                                    className="text-sm text-blue-600 hover:text-blue-700 mb-2"
                                >
                                    + Add Achievement
                                </button>
                                {profile.achievements.map((ach, i) => (
                                    <div key={i} className="flex gap-2">
                                        <input
                                            value={ach}
                                            onChange={e => {
                                                const newAch = [...profile.achievements];
                                                newAch[i] = e.target.value;
                                                updateField('achievements', newAch);
                                            }}
                                            className="flex-1 p-2 border rounded"
                                        />
                                        <button onClick={() => removeArrayItem('achievements', i)} className="text-red-400"><Trash2 className="h-4 w-4" /></button>
                                    </div>
                                ))}
                            </div>

                        </div>
                    )}

                </div>
            </div>
        </div>
    );
}

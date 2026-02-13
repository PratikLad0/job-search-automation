export interface Job {
    id: number;
    title: string;
    company: string;
    location: string;
    url: string;
    source: string;
    description?: string;
    salary_text?: string;
    job_type?: string;
    posted_date?: string;
    match_score?: number;
    score_reasoning?: string;
    matched_skills?: string;
    status: string;
    resume_path?: string;
    cover_letter_path?: string;
}

export interface Stats {
    total: number;
    avg_score: number;
    by_status: Record<string, number>;
    by_source: Record<string, number>;
}

export interface Experience {
    title: string;
    company: string;
    duration: string;
    description: string;
}

export interface Education {
    degree: string;
    institution: string;
    year: string;
}

export interface Project {
    name: string;
    description: string;
    link: string;
    tech_stack: string[];
}

export interface Volunteering {
    organization: string;
    role: string;
    start_date: string;
    end_date: string;
    description: string;
}

export interface Publication {
    title: string;
    publisher: string;
    date: string;
    link: string;
}

export interface Award {
    title: string;
    issuer: string;
    date: string;
    description: string;
}

export interface Reference {
    name: string;
    contact_info: string;
    relationship: string;
}

export interface UserProfile {
    id: number;
    full_name: string;
    email: string;
    phone: string;
    location: string;
    linkedin_url: string;
    github_url: string;
    portfolio_url: string;
    about_me: string;
    skills: string[];
    experience: Experience[];
    education: Education[];
    projects: Project[];
    certifications: string[];
    achievements: string[];
    hobbies: string[];
    interests: string[];
    languages: string[];
    volunteering: Volunteering[];
    publications: Publication[];
    awards: Award[];
    references: Reference[];
    resume_path?: string;
}

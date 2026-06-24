export type UserRole = 'admin' | 'recruiter' | 'candidate';

export interface UserInfo {
  id: string;
  role: UserRole;
  email: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserRegister {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface UserRead {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface Candidate {
  id: string;
  name: string;
  email: string;
  phone?: string | null;
  summary?: string | null;
  skills?: string | null;
  experience?: string | null;
  created_at: string;
  updated_at?: string;
  last_indexed_at?: string | null;
}

export type CandidateFormData = Pick<Candidate, 'name' | 'email' | 'phone' | 'summary' | 'skills' | 'experience'>;
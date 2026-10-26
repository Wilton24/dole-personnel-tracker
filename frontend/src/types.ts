export interface Role {
  id: number;
  name: string;
}

export interface ProjectHistoryItem {
  assignment_id: number;
  project_id: number;
  project_name: string;
  project_status: "Ongoing" | "Completed";
  start_date: string;
  end_date?: string | null;
  role: string;
  is_current: boolean;
  is_override: boolean;
}

export interface Personnel {
  id: number;
  first_name: string;
  middle_initial?: string | null;
  last_name: string;
  extension?: string | null;
  full_name: string;
  role: Role;
  contact_number?: string | null;
  email?: string | null;
  control_number?: string | null;
  certificate_number?: string | null;
  date_of_training?: string | null;
  training_valid_until?: string | null;
  notes?: string | null;
  is_active: boolean;
  availability_status: "Available" | "Engaged";
  projects: ProjectHistoryItem[];
  created_at?: string | null;
}

export interface PersonnelBrief {
  id: number;
  full_name: string;
  role: Role;
}

export interface Project {
  id: number;
  name: string;
  address?: string | null;
  start_date: string;
  duration_days?: number | null;
  end_date?: string | null;
  status: "Ongoing" | "Completed";
}

export interface Assignment {
  id: number;
  project_id: number;
  personnel_id: number;
  role_id: number;
  is_override: boolean;
  override_reason?: string | null;
  override_by?: number | null;
  created_at: string;
  personnel: PersonnelBrief;
  role: Role;
}

export interface ProjectDetail extends Project {
  assignments: Assignment[];
}
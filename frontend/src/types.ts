export interface Role {
  id: number;
  name: string;
}

export interface Personnel {
  id: number;
  name: string;
  contact_number?: string | null;
  role: Role;
  status: "Available" | "Engaged";
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
  personnel: Personnel;
  role: Role;
}

export interface ProjectDetail extends Project {
  assignments: Assignment[];
}

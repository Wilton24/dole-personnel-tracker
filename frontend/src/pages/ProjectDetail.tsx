import { useEffect, useState, FormEvent } from "react";
import { useParams } from "react-router-dom";
import api from "../api";
import { ProjectDetail, Personnel, Role } from "../types";
import { StatusBadge } from "../components/StatusBadge";

export default function ProjectDetailPage() {
  const { id } = useParams();
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [personnelList, setPersonnelList] = useState<Personnel[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [isAdmin, setIsAdmin] = useState(false);

  const [personnelId, setPersonnelId] = useState<number | "">("");
  const [roleId, setRoleId] = useState<number | "">("");
  const [overrideReason, setOverrideReason] = useState("");
  const [needsOverride, setNeedsOverride] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    const [projRes, personnelRes, rolesRes, meRes] = await Promise.all([
      api.get(`/projects/${id}`),
      api.get("/personnel/"),
      api.get("/roles/"),
      api.get("/auth/me"),
    ]);
    setProject(projRes.data);
    setPersonnelList(personnelRes.data);
    setRoles(rolesRes.data);
    setIsAdmin(meRes.data.is_admin);
    if (rolesRes.data.length && roleId === "") setRoleId(rolesRes.data[0].id);
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const handleAssign = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await api.post("/assignments/", {
        project_id: Number(id),
        personnel_id: personnelId,
        role_id: roleId,
        override_reason: needsOverride ? overrideReason : undefined,
      });
      setPersonnelId("");
      setOverrideReason("");
      setNeedsOverride(false);
      load();
    } catch (err: any) {
      const detail = err?.response?.data?.detail || "Failed to assign personnel";
      // 409 = personnel is engaged elsewhere -> only admins can see the override path
      if (err?.response?.status === 409 && isAdmin) {
        setNeedsOverride(true);
      }
      setError(detail);
    }
  };

  const handleUnassign = async (assignmentId: number) => {
    await api.delete(`/assignments/${assignmentId}`);
    load();
  };

  if (!project) return <div className="container">Loading...</div>;

  return (
    <div className="container">
      <h2>{project.name}</h2>
      <p className="hint">
        {project.address} &middot; {project.start_date} to {project.end_date || "—"} &middot;{" "}
        <StatusBadge status={project.status} />
      </p>

      <div className="card">
        <h3>Assigned personnel</h3>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Role</th>
              <th>Override?</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {project.assignments.map((a) => (
              <tr key={a.id}>
                <td>{a.personnel.name}</td>
                <td>{a.role.name}</td>
                <td>{a.is_override ? `Yes — ${a.override_reason}` : "No"}</td>
                <td>
                  <button onClick={() => handleUnassign(a.id)}>Unassign</button>
                </td>
              </tr>
            ))}
            {project.assignments.length === 0 && (
              <tr>
                <td colSpan={4} className="hint">No personnel assigned yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Assign personnel</h3>
        <form onSubmit={handleAssign}>
          <label>Personnel</label>
          <select
            value={personnelId}
            onChange={(e) => setPersonnelId(Number(e.target.value))}
            required
          >
            <option value="">Select...</option>
            {personnelList.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.role.name}) — {p.status}
              </option>
            ))}
          </select>
          <label>Role for this project</label>
          <select value={roleId} onChange={(e) => setRoleId(Number(e.target.value))}>
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>

          {needsOverride && (
            <>
              <label>Override reason (required — this personnel is already Engaged)</label>
              <textarea
                value={overrideReason}
                onChange={(e) => setOverrideReason(e.target.value)}
                rows={2}
                required
              />
            </>
          )}

          {error && <div className="error">{error}</div>}
          <button className="primary" type="submit">
            {needsOverride ? "Assign anyway (override)" : "Assign"}
          </button>
        </form>
      </div>
    </div>
  );
}

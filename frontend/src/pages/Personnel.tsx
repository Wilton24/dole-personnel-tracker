import { useEffect, useState, FormEvent, ChangeEvent } from "react";
import api from "../api";
import { Personnel, Role } from "../types";
import { StatusBadge } from "../components/StatusBadge";

const emptyForm = {
  first_name: "",
  middle_initial: "",
  last_name: "",
  extension: "",
  role_id: "",
  contact_number: "",
  email: "",
  control_number: "",
  certificate_number: "",
  date_of_training: "",
  training_valid_until: "",
  notes: "",
};
type FormState = typeof emptyForm;

const blankToNull = (v: string) => (v.trim() === "" ? null : v.trim());

function errorMessage(err: any, fallback: string): string {
  const detail = err?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((d: any) => d.msg).join("; ");
  return fallback;
}

export default function PersonnelPage() {
  const [personnel, setPersonnel] = useState<Personnel[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [search, setSearch] = useState("");
  const [showInactive, setShowInactive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadPersonnel = async () => {
    const res = await api.get("/personnel/", {
      params: { search: search || undefined, include_inactive: showInactive },
    });
    setPersonnel(res.data);
  };

  useEffect(() => {
    api.get("/roles/").then((res) => {
      setRoles(res.data);
      if (res.data.length) setForm((f) => ({ ...f, role_id: String(res.data[0].id) }));
    });
  }, []);

  useEffect(() => {
    loadPersonnel();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, showInactive]);

  const set =
    (key: keyof FormState) =>
      (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
        setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleAdd = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await api.post("/personnel/", {
        first_name: form.first_name.trim(),
        middle_initial: blankToNull(form.middle_initial),
        last_name: form.last_name.trim(),
        extension: blankToNull(form.extension),
        role_id: Number(form.role_id),
        contact_number: blankToNull(form.contact_number),
        email: blankToNull(form.email),
        control_number: blankToNull(form.control_number),
        certificate_number: blankToNull(form.certificate_number),
        date_of_training: blankToNull(form.date_of_training),
        training_valid_until: blankToNull(form.training_valid_until),
        notes: blankToNull(form.notes),
      });
      setForm({ ...emptyForm, role_id: form.role_id });
      loadPersonnel();
    } catch (err: any) {
      setError(errorMessage(err, "Failed to add personnel"));
    }
  };

  const toggleActive = async (p: Personnel) => {
    await api.put(`/personnel/${p.id}`, { is_active: !p.is_active });
    loadPersonnel();
  };

  return (
    <div className="container wide">
      <h2>Personnel</h2>

      <div className="card">
        <h3>Add personnel</h3>
        <form className="form-grid" onSubmit={handleAdd}>
          <div className="field s2">
            <label>First name *</label>
            <input value={form.first_name} onChange={set("first_name")} required />
          </div>
          <div className="field s1">
            <label>M.I.</label>
            <input value={form.middle_initial} onChange={set("middle_initial")} maxLength={2} />
          </div>
          <div className="field s2">
            <label>Last name *</label>
            <input value={form.last_name} onChange={set("last_name")} required />
          </div>
          <div className="field s1">
            <label>Extension</label>
            <input
              value={form.extension}
              onChange={set("extension")}
              placeholder="Jr., III"
            />
          </div>

          <div className="field s2">
            <label>Role *</label>
            <select value={form.role_id} onChange={set("role_id")} required>
              {roles.map((r) => (
                <option key={r.id} value={r.id}>{r.name}</option>
              ))}
            </select>
          </div>
          <div className="field s2">
            <label>Contact number</label>
            <input value={form.contact_number} onChange={set("contact_number")} />
          </div>
          <div className="field s2">
            <label>Email</label>
            <input type="email" value={form.email} onChange={set("email")} />
          </div>

          <div className="field s2">
            <label>Control number</label>
            <input value={form.control_number} onChange={set("control_number")} />
          </div>
          <div className="field s2">
            <label>Certificate number</label>
            <input value={form.certificate_number} onChange={set("certificate_number")} />
          </div>
          <div className="field s2">
            <label>Date of training</label>
            <input type="date" value={form.date_of_training} onChange={set("date_of_training")} />
          </div>

          <div className="field s2">
            <label>Training valid until</label>
            <input
              type="date"
              value={form.training_valid_until}
              onChange={set("training_valid_until")}
            />
          </div>
          <div className="field s6">
            <label>Notes</label>
            <textarea rows={2} value={form.notes} onChange={set("notes")} />
          </div>

          <div className="s6">
            {error && <div className="error" style={{ marginBottom: 8 }}>{error}</div>}
            <button className="primary" type="submit">Add personnel</button>
          </div>
        </form>
      </div>

      <div className="card">
        <div className="toolbar">
          <input
            placeholder="Search name, control no., certificate no."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <label style={{ display: "flex", gap: 6, alignItems: "center", fontWeight: 400 }}>
            <input
              type="checkbox"
              checked={showInactive}
              onChange={(e) => setShowInactive(e.target.checked)}
            />
            Show inactive
          </label>
        </div>

        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Role</th>
              <th>Control / Cert. no.</th>
              <th>Training</th>
              <th>Availability</th>
              <th>Projects</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {personnel.map((p) => (
              <tr key={p.id} style={p.is_active ? undefined : { opacity: 0.55 }}>
                <td>
                  {p.full_name}
                  {p.contact_number && <div className="muted">{p.contact_number}</div>}
                </td>
                <td>{p.role.name}</td>
                <td>
                  <div>{p.control_number || "—"}</div>
                  <div className="muted">{p.certificate_number || "—"}</div>
                </td>
                <td>
                  <div>{p.date_of_training || "—"}</div>
                  {p.training_valid_until && (
                    <div className="muted">valid until {p.training_valid_until}</div>
                  )}
                </td>
                <td><StatusBadge status={p.availability_status} /></td>
                <td>
                  {p.projects.length === 0 && <span className="muted">None yet</span>}
                  {p.projects.map((proj) => (
                    <div className="project-chip" key={proj.assignment_id}>
                      <span>{proj.project_name}</span>
                      <StatusBadge status={proj.project_status} />
                    </div>
                  ))}
                </td>
                <td>
                  <button onClick={() => toggleActive(p)}>
                    {p.is_active ? "Deactivate" : "Reactivate"}
                  </button>
                </td>
              </tr>
            ))}
            {personnel.length === 0 && (
              <tr>
                <td colSpan={7} className="hint">No personnel found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
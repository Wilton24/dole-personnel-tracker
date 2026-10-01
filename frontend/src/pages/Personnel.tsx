import { useEffect, useState, FormEvent } from "react";
import api from "../api";
import { Personnel, Role } from "../types";
import { StatusBadge } from "../components/StatusBadge";

export default function PersonnelPage() {
  const [personnel, setPersonnel] = useState<Personnel[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [name, setName] = useState("");
  const [contact, setContact] = useState("");
  const [roleId, setRoleId] = useState<number | "">("");
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    const [pRes, rRes] = await Promise.all([api.get("/personnel/"), api.get("/roles/")]);
    setPersonnel(pRes.data);
    setRoles(rRes.data);
    if (rRes.data.length && roleId === "") setRoleId(rRes.data[0].id);
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleAdd = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await api.post("/personnel/", {
        name,
        contact_number: contact || null,
        role_id: roleId,
      });
      setName("");
      setContact("");
      load();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to add personnel");
    }
  };

  return (
    <div className="container">
      <h2>Personnel</h2>

      <div className="card">
        <h3>Add personnel</h3>
        <form onSubmit={handleAdd}>
          <label>Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} required />
          <label>Contact number</label>
          <input value={contact} onChange={(e) => setContact(e.target.value)} />
          <label>Role</label>
          <select
            value={roleId}
            onChange={(e) => setRoleId(Number(e.target.value))}
          >
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
          {error && <div className="error">{error}</div>}
          <button className="primary" type="submit">Add</button>
        </form>
      </div>

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Role</th>
              <th>Contact</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {personnel.map((p) => (
              <tr key={p.id}>
                <td>{p.name}</td>
                <td>{p.role.name}</td>
                <td>{p.contact_number || "—"}</td>
                <td><StatusBadge status={p.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

import { useEffect, useState, FormEvent } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import { Project } from "../types";
import { StatusBadge } from "../components/StatusBadge";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [startDate, setStartDate] = useState("");
  const [durationDays, setDurationDays] = useState<number | "">("");
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    const res = await api.get("/projects/");
    setProjects(res.data);
  };

  useEffect(() => {
    load();
  }, []);

  const handleAdd = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await api.post("/projects/", {
        name,
        address: address || null,
        start_date: startDate,
        duration_days: durationDays === "" ? null : durationDays,
        status: "Ongoing",
      });
      setName("");
      setAddress("");
      setStartDate("");
      setDurationDays("");
      load();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to add project");
    }
  };

  const markCompleted = async (id: number) => {
    await api.put(`/projects/${id}`, { status: "Completed" });
    load();
  };

  return (
    <div className="container">
      <h2>Projects</h2>

      <div className="card">
        <h3>Add project</h3>
        <form onSubmit={handleAdd}>
          <label>Project name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} required />
          <label>Address</label>
          <input value={address} onChange={(e) => setAddress(e.target.value)} />
          <label>Start date</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            required
          />
          <label>Duration (days)</label>
          <input
            type="number"
            value={durationDays}
            onChange={(e) =>
              setDurationDays(e.target.value === "" ? "" : Number(e.target.value))
            }
          />
          {error && <div className="error">{error}</div>}
          <button className="primary" type="submit">Add project</button>
        </form>
      </div>

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Address</th>
              <th>Start</th>
              <th>End</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {projects.map((p) => (
              <tr key={p.id}>
                <td><Link to={`/projects/${p.id}`}>{p.name}</Link></td>
                <td>{p.address || "—"}</td>
                <td>{p.start_date}</td>
                <td>{p.end_date || "—"}</td>
                <td><StatusBadge status={p.status} /></td>
                <td>
                  {p.status === "Ongoing" && (
                    <button onClick={() => markCompleted(p.id)}>Mark completed</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

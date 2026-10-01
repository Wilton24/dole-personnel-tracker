import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem("token");

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  if (!isLoggedIn) return null;

  return (
    <div className="navbar">
      <div>
        <Link to="/personnel">Personnel</Link>
        <Link to="/projects">Projects</Link>
      </div>
      <button onClick={logout}>Log out</button>
    </div>
  );
}

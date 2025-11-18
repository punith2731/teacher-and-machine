
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const API_BASE = "http://127.0.0.1:8001";

export default function StudentDashboard() {
  const [chapters, setChapters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/units`)
      .then((res) => res.json())
      .then((data) => {
        setChapters(data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Failed to load units");
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading chapters...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div>
      <h3>Available Chapters</h3>
      {chapters.length === 0 && <p>No chapters found.</p>}
      <ul>
        {chapters.map((c) => (
          <li key={c.unit_id}>
            <Link to={`/chapter/${c.unit_id}`}>{c.title}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

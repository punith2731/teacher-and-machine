
import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8001";

export default function ChapterView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [pages, setPages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/unit-pages/${id}`)
      .then((res) => res.json())
      .then((data) => {
        setPages(data);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load pages");
        setLoading(false);
      });
  }, [id]);

  const handleSpeak = () => {
    const text = pages.map((p) => p.content).join(" ");
    if (!text) return;
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  if (loading) return <p>Loading pages...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div>
      <button onClick={() => navigate(-1)}>&larr; Back</button>
      <h3>Chapter Content (Unit {id})</h3>
      {pages.map((p) => (
        <div key={p.id} style={{ marginBottom: "1rem" }}>
          <h4>Page {p.page_number}</h4>
          <p style={{ whiteSpace: "pre-wrap" }}>{p.content}</p>
        </div>
      ))}
      <button onClick={() => navigate(`/mcq/${id}`)} style={{ marginRight: "1rem" }}>
        Generate MCQ Test
      </button>
      <button onClick={handleSpeak}>Play Text to Speech</button>
    </div>
  );
}

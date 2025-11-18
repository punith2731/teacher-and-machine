
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8001";

export default function MCQTest() {
  const { id } = useParams();
  const [mcqs, setMcqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [answers, setAnswers] = useState({});
  const [score, setScore] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/generate-mcq/${id}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.mcqs) {
          setMcqs(data.mcqs);
        } else {
          setError("No MCQs returned from server");
        }
        setLoading(false);
      })
      .catch((err) => {
        setError("Failed to generate MCQs");
        setLoading(false);
      });
  }, [id]);

  const handleChange = (qIndex, choice) => {
    setAnswers((prev) => ({ ...prev, [qIndex]: choice }));
  };

  const handleSubmit = () => {
    let s = 0;
    mcqs.forEach((q, index) => {
      const chosen = answers[index];
      if (!chosen) return;
      if (chosen.toUpperCase() === (q.correct_answer || "").toUpperCase()) {
        s += 1;
      }
    });
    setScore(s);
  };

  if (loading) return <p>Generating MCQs...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div>
      <h3>MCQ Test for Unit {id}</h3>
      {mcqs.map((q, index) => (
        <div key={index} style={{ marginBottom: "1rem" }}>
          <p><strong>Q{index + 1}.</strong> {q.question}</p>
          {["A", "B", "C", "D"].map((letter) => {
            const key = `option_${letter.toLowerCase()}`;
            return (
              <label key={letter} style={{ display: "block" }}>
                <input
                  type="radio"
                  name={`q${index}`}
                  value={letter}
                  onChange={() => handleChange(index, letter)}
                  checked={answers[index] === letter}
                />
                {" "}{q[key]}
              </label>
            );
          })}
        </div>
      ))}
      <button onClick={handleSubmit}>Submit</button>
      {score !== null && (
        <p>
          Your score: {score} / {mcqs.length}
        </p>
      )}
    </div>
  );
}

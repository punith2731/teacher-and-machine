
import { Routes, Route, Navigate } from "react-router-dom";
import StudentDashboard from "./pages/StudentDashboard";
import ChapterView from "./pages/ChapterView";
import MCQTest from "./pages/MCQTest";
import Navbar from "./components/Navbar";

export default function App() {
  return (
    <div style={{ fontFamily: "sans-serif", padding: "1rem" }}>
      <Navbar />
      <Routes>
        <Route path="/" element={<Navigate to="/student" replace />} />
        <Route path="/student" element={<StudentDashboard />} />
        <Route path="/chapter/:id" element={<ChapterView />} />
        <Route path="/mcq/:id" element={<MCQTest />} />
      </Routes>
    </div>
  );
}

"use client";
import { useEffect, useState } from "react";

interface Question {
  tag: string;
  filename: string;
}

interface SidebarProps {
  onSelect: (question: Question) => void;
}

export default function Sidebar({ onSelect }: SidebarProps) {
  const [questions, setQuestions] = useState<Question[]>([]);

  useEffect(() => {
    async function fetchQuestions() {
      try {
        const res = await fetch("/api/questions");
        if (!res.ok) throw new Error("Failed to fetch questions");
        const data = await res.json();
        setQuestions(data);
      } catch (err) {
        console.error(err);
      }
    }
    fetchQuestions();
  }, []);

  return (
    <aside className="sidebar">
      <button>☰</button>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {questions.map((q) => (
          <li
            key={q.filename}
            style={{ cursor: "pointer", marginBottom: "0.5rem" }}
            onClick={() => onSelect(q)}
          >
            {q.tag}
          </li>
        ))}
      </ul>
    </aside>
  );
}

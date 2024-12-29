"use client";
import Image from "next/image";

interface Question {
  tag: string;
  filename: string;
}

interface QuestionDisplayProps {
  question: Question | null;
  setHint: (text: string) => void;
  setSolution: (text: string) => void;
}

export default function QuestionDisplay({
  question,
  setHint,
  setSolution,
}: QuestionDisplayProps) {
  const handleHintClick = () => {
    // Set hint, clear solution
    setHint("This is a hint from the LLM.");
    setSolution("");
  };

  const handleSolutionClick = () => {
    // Set solution, clear hint
    setSolution("This is a solution from the LLM.");
    setHint("");
  };

  if (!question) {
    return <div style={{ padding: "1rem" }}>No question selected</div>;
  }

  return (
    <div
      className="questionArea"
      style={{ display: "flex", flexDirection: "row", margin: "1rem" }}
    >
      {/* question left, buttons right */}
      <div style={{ flex: 1 }}>
        {question ? (
          <Image
            src={`/questions/${question.filename}`}
            alt={question.tag}
            width={400}
            height={200}
            style={{ maxWidth: "100%", height: "auto" }}
          />
        ) : (
          <p>No question selected</p>
        )}
      </div>

      {/* Buttons on the right */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "1rem",
          marginLeft: "1rem",
        }}
      >
        <button onClick={handleHintClick}>Hint</button>
        <button onClick={handleSolutionClick}>Solution</button>
      </div>
    </div>
  );
}

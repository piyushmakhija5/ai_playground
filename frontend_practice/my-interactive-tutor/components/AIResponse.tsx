"use client";

interface AIResponseProps {
  hint: string;
  solution: string;
}

export default function AIResponse({ hint, solution }: AIResponseProps) {
  return (
    <div className="aiPanel">
      <h3>AI Response</h3>
      {hint && <p>Hint: {hint}</p>}
      {solution && <p>Solution: {solution}</p>}
    </div>
  );
}

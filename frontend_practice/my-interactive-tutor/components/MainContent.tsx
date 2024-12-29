"use client";

import { useState } from "react";
import QuestionDisplay from "./QuestionDisplay";
import CanvasArea from "./CanvasArea";
import AIResponse from "./AIResponse";
import styles from "../app/tutor/styles.module.css";

interface Question {
  tag: string;
  filename: string;
}

export default function MainContent() {
  // e.g., track selectedQuestion here
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);

  return (
    <div className={styles.content}>
      {/* Central area for question + canvas */}
      <div className={styles.centerPane}>
        <QuestionDisplay question={selectedQuestion} />
        <CanvasArea />
      </div>

      {/* AI panel on the right */}
      <AIResponse />
    </div>
  );
}

"use client";

import { useState } from "react";
import Navbar from "@/components/Navbar";
import Sidebar from "@/components/Sidebar";
import QuestionDisplay from "@/components/QuestionDisplay";
import CanvasArea from "@/components/CanvasArea";
import AIResponse from "@/components/AIResponse";

/**
 * Example color palette:
 * - Background: Black (#000000)
 * - Text: White (#FFFFFF)
 * - Accent: Rich Blue (#2C6BED or #1C4BA3)
 */

export default function TutorPage() {
  const [selectedQuestion, setSelectedQuestion] = useState<{
    tag: string;
    filename: string;
  } | null>(null);

  const [hint, setHint] = useState("");
  const [solution, setSolution] = useState("");

  const handleSelectQuestion = (question: { tag: string; filename: string }) => {
    setSelectedQuestion(question);
    setHint("");
    setSolution("");
  };

  // Basic theme colors
  const colors = {
    background: "#FFFFFF",
    text: "#000000",
    accent: "#2C6BED", // or #1C4BA3 for a darker royal blue
    border: "#2C2C2C",
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        backgroundColor: colors.background,
        color: colors.text,
        fontFamily: "sans-serif",
      }}
    >
      {/* NAVBAR */}
      <Navbar
        style={{
          backgroundColor: colors.accent,
          color: "#FFF",
          padding: "1rem",
          fontWeight: "bold",
          borderBottom: `1px solid ${colors.border}`,
        }}
      />

      {/* MAIN AREA */}
      <div style={{ flex: 1, display: "flex" }}>
        {/* SIDEBAR */}
        <Sidebar
          onSelect={handleSelectQuestion}
          style={{
            backgroundColor: "#111", // a deep black/gray
            borderRight: `1px solid ${colors.border}`,
          }}
        />

        {/* CENTER + RIGHT PANE */}
        <div style={{ display: "flex", flex: 1 }}>
          {/* LEFT: QUESTION + CANVAS */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              flex: 1,
              borderRight: `1px solid ${colors.border}`,
            }}
          >
            <QuestionDisplay
              question={selectedQuestion}
              setHint={setHint}
              setSolution={setSolution}
              style={{
                borderBottom: `1px solid ${colors.border}`,
                padding: "1rem",
              }}
            />
            <CanvasArea
              style={{
                padding: "1rem",
              }}
            />
          </div>

          {/* RIGHT: AI RESPONSE */}
          <div
            style={{
              width: "300px",
              minWidth: "250px",
              padding: "1rem",
              borderLeft: `1px solid ${colors.border}`,
            }}
          >
            <AIResponse hint={hint} solution={solution} />
          </div>
        </div>
      </div>
    </div>
  );
}

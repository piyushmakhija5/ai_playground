"use client";
import { useRef } from "react";

export default function CanvasArea() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleDraw = (e: React.MouseEvent) => {
    // Implement your pen drawing logic
  };

  return (
    <div style={{ flex: 1, position: "relative" }}>
      <canvas
        ref={canvasRef}
        onMouseDown={handleDraw}
        style={{
          border: "1px solid #ccc",
          width: "100%",
          height: "600px", // or "100%" if you want it to grow
          backgroundColor: "#fff"
        }}
      />
    </div>
  );
}

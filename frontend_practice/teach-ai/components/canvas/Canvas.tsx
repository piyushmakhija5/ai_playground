'use client'
import { useRef, useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import CanvasControls from './CanvasControls'
import { setupCanvas, handleDrawing } from '@/lib/utils/canvas'

interface CanvasProps {
  onHint: () => void
  onSolution: () => void
}

export default function Canvas({ onHint, onSolution }: CanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isDrawing, setIsDrawing] = useState(false)

  useEffect(() => {
    if (canvasRef.current) {
      setupCanvas(canvasRef.current)
    }
  }, [])

  return (
    <Card className="h-[78%]">
      <CardContent className="p-4 h-full">
        <CanvasControls onHint={onHint} onSolution={onSolution} />
        <canvas
          ref={canvasRef}
          className="border rounded-lg w-full h-[calc(100%-2.5rem)]"
          onMouseDown={() => setIsDrawing(true)}
          onMouseUp={() => setIsDrawing(false)}
          onMouseOut={() => setIsDrawing(false)}
          onMouseMove={(e) => handleDrawing(e, canvasRef.current, isDrawing)}
        />
      </CardContent>
    </Card>
  )
}

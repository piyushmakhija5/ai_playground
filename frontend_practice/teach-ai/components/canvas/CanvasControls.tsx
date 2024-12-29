'use client'

import { HelpCircle, Lightbulb } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface CanvasControlsProps {
  onHint: () => void
  onSolution: () => void
}

export default function CanvasControls({ onHint, onSolution }: CanvasControlsProps) {
  return (
    <div className="flex justify-between mb-2">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">Canvas</span>
      </div>
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onHint}
          className="flex items-center gap-1"
        >
          <HelpCircle className="w-4 h-4" />
          Hint
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={onSolution}
          className="flex items-center gap-1"
        >
          <Lightbulb className="w-4 h-4" />
          Solve
        </Button>
      </div>
    </div>
  )
}

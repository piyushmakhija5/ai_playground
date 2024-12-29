'use client'

import { Card, CardContent } from '@/components/ui/card'

interface AIResponseProps {
  response: string
  loading?: boolean
}

export default function AIResponse({ response, loading }: AIResponseProps) {
  return (
    <Card className="w-[30%]">
      <CardContent className="p-4">
        <h2 className="text-lg font-medium mb-4">AI Response</h2>
        <div className="text-sm">
          {loading ? 'Loading...' : response || 'No response yet'}
        </div>
      </CardContent>
    </Card>
  )
}

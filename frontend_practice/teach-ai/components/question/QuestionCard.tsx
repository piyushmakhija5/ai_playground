'use client'

import Image from 'next/image'
import { Card, CardContent } from '@/components/ui/card'
import { Question } from '@/lib/types'

interface QuestionCardProps {
  question: Question
}

export default function QuestionCard({ question }: QuestionCardProps) {
  return (
    <Card className="mb-4 h-[20%]">
      <CardContent className="p-4">
        <div className="relative w-full h-full">
          <Image
            src={question.imagePath}
            alt={`Question ${question.id}`}
            fill
            style={{ objectFit: 'contain' }}
            priority
          />
        </div>
      </CardContent>
    </Card>
  )
}
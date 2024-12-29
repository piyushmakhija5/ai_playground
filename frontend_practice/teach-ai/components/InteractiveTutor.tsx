'use client'

import { useState, useEffect } from 'react'
import Navbar from './layout/Navbar'
import Sidebar from './layout/Sidebar'
import Canvas from './canvas/Canvas'
import QuestionCard from './question/QuestionCard'
import AIResponse from './ai/AIResponse'
import { Question } from '@/lib/types'
import { getQuestions, selectRandomQuestion } from '@/lib/utils/questions'
import { getHint, getSolution } from '@/services/ai'

export default function InteractiveTutor() {
  const [questions, setQuestions] = useState<Question[]>([])
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null)
  const [aiResponse, setAiResponse] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadQuestions()
  }, [])

  const loadQuestions = async () => {
    try {
      const loadedQuestions = await getQuestions()
      setQuestions(loadedQuestions)
      if (loadedQuestions.length > 0) {
        setCurrentQuestion(selectRandomQuestion(loadedQuestions))
      }
    } catch (error) {
      console.error('Failed to load questions:', error)
    }
  }

  const handleHint = async () => {
    if (!currentQuestion) return
    setLoading(true)
    try {
      const hint = await getHint(currentQuestion.id)
      setAiResponse(hint)
    } catch (error) {
      console.error('Failed to get hint:', error)
    }
    setLoading(false)
  }

  const handleSolution = async () => {
    if (!currentQuestion) return
    setLoading(true)
    try {
      const solution = await getSolution(currentQuestion.id)
      setAiResponse(solution)
    } catch (error) {
      console.error('Failed to get solution:', error)
    }
    setLoading(false)
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="flex p-4 gap-4 h-[calc(100vh-4rem)]">
          <div className="w-[70%]">
            {currentQuestion && <QuestionCard question={currentQuestion} />}
            <Canvas onHint={handleHint} onSolution={handleSolution} />
          </div>
          <AIResponse response={aiResponse} loading={loading} />
        </div>
      </div>
    </div>
  )
}

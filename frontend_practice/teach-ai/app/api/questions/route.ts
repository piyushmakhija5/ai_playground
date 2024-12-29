import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export async function GET() {
  try {
    const questionsDir = path.join(process.cwd(), 'public/questions')
    const files = fs.readdirSync(questionsDir)
    const questions = files
      .filter(file => file.endsWith('.jpg') || file.endsWith('.png'))
      .map(file => ({
        id: file.split('.')[0],
        imagePath: `/questions/${file}`
      }))
    
    return NextResponse.json(questions)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to load questions' },
      { status: 500 }
    )
  }
}

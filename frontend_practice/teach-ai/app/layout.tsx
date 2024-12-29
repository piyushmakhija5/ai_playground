
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Teach.AI',
  description: 'Interactive AI Teaching Assistant',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}


// app/layout.tsx
// app/page.tsx
// app/api/questions/route.ts
// components/InteractiveTutor.tsx
// components/layout/Navbar.tsx
// components/layout/Sidebar.tsx
// components/canvas/Canvas.tsx
// components/canvas/CanvasControls.tsx
// components/question/QuestionCard.tsx
// components/ai/AIResponse.tsx
// lib/types/index.ts
// lib/utils/canvas.ts
// lib/utils/questions.ts
// services/ai.ts
// next.config.js
// tailwind.config.ts
// tsconfig.json

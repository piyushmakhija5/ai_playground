'use client'

import { Menu } from 'lucide-react'

export default function Sidebar() {
  return (
    <div className="w-16 bg-white shadow-md">
      <div className="p-4">
        <Menu className="w-6 h-6 text-gray-600" />
      </div>
    </div>
  )
}

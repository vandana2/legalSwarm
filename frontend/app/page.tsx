'use client'

import FileUpload from '@/components/FileUpload'

export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
            LegalSwarm
          </h1>
          <p className="text-xl text-gray-300">A law firm in your laptop</p>
          <p className="text-gray-400 mt-2">Upload your contract for instant AI-powered risk analysis</p>
        </div>
        <FileUpload />
      </div>
    </main>
  )
}

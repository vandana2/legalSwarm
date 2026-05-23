'use client'

import { useState } from 'react'
import axios from 'axios'

export default function FileUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0])
      setError('')
    }
  }

  const handleUpload = async () => {
    if (!file) return

    if (file.type !== 'application/pdf') {
      setError('Please select a PDF file')
      return
    }

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/upload/contract`,
        formData
      )
      console.log('Upload successful:', response.data)
      setFile(null)
    } catch (err) {
      setError('Upload failed. Please try again.')
      console.error(err)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="bg-slate-800 p-8 rounded-lg border border-slate-700">
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Upload Contract</label>
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="w-full px-4 py-2 bg-slate-700 rounded border border-slate-600 text-white"
        />
      </div>

      {file && (
        <div className="mb-4 p-3 bg-blue-900 text-blue-100 rounded">
          Selected: {file.name}
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-red-900 text-red-100 rounded">
          {error}
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 text-white font-bold py-3 rounded transition"
      >
        {uploading ? 'Uploading...' : 'Upload & Analyze'}
      </button>
    </div>
  )
}

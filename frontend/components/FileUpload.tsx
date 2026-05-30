'use client'

import { useState } from 'react'
import axios from 'axios'

type RiskItem = {
  clause_id?: number
  clause_type?: string
  risk_level?: string
  reason?: string
  recommendation?: string
}

type ExplanationItem = {
  clause_id?: number
  clause_type?: string
  simple_explanation?: string
}

type RedlineItem = {
  clause_id?: number
  clause_type?: string
  risk_level?: string
  suggested_clause?: string
}

type Verdict = {
  risk_score?: number
  verdict?: string
  recommendation?: string
  rationale?: string
}

type AnalysisPayload = {
  verdict?: Verdict
  risk_analysis?: RiskItem[]
  explanations?: ExplanationItem[]
  redlines?: RedlineItem[]
  analysis_summary?: string
}

export default function FileUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<Record<string, unknown> | null>(null)

  const getAnalysis = (data: Record<string, unknown> | null): AnalysisPayload | null => {
    if (!data) return null
    const nested = data.analysis
    if (nested && typeof nested === 'object') {
      return nested as AnalysisPayload
    }
    return data as AnalysisPayload
  }

  const analysis = getAnalysis(result)
  const verdict = analysis?.verdict
  const riskItems = Array.isArray(analysis?.risk_analysis) ? analysis.risk_analysis : []
  const topRisks = riskItems
    .filter((risk) => risk.risk_level === 'CRITICAL' || risk.risk_level === 'HIGH')
    .slice(0, 3)
  const explanations = Array.isArray(analysis?.explanations) ? analysis.explanations.slice(0, 3) : []
  const redlines = Array.isArray(analysis?.redlines)
    ? analysis.redlines
        .filter((item) => item.risk_level === 'CRITICAL' || item.risk_level === 'HIGH')
        .slice(0, 3)
    : []

  const score = typeof verdict?.risk_score === 'number' ? verdict.risk_score : null
  const scoreColor = score === null ? 'text-gray-200' : score >= 8 ? 'text-red-300' : score >= 6 ? 'text-yellow-300' : 'text-green-300'

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

    setAnalyzing(true)
    setError('')
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/contracts/analyze`,
        formData
      )
      setResult(response.data)
    } catch (err) {
      setError('Analysis failed. Please check backend logs and try again.')
      console.error(err)
    } finally {
      setAnalyzing(false)
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
          disabled={analyzing}
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
        disabled={!file || analyzing}
        className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 text-white font-bold py-3 rounded transition"
      >
        {analyzing ? 'Analyzing contract...' : 'Upload & Analyze'}
      </button>

      {result && (
        <div className="mt-8 space-y-4">
          <h3 className="text-lg font-semibold">Contract Analysis</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded bg-slate-900 border border-slate-700">
              <p className="text-sm text-gray-400">Risk score</p>
              <p className={`text-3xl font-bold mt-1 ${scoreColor}`}>{score ?? 'N/A'}{score !== null ? '/10' : ''}</p>
              <p className="text-sm text-gray-300 mt-2">{verdict?.verdict ?? 'Verdict unavailable'}</p>
            </div>

            <div className="p-4 rounded bg-slate-900 border border-slate-700">
              <p className="text-sm text-gray-400">Final recommendation</p>
              <p className="text-sm text-gray-100 mt-2">{verdict?.recommendation ?? 'Recommendation unavailable'}</p>
            </div>
          </div>

          <div className="p-4 rounded bg-slate-900 border border-slate-700">
            <p className="text-sm text-gray-400 mb-2">Top risks</p>
            {topRisks.length === 0 ? (
              <p className="text-sm text-gray-300">No critical/high risks found in the response.</p>
            ) : (
              <div className="space-y-3">
                {topRisks.map((risk, index) => (
                  <div key={`${risk.clause_id}-${index}`} className="p-3 rounded bg-slate-800 border border-slate-700">
                    <p className="text-sm font-semibold text-white">{risk.risk_level} - {risk.clause_type ?? 'General clause'}</p>
                    <p className="text-sm text-gray-300 mt-1">{risk.reason ?? 'Reason not provided'}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="p-4 rounded bg-slate-900 border border-slate-700">
            <p className="text-sm text-gray-400 mb-2">Plain-English explanation</p>
            {explanations.length === 0 ? (
              <p className="text-sm text-gray-300">No simplified explanations were returned.</p>
            ) : (
              <div className="space-y-3">
                {explanations.map((item, index) => (
                  <div key={`${item.clause_id}-${index}`} className="p-3 rounded bg-slate-800 border border-slate-700">
                    <p className="text-xs uppercase tracking-wide text-blue-300">{item.clause_type ?? 'General'}</p>
                    <p className="text-sm text-gray-200 mt-1 whitespace-pre-line">{item.simple_explanation ?? 'Explanation missing'}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="p-4 rounded bg-slate-900 border border-slate-700">
            <p className="text-sm text-gray-400 mb-2">Suggested redlines</p>
            {redlines.length === 0 ? (
              <p className="text-sm text-gray-300">No redlines found for critical/high-risk clauses.</p>
            ) : (
              <div className="space-y-3">
                {redlines.map((item, index) => (
                  <div key={`${item.clause_id}-${index}`} className="p-3 rounded bg-slate-800 border border-slate-700">
                    <p className="text-sm font-semibold text-white">{item.clause_type ?? 'General clause'} ({item.risk_level ?? 'UNKNOWN'})</p>
                    <p className="text-sm text-gray-300 mt-1">{item.suggested_clause ?? 'Suggested language not provided'}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {verdict?.rationale && (
            <div className="p-4 rounded bg-slate-900 border border-slate-700">
              <p className="text-sm text-gray-400">Why this verdict</p>
              <p className="text-sm text-gray-200 mt-2 whitespace-pre-line">{verdict.rationale}</p>
            </div>
          )}

          <div className="p-4 rounded bg-slate-900 border border-slate-700 text-sm">
            <details>
              <summary className="cursor-pointer text-gray-300">Raw API response</summary>
              <pre className="mt-3 overflow-auto max-h-[320px]">{JSON.stringify(result, null, 2)}</pre>
            </details>
          </div>
        </div>
      )}
    </div>
  )
}

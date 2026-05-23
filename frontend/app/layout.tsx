import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'LegalSwarm - Contract Review Platform',
  description: 'AI-powered contract review & risk analysis for Indian startups',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gradient-to-br from-slate-900 to-slate-800 text-white min-h-screen">
        {children}
      </body>
    </html>
  )
}

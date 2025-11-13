import React, { useState } from 'react'
import { TechnicalImplementation } from '../../data/portfolioData'
import { CheckIcon, CopyIcon } from './icons'

export const CodeBlock: React.FC<TechnicalImplementation> = ({ fileName, language, code }) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    const textToCopy = code.trim()

    try {
      if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(textToCopy)
      } else {
        throw new Error('Clipboard API not available')
      }
    } catch {
      const textArea = document.createElement('textarea')
      textArea.value = textToCopy
      document.body.appendChild(textArea)
      textArea.select()
      try {
        document.execCommand('copy')
      } finally {
        document.body.removeChild(textArea)
      }
    }

    setCopied(true)
    window.setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden my-4 border border-gray-700">
      <div className="flex justify-between items-center px-4 py-2 bg-gray-900 text-gray-400 text-xs">
        <span className="font-mono">{fileName}</span>
        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center gap-1.5 text-gray-400 hover:text-white transition-colors"
        >
          {copied ? <CheckIcon /> : <CopyIcon />}
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <div className="p-4 text-sm overflow-x-auto">
        <pre>
          <code className={`language-${language}`}>{code.trim()}</code>
        </pre>
      </div>
    </div>
  )
}

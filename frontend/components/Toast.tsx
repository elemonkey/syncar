'use client'

import { useEffect } from 'react'

interface ToastProps {
  message: string
  type: 'success' | 'error' | 'info'
  onClose: () => void
  duration?: number
}

export function Toast({ message, type, onClose, duration = 3000 }: ToastProps) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose()
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [duration, onClose])

  const typeStyles = {
    success: 'bg-green-500/20 border-green-500 text-green-400',
    error: 'bg-red-500/20 border-red-500 text-red-400',
    info: 'bg-blue-500/20 border-blue-500 text-blue-400',
  }

  const icons = {
    success: '✅',
    error: '❌',
    info: 'ℹ️',
  }

  return (
    <div className="fixed top-24 right-6 z-50 animate-in slide-in-from-right duration-300">
      <div className={`
        p-4 rounded-lg border-2 shadow-2xl backdrop-blur-sm min-w-[300px] max-w-[400px]
        ${typeStyles[type]}
      `}>
        <div className="flex items-start gap-3">
          <span className="text-xl flex-shrink-0">{icons[type]}</span>
          <div className="flex-1">
            <p className="whitespace-pre-line">{message}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors flex-shrink-0"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  )
}

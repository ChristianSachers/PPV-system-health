/**
 * Error Message Component
 *
 * User-friendly error display with retry functionality.
 * Designed for system health monitoring error scenarios.
 */

import React from 'react'
import { AlertCircle, RefreshCw } from 'lucide-react'
import { BaseComponentProps } from '@/types'

interface ErrorMessageProps extends BaseComponentProps {
  error: string
  onRetry?: () => void
  retryLabel?: string
  variant?: 'default' | 'compact'
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({
  error,
  onRetry,
  retryLabel = 'Retry',
  variant = 'default',
  className = '',
  'data-testid': testId = 'error-message'
}) => {
  const isCompact = variant === 'compact'

  return (
    <div
      className={`
        ${isCompact ? 'p-3' : 'p-6'}
        bg-red-50 border border-red-200 rounded-lg
        ${className}
      `}
      data-testid={testId}
      role="alert"
    >
      <div className={`flex ${isCompact ? 'items-center' : 'items-start'} gap-3`}>
        <AlertCircle
          className={`${isCompact ? 'w-4 h-4' : 'w-5 h-5'} text-red-600 flex-shrink-0 mt-0.5`}
        />

        <div className="flex-1 min-w-0">
          <h3 className={`${isCompact ? 'text-sm' : 'text-base'} font-medium text-red-800`}>
            {isCompact ? 'Error' : 'Failed to load campaigns'}
          </h3>
          <p className={`${isCompact ? 'text-xs' : 'text-sm'} text-red-700 mt-1`}>
            {error}
          </p>
        </div>

        {onRetry && (
          <button
            onClick={onRetry}
            className={`
              inline-flex items-center gap-2
              ${isCompact ? 'px-2 py-1 text-xs' : 'px-3 py-2 text-sm'}
              bg-red-600 text-white rounded-md
              hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2
              transition-colors
            `}
            aria-label={`${retryLabel} loading data`}
          >
            <RefreshCw className={`${isCompact ? 'w-3 h-3' : 'w-4 h-4'}`} />
            {retryLabel}
          </button>
        )}
      </div>
    </div>
  )
}

export default ErrorMessage
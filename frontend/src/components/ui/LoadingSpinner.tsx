/**
 * Loading Spinner Component
 *
 * Reusable loading indicator for async operations throughout the dashboard.
 * Supports different sizes and contexts for system health monitoring.
 */

import React from 'react'
import { BaseComponentProps } from '@/types'

interface LoadingSpinnerProps extends BaseComponentProps {
  size?: 'small' | 'medium' | 'large'
  message?: string
  inline?: boolean
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  message,
  inline = false,
  className = '',
  'data-testid': testId = 'loading-spinner'
}) => {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-6 w-6',
    large: 'h-8 w-8'
  }

  const containerClasses = inline
    ? 'inline-flex items-center'
    : 'flex flex-col items-center justify-center space-y-3'

  return (
    <div className={`${containerClasses} ${className}`} data-testid={testId}>
      <div
        className={`loading-spinner ${sizeClasses[size]}`}
        role="status"
        aria-label={message || 'Loading'}
      />
      {message && (
        <span className="text-sm text-gray-600 animate-pulse">
          {message}
        </span>
      )}
    </div>
  )
}

export default LoadingSpinner
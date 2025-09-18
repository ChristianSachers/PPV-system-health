/**
 * Search and Filters Component
 *
 * Provides filtering and search capabilities for campaign investigation workflow.
 * Implements TDD specifications for campaign filtering by type, status, and fulfillment.
 */

import React, { useState, useCallback } from 'react'
import { Search, Filter, X } from 'lucide-react'
import { CampaignFilters, BaseComponentProps } from '@/types'

interface SearchAndFiltersProps extends BaseComponentProps {
  filters: CampaignFilters
  onFiltersChange: (filters: CampaignFilters) => void
  campaignCount: number
}

const SearchAndFilters: React.FC<SearchAndFiltersProps> = ({
  filters,
  onFiltersChange,
  campaignCount,
  className = '',
  'data-testid': testId = 'search-and-filters'
}) => {
  const [isFilterOpen, setIsFilterOpen] = useState(false)

  /**
   * Handle search input changes with debouncing
   */
  const handleSearchChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    onFiltersChange({
      ...filters,
      search: event.target.value,
    })
  }, [filters, onFiltersChange])

  /**
   * Handle filter changes
   */
  const handleFilterChange = useCallback((key: keyof CampaignFilters, value: any) => {
    onFiltersChange({
      ...filters,
      [key]: value,
    })
  }, [filters, onFiltersChange])

  /**
   * Clear all filters
   */
  const handleClearFilters = useCallback(() => {
    onFiltersChange({
      type: 'all',
      status: 'all',
      fulfillment_status: 'all',
      search: '',
    })
  }, [onFiltersChange])

  /**
   * Check if any filters are active
   */
  const hasActiveFilters =
    filters.type !== 'all' ||
    filters.status !== 'all' ||
    filters.fulfillment_status !== 'all' ||
    (filters.search && filters.search.length > 0)

  return (
    <div className={`space-y-4 ${className}`} data-testid={testId}>
      {/* Search and Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search Input */}
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Search campaigns..."
            value={filters.search || ''}
            onChange={handleSearchChange}
            className="
              block w-full pl-10 pr-3 py-2
              border border-gray-300 rounded-md
              placeholder-gray-500 text-gray-900
              focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500
              text-sm
            "
            aria-label="Search campaigns"
            data-testid="campaign-search-input"
          />
        </div>

        {/* Filter Toggle Button */}
        <button
          onClick={() => setIsFilterOpen(!isFilterOpen)}
          className={`
            inline-flex items-center px-4 py-2 border border-gray-300 rounded-md
            text-sm font-medium text-gray-700 bg-white
            hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
            ${hasActiveFilters ? 'border-primary-300 bg-primary-50' : ''}
          `}
          aria-label="Toggle filters"
          aria-expanded={isFilterOpen}
        >
          <Filter className="h-4 w-4 mr-2" />
          Filters
          {hasActiveFilters && (
            <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
              Active
            </span>
          )}
        </button>

        {/* Results Count */}
        <div className="flex items-center text-sm text-gray-600">
          <span>{campaignCount} campaigns</span>
        </div>
      </div>

      {/* Filter Panel */}
      {isFilterOpen && (
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Campaign Type Filter */}
            <div>
              <label htmlFor="type-filter" className="block text-sm font-medium text-gray-700 mb-1">
                Type
              </label>
              <select
                id="type-filter"
                value={filters.type || 'all'}
                onChange={(e) => handleFilterChange('type', e.target.value)}
                className="
                  block w-full px-3 py-2 border border-gray-300 rounded-md
                  text-sm text-gray-900 bg-white
                  focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500
                "
                aria-label="Filter by type"
              >
                <option value="all">All Types</option>
                <option value="campaign">Campaigns</option>
                <option value="deal">Deals</option>
              </select>
            </div>

            {/* Campaign Status Filter */}
            <div>
              <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                id="status-filter"
                value={filters.status || 'all'}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="
                  block w-full px-3 py-2 border border-gray-300 rounded-md
                  text-sm text-gray-900 bg-white
                  focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500
                "
                aria-label="Filter by status"
              >
                <option value="all">All Status</option>
                <option value="running">Running</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            {/* Fulfillment Status Filter */}
            <div>
              <label htmlFor="fulfillment-filter" className="block text-sm font-medium text-gray-700 mb-1">
                Fulfillment
              </label>
              <select
                id="fulfillment-filter"
                value={filters.fulfillment_status || 'all'}
                onChange={(e) => handleFilterChange('fulfillment_status', e.target.value)}
                className="
                  block w-full px-3 py-2 border border-gray-300 rounded-md
                  text-sm text-gray-900 bg-white
                  focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500
                "
                aria-label="Filter by fulfillment status"
              >
                <option value="all">All Fulfillment</option>
                <option value="excellent">Excellent (≥100%)</option>
                <option value="good">Good (98-99.9%)</option>
                <option value="warning">Warning (95-98%)</option>
                <option value="critical">Critical (&lt;95%)</option>
              </select>
            </div>
          </div>

          {/* Filter Actions */}
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
            <div className="text-sm text-gray-600">
              {hasActiveFilters ? 'Filters applied' : 'No filters applied'}
            </div>

            <div className="flex space-x-2">
              {hasActiveFilters && (
                <button
                  onClick={handleClearFilters}
                  className="inline-flex items-center px-3 py-1 text-sm text-gray-700 hover:text-gray-900"
                  aria-label="Clear all filters"
                >
                  <X className="h-3 w-3 mr-1" />
                  Clear
                </button>
              )}

              <button
                onClick={() => setIsFilterOpen(false)}
                className="btn btn-primary text-sm"
                aria-label="Close filters"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SearchAndFilters
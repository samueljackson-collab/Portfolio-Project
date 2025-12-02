/**
 * SidebarNav - Windows XP-style sidebar navigation
 *
 * Features:
 * - Large clickable areas
 * - Icons with text labels
 * - Clear visual hierarchy
 * - Folder tree structure
 * - Photo counts next to folders
 */

import React, { useState } from 'react'

export interface NavItem {
  id: string
  label: string
  icon: string
  count?: number
  children?: NavItem[]
  onClick?: () => void
}

interface SidebarNavProps {
  items: NavItem[]
  activeId?: string
  onItemClick?: (item: NavItem) => void
  className?: string
}

export const SidebarNav: React.FC<SidebarNavProps> = ({
  items,
  activeId,
  onItemClick,
  className = '',
}) => {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})

  const toggleExpand = (id: string) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  const handleItemClick = (item: NavItem) => {
    if (item.children && item.children.length > 0) {
      toggleExpand(item.id)
    }
    if (item.onClick) {
      item.onClick()
    }
    if (onItemClick) {
      onItemClick(item)
    }
  }

  const renderItem = (item: NavItem, level = 0) => {
    const isActive = activeId === item.id
    const isExpanded = expanded[item.id]
    const hasChildren = item.children && item.children.length > 0
    const indentation = { paddingLeft: `${16 + level * 16}px` }

    return (
      <div key={item.id} className="w-full">
        <button
          onClick={() => handleItemClick(item)}
          className={`
            w-full flex items-center gap-3 py-3 pr-4 text-left text-lg border-l-4
            transition-colors duration-150
            hover:bg-blue-50 focus:outline-none focus:bg-blue-100
            ${isActive ? 'bg-blue-100 border-blue-900 font-semibold' : 'border-transparent'}
          `}
          style={indentation}
        >
          {/* Expand/collapse indicator */}
          {hasChildren && (
            <span className="text-gray-600 text-sm font-bold w-4">
              {isExpanded ? '▼' : '▶'}
            </span>
          )}

          {/* Icon */}
          <span className="text-2xl" role="img" aria-label={item.label}>
            {item.icon}
          </span>

          {/* Label */}
          <span className="flex-1 font-medium text-gray-800">{item.label}</span>

          {/* Count badge */}
          {item.count !== undefined && (
            <span className="bg-gray-200 text-gray-700 px-3 py-1 rounded-full text-base font-semibold min-w-[40px] text-center">
              {item.count}
            </span>
          )}
        </button>

        {/* Children */}
        {hasChildren && isExpanded && (
          <div className="border-l-2 border-gray-200 ml-6">
            {item.children!.map((child) => renderItem(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  return (
    <nav
      className={`
        bg-white border-r-2 border-gray-300
        overflow-y-auto
        ${className}
      `}
      aria-label="Photo navigation"
    >
      <div className="py-4">
        {items.map((item) => renderItem(item))}
      </div>
    </nav>
  )
}

import React from 'react'
import clsx from 'clsx'

type NavItem = {
  id: string
  label: string
  icon?: React.ReactNode
  children?: NavItem[]
}

type Props = {
  items: NavItem[]
  activeId: string
  onSelect: (id: string) => void
}

export const SidebarNav: React.FC<Props> = ({ items, activeId, onSelect }) => {
  const renderItems = (navItems: NavItem[], level = 0) => {
    return navItems.map((item) => {
      const isActive = activeId === item.id
      return (
        <div key={item.id}>
          <button
            type="button"
            onClick={() => onSelect(item.id)}
            className={clsx(
              'flex w-full items-center gap-3 rounded-r-full py-3 pr-4 text-left text-lg transition-colors focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-300',
              isActive ? 'bg-blue-100 font-semibold text-blue-900' : 'text-gray-700 hover:bg-blue-50',
            )}
            style={{ paddingLeft: `${1 + level}rem` }}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
          {item.children && item.children.length > 0 && (
            <div className="mt-1 border-l-2 border-blue-100 pl-1">
              {renderItems(item.children, level + 1)}
            </div>
          )}
        </div>
      )
    })
  }

  return <nav className="space-y-2" aria-label="Photo navigation">{renderItems(items)}</nav>
}

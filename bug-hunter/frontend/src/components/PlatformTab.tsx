import type { Platform } from '../api/types'

interface PlatformConfig {
  label: string
  border: string
  text: string
  badge: string
  icon: React.FC<{ className?: string }>
}

function AndroidIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M17.523 15.341A5 5 0 0 1 12 19a5 5 0 0 1-5.523-3.659L3 14v-4l3.477-1.341A5 5 0 0 1 12 5a5 5 0 0 1 5.523 3.659L21 10v4l-3.477 1.341zM9 11a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm6 0a1 1 0 1 0 0 2 1 1 0 0 0 0-2zM8.5 4.5l-1.5-2.5M15.5 4.5l1.5-2.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" fill="none" />
      <circle cx="9" cy="11" r="1" />
      <circle cx="15" cy="11" r="1" />
    </svg>
  )
}

function IOSIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.71 19.5C17.88 20.74 17 21.95 15.66 21.97C14.32 22 13.89 21.18 12.37 21.18C10.84 21.18 10.37 21.95 9.1 22C7.78 22.05 6.8 20.68 5.96 19.47C4.25 17 2.94 12.45 4.7 9.39C5.57 7.87 7.13 6.91 8.82 6.88C10.1 6.86 11.32 7.75 12.11 7.75C12.89 7.75 14.37 6.68 15.92 6.84C16.57 6.87 18.39 7.1 19.56 8.82C19.47 8.88 17.39 10.1 17.41 12.63C17.44 15.65 20.06 16.66 20.09 16.67C20.06 16.74 19.67 18.11 18.71 19.5ZM13 3.5C13.73 2.67 14.94 2.04 15.94 2C16.07 3.17 15.6 4.35 14.9 5.19C14.21 6.04 13.07 6.7 11.95 6.61C11.8 5.46 12.36 4.26 13 3.5Z" />
    </svg>
  )
}

function WindowsIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M3 5.557L10.396 4.5V11.5H3V5.557zM11.328 4.357L21 3V11.5H11.328V4.357zM3 12.5H10.396V19.5L3 18.443V12.5zM11.328 12.5H21V21L11.328 19.643V12.5z" />
    </svg>
  )
}

function MacOSIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm0 2c4.418 0 8 3.582 8 8s-3.582 8-8 8-8-3.582-8-8 3.582-8 8-8zm-1 3v2H9v2h2v5h2v-5h2v-2h-2V7h-2z" />
    </svg>
  )
}

function WebIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8}>
      <circle cx="12" cy="12" r="9" />
      <path strokeLinecap="round" d="M3.6 9h16.8M3.6 15h16.8M12 3a14.4 14.4 0 0 1 0 18M12 3a14.4 14.4 0 0 0 0 18" />
    </svg>
  )
}

export const PLATFORM_CONFIG: Record<Platform, PlatformConfig> = {
  android: {
    label: 'Android',
    border: 'border-green-500',
    text: 'text-green-600',
    badge: 'bg-green-100 text-green-700',
    icon: AndroidIcon,
  },
  ios: {
    label: 'iOS',
    border: 'border-gray-500',
    text: 'text-gray-700',
    badge: 'bg-gray-100 text-gray-700',
    icon: IOSIcon,
  },
  windows: {
    label: 'Windows',
    border: 'border-sky-500',
    text: 'text-sky-600',
    badge: 'bg-sky-100 text-sky-700',
    icon: WindowsIcon,
  },
  macos: {
    label: 'macOS',
    border: 'border-purple-500',
    text: 'text-purple-600',
    badge: 'bg-purple-100 text-purple-700',
    icon: MacOSIcon,
  },
  web: {
    label: 'Web',
    border: 'border-blue-500',
    text: 'text-blue-600',
    badge: 'bg-blue-100 text-blue-700',
    icon: WebIcon,
  },
}

export const PLATFORMS: Platform[] = ['android', 'ios', 'windows', 'macos', 'web']

interface Props {
  active: Platform
  onChange: (p: Platform) => void
}

export function PlatformTabBar({ active, onChange }: Props) {
  return (
    <div className="border-b border-gray-200 bg-white">
      <nav className="-mb-px flex overflow-x-auto" role="tablist">
        {PLATFORMS.map(p => {
          const cfg = PLATFORM_CONFIG[p]
          const Icon = cfg.icon
          const isActive = active === p
          return (
            <button
              key={p}
              role="tab"
              aria-selected={isActive}
              onClick={() => onChange(p)}
              className={`flex items-center gap-2 whitespace-nowrap px-5 py-3.5 border-b-2 font-medium text-sm transition-all duration-150 ${
                isActive
                  ? `${cfg.border} ${cfg.text}`
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Icon className="w-4 h-4" />
              {cfg.label}
            </button>
          )
        })}
      </nav>
    </div>
  )
}

export function PlatformBadge({ platform }: { platform: string }) {
  const p = platform as Platform
  const cfg = PLATFORM_CONFIG[p]
  if (!cfg) return <span className="text-xs font-medium text-gray-500">{platform}</span>
  const Icon = cfg.icon
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold ${cfg.badge}`}>
      <Icon className="w-3 h-3" />
      {cfg.label}
    </span>
  )
}

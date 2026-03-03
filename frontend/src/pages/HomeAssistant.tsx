/**
 * Home Assistant Dashboard Page
 *
 * Interactive smart home dashboard with fully functional tab navigation.
 * Tabs: Overview · Lights · Climate · Security · System · Remote Connect · Settings
 *
 * Code-review fixes applied in this revision:
 *  - Moved static data arrays outside the component (prevents re-creation on render)
 *  - Light status text is now derived from state (was stale string)
 *  - Quick-action buttons are now wired to real state mutations
 *  - h-30 / w-15 replaced with explicit pixel values (Tailwind v4 compat)
 *  - All icon-only buttons have aria-label attributes
 *  - Toggle buttons use role="switch" + aria-checked
 *  - Settings persisted to localStorage; reset button clears them
 *  - Tooltip component used throughout for protocol / service explanations
 */

import React, { useState, useCallback } from 'react'
import { Tooltip } from '../components/Tooltip'

// ─── Interfaces ───────────────────────────────────────────────────────────────

interface Light {
  id: string
  name: string
  brightness: number // 0-100
  colorTemp: 'warm' | 'neutral' | 'cool'
  isOn: boolean
}

interface Sensor {
  id: string
  location: string
  hasMotion: boolean
  lastTriggered?: string
}

interface HomelabService {
  id: string
  name: string
  status: 'online' | 'warning' | 'offline'
  statusText: string
  description: string
  cpu?: number
  memory?: number
}

interface SshHost {
  id: string
  name: string
  hostname: string
  ip: string
  user: string
  port: number
  description: string
  status: 'online' | 'warning' | 'offline'
}

interface WebUI {
  id: string
  name: string
  url: string
  description: string
  icon: string
  status: 'online' | 'warning' | 'offline'
}

interface VpnTunnel {
  id: string
  name: string
  protocol: string
  protocolDescription: string
  peer: string
  tunnelIp: string
  status: 'connected' | 'disconnected' | 'connecting'
  rxBytes: string
  txBytes: string
  lastHandshake: string
}

interface DashboardSettings {
  temperatureUnit: 'F' | 'C'
  autoRefresh: boolean
  refreshIntervalSeconds: number
  costPerKwh: number
  currency: string
  compactMode: boolean
  showEnergyCard: boolean
  showMediaCard: boolean
  alertThreshold: number
}

// ─── Static data (outside component — no re-creation on each render) ──────────

const SENSORS: Sensor[] = [
  { id: '1', location: 'Living Room', hasMotion: false },
  { id: '2', location: 'Kitchen', hasMotion: true, lastTriggered: '2 min ago' },
  { id: '3', location: 'Bedroom', hasMotion: false },
  { id: '4', location: 'Garage', hasMotion: false },
]

const SERVICES: HomelabService[] = [
  {
    id: '1',
    name: 'Proxmox VE',
    status: 'online',
    statusText: 'Online',
    description:
      'Type-1 bare-metal hypervisor built on Debian. Runs KVM virtual machines and lightweight LXC containers. Managed via web UI on port 8006.',
    cpu: 18,
    memory: 62,
  },
  {
    id: '2',
    name: 'TrueNAS SCALE',
    status: 'online',
    statusText: 'Online',
    description:
      'ZFS-based NAS OS (Debian fork). Provides SMB, NFS, and iSCSI shares. 48 TB raw storage across a 6-drive RAIDZ2 pool with automatic checksums and snapshots.',
    cpu: 4,
    memory: 31,
  },
  {
    id: '3',
    name: 'PostgreSQL',
    status: 'online',
    statusText: 'Online',
    description:
      'Primary relational database running in a Proxmox VM. Streaming replication to a standby replica for HA. Monitored via Prometheus pg_exporter.',
    cpu: 8,
    memory: 45,
  },
  {
    id: '4',
    name: 'Backup Server',
    status: 'warning',
    statusText: 'High Load',
    description:
      'Differential backup target using Restic with B2 cloud offsite sync. Currently processing nightly snapshot — elevated CPU/memory is expected during this window.',
    cpu: 72,
    memory: 88,
  },
]

const SSH_HOSTS: SshHost[] = [
  {
    id: '1',
    name: 'Proxmox VE',
    hostname: 'proxmox.homelab.local',
    ip: '192.168.1.100',
    user: 'root',
    port: 22,
    description:
      'Primary hypervisor. Manages all VMs and LXC containers via KVM. Connect here to run qm/pct commands or troubleshoot guest VMs.',
    status: 'online',
  },
  {
    id: '2',
    name: 'TrueNAS SCALE',
    hostname: 'truenas.homelab.local',
    ip: '192.168.1.101',
    user: 'admin',
    port: 22,
    description:
      'ZFS NAS storage server. Connect to run zpool status, zfs list, or manage datasets and shares from the CLI.',
    status: 'online',
  },
  {
    id: '3',
    name: 'Pi-hole',
    hostname: 'pihole.homelab.local',
    ip: '192.168.1.103',
    user: 'pi',
    port: 22,
    description:
      'Network-level DNS ad blocker and DHCP server. Connect to edit blocklists, check pihole-FTL logs, or update gravity.',
    status: 'online',
  },
  {
    id: '4',
    name: 'Backup Server',
    hostname: 'backup.homelab.local',
    ip: '192.168.1.102',
    user: 'admin',
    port: 2222,
    description:
      'Off-site backup target running Restic with B2 cloud sync. Non-standard port 2222 — currently processing nightly snapshot.',
    status: 'warning',
  },
]

const WEB_UIS: WebUI[] = [
  {
    id: '1',
    name: 'Proxmox VE',
    url: 'https://192.168.1.100:8006',
    description:
      'Manage VMs and LXC containers, configure storage pools, monitor cluster health, and access the built-in VNC/SPICE console for guest VMs.',
    icon: '⚙️',
    status: 'online',
  },
  {
    id: '2',
    name: 'TrueNAS SCALE',
    url: 'https://192.168.1.101',
    description:
      'Configure ZFS datasets, SMB/NFS/iSCSI shares, view S.M.A.R.T. drive health, manage snapshots, and set replication tasks.',
    icon: '🗄️',
    status: 'online',
  },
  {
    id: '3',
    name: 'Grafana',
    url: 'http://192.168.1.104:3000',
    description:
      'Visualize Prometheus metrics for all homelab nodes. Pre-built dashboards for CPU, memory, network I/O, disk utilisation, and application-level metrics.',
    icon: '📊',
    status: 'online',
  },
  {
    id: '4',
    name: 'Pi-hole Admin',
    url: 'http://192.168.1.103/admin',
    description:
      'DNS sinkhole admin console. Shows blocked query stats, top domains, per-client activity, DHCP lease table, and blocklist management.',
    icon: '🛡️',
    status: 'online',
  },
  {
    id: '5',
    name: 'Portainer',
    url: 'http://192.168.1.105:9000',
    description:
      'Web UI for Docker and Docker Swarm. Deploy stacks from Compose files, inspect running containers, tail live logs, and manage volumes and networks.',
    icon: '🐳',
    status: 'online',
  },
  {
    id: '6',
    name: 'Netdata',
    url: 'http://192.168.1.106:19999',
    description:
      'Real-time performance and health monitoring with per-second granularity. Built-in anomaly detection, alert history, and zero-configuration auto-discovery.',
    icon: '📈',
    status: 'online',
  },
]

const VPN_TUNNELS: VpnTunnel[] = [
  {
    id: '1',
    name: 'WireGuard (Primary)',
    protocol: 'WireGuard',
    protocolDescription:
      'Modern VPN protocol using Curve25519 key exchange and ChaCha20-Poly1305 AEAD encryption. Implemented as a Linux kernel module — roughly 4,000 lines of auditable code vs. OpenVPN\'s 70,000+. Typically 2–4× faster than OpenVPN due to kernel-space processing.',
    peer: 'vpn.homelab.example.com:51820',
    tunnelIp: '10.10.0.2/24',
    status: 'connected',
    rxBytes: '1.2 GB',
    txBytes: '340 MB',
    lastHandshake: '14 seconds ago',
  },
  {
    id: '2',
    name: 'OpenVPN (Fallback)',
    protocol: 'OpenVPN',
    protocolDescription:
      'Battle-tested SSL/TLS VPN using the OpenSSL library with AES-256-GCM encryption. Operates in user-space (slower than WireGuard) but supports TCP mode for bypassing restrictive firewalls. Widely supported on all platforms and devices.',
    peer: 'vpn.homelab.example.com:1194',
    tunnelIp: '10.20.0.2/24',
    status: 'disconnected',
    rxBytes: '0 B',
    txBytes: '0 B',
    lastHandshake: 'Never',
  },
]

const PROTOCOL_LEGEND = [
  {
    term: 'SSH',
    desc: 'Secure Shell — encrypted terminal access (default port 22). Uses public-key cryptography (Ed25519 / RSA) for passwordless auth.',
  },
  {
    term: 'WireGuard',
    desc: 'Modern VPN. Curve25519 key exchange + ChaCha20-Poly1305 encryption. ~4,000 lines of auditable kernel code.',
  },
  {
    term: 'ZFS',
    desc: 'Copy-on-write filesystem with per-block checksums, snapshots, send/receive replication, transparent compression, and RAIDZ.',
  },
  {
    term: 'KVM',
    desc: 'Kernel-based Virtual Machine. Linux kernel module that enables full hardware virtualisation. Used by Proxmox VE.',
  },
  {
    term: 'LXC',
    desc: 'Linux Containers — OS-level virtualisation sharing the host kernel. Near-native performance; lighter than full VMs.',
  },
  {
    term: 'SMB/CIFS',
    desc: 'Server Message Block — Windows-native file-sharing protocol. Used by TrueNAS for Windows/macOS network drive mounts.',
  },
]

const DEFAULT_SETTINGS: DashboardSettings = {
  temperatureUnit: 'F',
  autoRefresh: false,
  refreshIntervalSeconds: 30,
  costPerKwh: 0.12,
  currency: 'USD',
  compactMode: false,
  showEnergyCard: true,
  showMediaCard: true,
  alertThreshold: 80,
}

const TABS = [
  'Overview',
  'Lights',
  'Climate',
  'Security',
  'System',
  'Remote Connect',
  'Settings',
] as const

type Tab = (typeof TABS)[number]

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Convert Fahrenheit to Celsius */
const toC = (f: number) => Math.round(((f - 32) * 5) / 9)

type StatusKey = 'online' | 'warning' | 'offline' | 'connected' | 'disconnected' | 'connecting'

const STATUS_DOT_CLASSES: Record<StatusKey, string> = {
  online: 'bg-green-500 shadow-[0_0_6px_rgba(34,197,94,0.6)]',
  connected: 'bg-green-500 shadow-[0_0_6px_rgba(34,197,94,0.6)]',
  warning: 'bg-orange-500 shadow-[0_0_6px_rgba(249,115,22,0.6)]',
  connecting: 'bg-yellow-400 shadow-[0_0_6px_rgba(234,179,8,0.6)]',
  offline: 'bg-red-500 shadow-[0_0_6px_rgba(239,68,68,0.6)]',
  disconnected: 'bg-gray-400',
}

const STATUS_TEXT_CLASSES: Record<StatusKey, string> = {
  online: 'text-green-600',
  connected: 'text-green-600',
  warning: 'text-orange-500',
  connecting: 'text-yellow-600',
  offline: 'text-red-500',
  disconnected: 'text-gray-400',
}

const statusDot = (status: StatusKey) =>
  `w-2.5 h-2.5 rounded-full flex-shrink-0 ${STATUS_DOT_CLASSES[status] ?? 'bg-gray-400'}`

const statusTextCls = (status: string) =>
  STATUS_TEXT_CLASSES[status as StatusKey] ?? 'text-gray-500'

/** Styled toggle switch — reusable snippet */
const Toggle = ({
  checked,
  onChange,
  label,
}: {
  checked: boolean
  onChange: () => void
  label: string
}) => (
  <button
    onClick={onChange}
    aria-label={label}
    role="switch"
    aria-checked={checked}
    className={`relative w-11 h-6 rounded-full transition-colors flex-shrink-0 ${checked ? 'bg-blue-400' : 'bg-gray-300'}`}
  >
    <div
      className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${checked ? 'translate-x-5' : ''}`}
    />
  </button>
)

// ─── Component ────────────────────────────────────────────────────────────────

export const HomeAssistant: React.FC = () => {
  // ── Existing state ─────────────────────────────────────────────────────────
  const [lights, setLights] = useState<Light[]>([
    { id: '1', name: 'Living Room', brightness: 85, colorTemp: 'warm', isOn: true },
    { id: '2', name: 'Bedroom', brightness: 60, colorTemp: 'cool', isOn: false },
    { id: '3', name: 'Kitchen', brightness: 60, colorTemp: 'cool', isOn: true },
    { id: '4', name: 'Office', brightness: 75, colorTemp: 'neutral', isOn: false },
  ])

  const [temperature, setTemperature] = useState(72)
  const [climateMode, setClimateMode] = useState<'off' | 'heat' | 'cool' | 'auto'>('heat')
  const [isPlaying, setIsPlaying] = useState(true)
  const [activeTab, setActiveTab] = useState<Tab>('Overview')

  // ── New state ───────────────────────────────────────────────────────────────
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const [settings, setSettings] = useState<DashboardSettings>(() => {
    try {
      const saved = localStorage.getItem('ha_dashboard_settings')
      return saved ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) } : DEFAULT_SETTINGS
    } catch {
      return DEFAULT_SETTINGS
    }
  })

  // ── Handlers ────────────────────────────────────────────────────────────────

  const toggleLight = (id: string) =>
    setLights(prev => prev.map(l => (l.id === id ? { ...l, isOn: !l.isOn } : l)))

  const setBrightness = (id: string, brightness: number) =>
    setLights(prev => prev.map(l => (l.id === id ? { ...l, brightness } : l)))

  const setColorTemp = (id: string, colorTemp: Light['colorTemp']) =>
    setLights(prev => prev.map(l => (l.id === id ? { ...l, colorTemp } : l)))

  const allLightsOff = () => setLights(prev => prev.map(l => ({ ...l, isOn: false })))

  const adjustTemperature = (delta: number) =>
    setTemperature(prev => Math.max(60, Math.min(85, prev + delta)))

  const copyToClipboard = useCallback(async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text)
    } catch {
      // Fallback for environments without Clipboard API
      const el = document.createElement('textarea')
      el.value = text
      el.style.position = 'fixed'
      el.style.opacity = '0'
      document.body.appendChild(el)
      el.select()
      document.execCommand('copy')
      document.body.removeChild(el)
    }
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }, [])

  const updateSetting = <K extends keyof DashboardSettings>(
    key: K,
    value: DashboardSettings[K],
  ) => {
    setSettings(prev => {
      const next = { ...prev, [key]: value }
      try {
        localStorage.setItem('ha_dashboard_settings', JSON.stringify(next))
      } catch {
        // Storage unavailable — silently ignore
      }
      return next
    })
  }

  const resetSettings = () => {
    setSettings(DEFAULT_SETTINGS)
    try {
      localStorage.removeItem('ha_dashboard_settings')
    } catch {
      // ignore
    }
  }

  // ── Derived values ──────────────────────────────────────────────────────────

  const displayTemp = (f: number) =>
    settings.temperatureUnit === 'F' ? `${f}°F` : `${toC(f)}°C`

  const onLightsCount = lights.filter(l => l.isOn).length

  const lightStatusLabel = (light: Light) => {
    if (!light.isOn) return 'Off'
    const ct = light.colorTemp === 'warm' ? 'Warm White' : light.colorTemp === 'cool' ? 'Cool White' : 'Neutral'
    return `${light.brightness}% · ${ct}`
  }

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-purple-700">

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md shadow-md">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-5 min-w-0">
              <span className="text-2xl text-blue-400" aria-hidden>🏠</span>
              <span className="text-xl font-medium text-gray-800 whitespace-nowrap">Home</span>
              <nav className="ml-4 flex gap-1 overflow-x-auto" aria-label="Dashboard sections">
                {TABS.map(tab => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    aria-current={activeTab === tab ? 'page' : undefined}
                    className={`px-3 py-2 text-sm rounded-lg transition-colors whitespace-nowrap ${
                      activeTab === tab
                        ? 'bg-blue-50 text-blue-600 font-semibold'
                        : 'text-gray-600 hover:text-blue-500 hover:bg-gray-50'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </nav>
            </div>

            <div className="flex items-center gap-4 ml-4">
              <Tooltip content="1 unread notification" position="bottom">
                <button
                  className="relative text-xl text-gray-600 focus:outline-none"
                  aria-label="Notifications (1 unread)"
                >
                  🔔
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-4 h-4 flex items-center justify-center pointer-events-none">
                    1
                  </span>
                </button>
              </Tooltip>
              <div
                className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-700 text-white flex items-center justify-center font-semibold cursor-pointer"
                aria-label="User menu"
              >
                S
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* ── Main ───────────────────────────────────────────────────────────── */}
      <main className="max-w-7xl mx-auto p-6">

        {/* ================================================================ */}
        {/* OVERVIEW TAB                                                       */}
        {/* ================================================================ */}
        {activeTab === 'Overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">

            {/* Quick Actions */}
            <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800 mb-4">
                <span aria-hidden>⚡</span>Quick Actions
              </div>
              <div className="flex gap-3 overflow-x-auto pb-1">
                <button
                  onClick={allLightsOff}
                  className="bg-gradient-to-br from-indigo-500 to-purple-700 text-white px-5 py-3 rounded-lg flex items-center gap-2 text-sm whitespace-nowrap hover:scale-105 transition-transform"
                >
                  <span aria-hidden>🌙</span>All Lights Off
                </button>
                <button
                  onClick={() => { allLightsOff(); setClimateMode('off') }}
                  className="bg-gradient-to-br from-indigo-500 to-purple-700 text-white px-5 py-3 rounded-lg flex items-center gap-2 text-sm whitespace-nowrap hover:scale-105 transition-transform"
                >
                  <span aria-hidden>😴</span>Goodnight
                </button>
                <button
                  onClick={() => { allLightsOff(); setClimateMode('off') }}
                  className="bg-gradient-to-br from-indigo-500 to-purple-700 text-white px-5 py-3 rounded-lg flex items-center gap-2 text-sm whitespace-nowrap hover:scale-105 transition-transform"
                >
                  <span aria-hidden>🔒</span>Away Mode
                </button>
              </div>
            </div>

            {/* Climate summary */}
            <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800 mb-4">
                <span aria-hidden>🌡️</span>Climate Control
              </div>
              <div className="text-center">
                <div className="text-5xl font-light text-blue-400 my-4">{displayTemp(temperature)}</div>
                <div className="flex items-center justify-center gap-5 my-3">
                  <button
                    onClick={() => adjustTemperature(-1)}
                    aria-label="Decrease set temperature"
                    className="w-10 h-10 border-2 border-blue-400 bg-white text-blue-400 rounded-full text-xl flex items-center justify-center hover:bg-blue-400 hover:text-white transition-colors"
                  >−</button>
                  <span className="text-lg font-medium">{temperature}</span>
                  <button
                    onClick={() => adjustTemperature(1)}
                    aria-label="Increase set temperature"
                    className="w-10 h-10 border-2 border-blue-400 bg-white text-blue-400 rounded-full text-xl flex items-center justify-center hover:bg-blue-400 hover:text-white transition-colors"
                  >+</button>
                </div>
                <div className="text-sm text-gray-600 mb-3">
                  Current: {displayTemp(68)} · {climateMode === 'heat' ? 'Heating' : climateMode === 'cool' ? 'Cooling' : climateMode === 'auto' ? 'Auto' : 'Off'}
                </div>
                <div className="flex gap-2 justify-center">
                  {(['off', 'heat', 'cool', 'auto'] as const).map(mode => (
                    <button
                      key={mode}
                      onClick={() => setClimateMode(mode)}
                      className={`px-3 py-1.5 border rounded text-xs capitalize transition-colors ${
                        climateMode === mode
                          ? 'bg-blue-400 text-white border-blue-400'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
                      }`}
                    >{mode}</button>
                  ))}
                </div>
              </div>
            </div>

            {/* Lights summary */}
            <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2 text-base font-medium text-gray-800">
                  <span aria-hidden>💡</span>Lights
                </div>
                <span className="text-xs text-gray-500">{onLightsCount} of {lights.length} on</span>
              </div>
              <div>
                {lights.map((light, idx) => (
                  <div
                    key={light.id}
                    className={`flex items-center justify-between py-3 ${idx !== lights.length - 1 ? 'border-b border-gray-100' : ''}`}
                  >
                    <div className="flex items-center gap-3">
                      <span
                        aria-hidden
                        className={`text-2xl transition-all ${light.isOn ? 'drop-shadow-[0_0_6px_rgba(253,184,19,0.6)]' : 'opacity-30'}`}
                      >💡</span>
                      <div>
                        <div className="font-medium text-gray-800">{light.name}</div>
                        <div className="text-xs text-gray-500">{lightStatusLabel(light)}</div>
                      </div>
                    </div>
                    <button
                      onClick={() => toggleLight(light.id)}
                      aria-label={`Turn ${light.isOn ? 'off' : 'on'} ${light.name}`}
                      role="switch"
                      aria-checked={light.isOn}
                      className={`relative w-12 h-6 rounded-full transition-colors ${light.isOn ? 'bg-blue-400' : 'bg-gray-300'}`}
                    >
                      <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${light.isOn ? 'translate-x-6' : ''}`} />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Security summary */}
            <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800 mb-4">
                <span aria-hidden>🔐</span>Security
              </div>
              {[
                { label: 'Front Door', icon: '🔒', status: 'Locked', ok: true },
                { label: 'Garage Door', icon: '🔒', status: 'Closed', ok: true },
                { label: 'Motion Sensors', icon: '📡', status: '2 active', ok: true },
              ].map((item, idx) => (
                <div key={idx} className={`flex items-center gap-3 py-3 ${idx < 2 ? 'border-b border-gray-100' : ''}`}>
                  <span className={`text-2xl ${item.ok ? 'text-green-500' : 'text-red-500'}`} aria-hidden>{item.icon}</span>
                  <div>
                    <div className="font-medium text-gray-800">{item.label}</div>
                    <div className="text-xs text-gray-500">{item.status}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Motion Sensors */}
            <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800 mb-4">
                <span aria-hidden>📡</span>Motion Sensors
              </div>
              <div className="grid grid-cols-2 gap-3">
                {SENSORS.map(sensor => (
                  <div key={sensor.id} className="bg-gray-50 p-3 rounded-lg flex items-center gap-3">
                    <span className={`text-2xl ${sensor.hasMotion ? 'text-orange-500' : 'text-green-500'}`} aria-hidden>
                      {sensor.hasMotion ? '👤' : '✓'}
                    </span>
                    <div>
                      <div className="text-sm font-medium">{sensor.location}</div>
                      <div className="text-xs text-gray-500">
                        {sensor.hasMotion ? `Motion · ${sensor.lastTriggered}` : 'Clear'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Energy */}
            {settings.showEnergyCard && (
              <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
                <div className="flex items-center gap-2 text-base font-medium text-gray-800 mb-4">
                  <span aria-hidden>⚡</span>Energy Today
                </div>
                <div className="h-[120px] my-4">
                  <div className="flex items-end h-full gap-1" aria-label="Hourly energy usage chart">
                    {[30, 25, 45, 60, 75, 65, 50, 40].map((height, idx) => (
                      <div
                        key={idx}
                        className="flex-1 bg-gradient-to-t from-blue-600 to-blue-400 rounded-t"
                        style={{ height: `${height}%` }}
                      />
                    ))}
                  </div>
                </div>
                <div className="flex justify-between mt-3">
                  <div className="text-center">
                    <div className="text-xl font-medium text-blue-400">12.3</div>
                    <div className="text-xs text-gray-500">
                      <Tooltip content="Kilowatt-hours: energy consumed. 1 kWh = running a 1,000 W device for 1 hour." position="top">
                        <span className="cursor-help underline decoration-dotted decoration-gray-400">kWh Used</span>
                      </Tooltip>
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-medium text-blue-400">
                      {(12.3 * settings.costPerKwh).toLocaleString('en-US', {
                        style: 'currency',
                        currency: settings.currency,
                        maximumFractionDigits: 2,
                      })}
                    </div>
                    <div className="text-xs text-gray-500">Cost</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-medium text-blue-400">0</div>
                    <div className="text-xs text-gray-500">Solar kWh</div>
                  </div>
                </div>
              </div>
            )}

            {/* Media Player */}
            {settings.showMediaCard && (
              <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
                <div className="flex items-center gap-2 text-base font-medium text-gray-800 mb-4">
                  <span aria-hidden>🎵</span>Now Playing
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex gap-4 mb-3">
                    <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-700 rounded-lg flex items-center justify-center text-white text-2xl" aria-hidden>
                      🎵
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium mb-1 truncate">Bohemian Rhapsody</div>
                      <div className="text-sm text-gray-600">Queen</div>
                      <div className="text-xs text-gray-500 mt-1">Spotify · Living Room</div>
                    </div>
                  </div>
                  <div className="flex gap-3 items-center justify-center">
                    <button aria-label="Previous track" className="w-9 h-9 bg-white rounded-full shadow flex items-center justify-center text-base hover:bg-gray-100 transition-colors">⏮</button>
                    <button
                      onClick={() => setIsPlaying(!isPlaying)}
                      aria-label={isPlaying ? 'Pause' : 'Play'}
                      className="w-12 h-12 bg-blue-400 text-white rounded-full shadow flex items-center justify-center text-xl hover:bg-blue-500 transition-colors"
                    >
                      {isPlaying ? '⏸' : '▶'}
                    </button>
                    <button aria-label="Next track" className="w-9 h-9 bg-white rounded-full shadow flex items-center justify-center text-base hover:bg-gray-100 transition-colors">⏭</button>
                  </div>
                </div>
              </div>
            )}

            {/* Homelab Services */}
            <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800 mb-4">
                <span aria-hidden>🖥️</span>Homelab Services
              </div>
              <ul className="space-y-2">
                {SERVICES.map(svc => (
                  <li key={svc.id} className="bg-gray-50 p-3 rounded-lg flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className={statusDot(svc.status)} />
                      <Tooltip content={svc.description} position="right" maxWidth="max-w-sm">
                        <span className="text-sm cursor-help underline decoration-dotted decoration-gray-400">{svc.name}</span>
                      </Tooltip>
                    </div>
                    <span className={`text-xs ${statusTextCls(svc.status)}`}>{svc.statusText}</span>
                  </li>
                ))}
              </ul>
            </div>

          </div>
        )}

        {/* ================================================================ */}
        {/* LIGHTS TAB                                                         */}
        {/* ================================================================ */}
        {activeTab === 'Lights' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {lights.map(light => (
              <div key={light.id} className="bg-white rounded-xl p-5 shadow-lg">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span
                      aria-hidden
                      className={`text-3xl transition-all ${light.isOn ? 'drop-shadow-[0_0_8px_rgba(253,184,19,0.6)]' : 'opacity-30'}`}
                    >💡</span>
                    <div>
                      <div className="text-base font-semibold text-gray-800">{light.name}</div>
                      <div className="text-xs text-gray-500">{lightStatusLabel(light)}</div>
                    </div>
                  </div>
                  <button
                    onClick={() => toggleLight(light.id)}
                    aria-label={`Turn ${light.isOn ? 'off' : 'on'} ${light.name}`}
                    role="switch"
                    aria-checked={light.isOn}
                    className={`relative w-14 h-7 rounded-full transition-colors ${light.isOn ? 'bg-blue-400' : 'bg-gray-300'}`}
                  >
                    <div className={`absolute top-1 left-1 w-5 h-5 bg-white rounded-full shadow transition-transform ${light.isOn ? 'translate-x-7' : ''}`} />
                  </button>
                </div>

                {light.isOn && (
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span>Brightness</span>
                        <span>{light.brightness}%</span>
                      </div>
                      <input
                        type="range"
                        min={1}
                        max={100}
                        value={light.brightness}
                        onChange={e => setBrightness(light.id, Number(e.target.value))}
                        aria-label={`${light.name} brightness`}
                        className="w-full accent-blue-400"
                      />
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 mb-2">Color Temperature</div>
                      <div className="flex gap-2">
                        {(['warm', 'neutral', 'cool'] as const).map(ct => (
                          <button
                            key={ct}
                            onClick={() => setColorTemp(light.id, ct)}
                            className={`flex-1 py-2 rounded-lg text-xs border transition-colors ${
                              light.colorTemp === ct
                                ? 'bg-blue-400 text-white border-blue-400'
                                : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
                            }`}
                          >
                            {ct === 'warm' ? '🔆 Warm' : ct === 'cool' ? '❄️ Cool' : '⚪ Neutral'}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}

            {/* Scenes card */}
            <div className="bg-white rounded-xl p-5 shadow-lg">
              <div className="text-base font-medium text-gray-800 mb-4">Scenes</div>
              <div className="space-y-2">
                {[
                  { icon: '🌅', name: 'Morning', desc: 'Warm gradual sunrise brightness' },
                  { icon: '💼', name: 'Focus', desc: 'Bright cool white — reduces eye strain' },
                  { icon: '🎬', name: 'Movie', desc: 'Dim warm accent lighting' },
                  { icon: '🌙', name: 'Night', desc: 'Very dim warm — preserves melatonin' },
                ].map(scene => (
                  <button
                    key={scene.name}
                    className="w-full flex items-center gap-3 p-3 rounded-lg bg-gray-50 hover:bg-blue-50 border border-transparent hover:border-blue-200 transition-colors text-left"
                  >
                    <span className="text-2xl" aria-hidden>{scene.icon}</span>
                    <div>
                      <div className="text-sm font-medium text-gray-800">{scene.name}</div>
                      <div className="text-xs text-gray-500">{scene.desc}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ================================================================ */}
        {/* CLIMATE TAB                                                        */}
        {/* ================================================================ */}
        {activeTab === 'Climate' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="bg-white rounded-xl p-6 shadow-lg">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800 mb-6">
                <span aria-hidden>🌡️</span>Thermostat
              </div>
              <div className="text-center">
                <div className="text-7xl font-extralight text-blue-400 my-6">{displayTemp(temperature)}</div>
                <div className="text-sm text-gray-500 mb-6">Set point · Current: {displayTemp(68)}</div>
                <div className="flex items-center justify-center gap-8 mb-6">
                  <button onClick={() => adjustTemperature(-1)} aria-label="Decrease temperature"
                    className="w-14 h-14 border-2 border-blue-400 rounded-full text-2xl text-blue-400 hover:bg-blue-400 hover:text-white transition-colors flex items-center justify-center"
                  >−</button>
                  <button onClick={() => adjustTemperature(1)} aria-label="Increase temperature"
                    className="w-14 h-14 border-2 border-blue-400 rounded-full text-2xl text-blue-400 hover:bg-blue-400 hover:text-white transition-colors flex items-center justify-center"
                  >+</button>
                </div>
                <div className="flex gap-2 justify-center">
                  {(['off', 'heat', 'cool', 'auto'] as const).map(mode => (
                    <button key={mode} onClick={() => setClimateMode(mode)}
                      className={`px-4 py-2 rounded-lg text-sm capitalize border transition-colors ${
                        climateMode === mode
                          ? 'bg-blue-400 text-white border-blue-400'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
                      }`}
                    >{mode}</button>
                  ))}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {[
                { room: 'Living Room', current: 68, set: 72 },
                { room: 'Bedroom', current: 65, set: 68 },
                { room: 'Kitchen', current: 71, set: 70 },
                { room: 'Office', current: 70, set: 72 },
              ].map(zone => (
                <div key={zone.room} className="bg-white rounded-xl p-4 shadow-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium text-gray-800">{zone.room}</div>
                    <div className="flex items-center gap-4">
                      <div className="text-center">
                        <div className="text-xs text-gray-400">Current</div>
                        <div className="text-sm font-medium text-gray-700">{displayTemp(zone.current)}</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xs text-gray-400">Set</div>
                        <div className="text-sm font-medium text-blue-500">{displayTemp(zone.set)}</div>
                      </div>
                    </div>
                  </div>
                  <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-400 to-indigo-500 rounded-full"
                      style={{ width: `${((zone.current - 60) / 30) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ================================================================ */}
        {/* SECURITY TAB                                                       */}
        {/* ================================================================ */}
        {activeTab === 'Security' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="bg-white rounded-xl p-5 shadow-lg">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800 mb-4">
                <span aria-hidden>🔐</span>Door &amp; Lock Status
              </div>
              <ul className="space-y-2">
                {[
                  { label: 'Front Door', icon: '🔒', locked: true },
                  { label: 'Back Door', icon: '🔒', locked: true },
                  { label: 'Garage Door', icon: '🚗', locked: true },
                  { label: 'Side Gate', icon: '🔓', locked: false },
                ].map(door => (
                  <li key={door.label} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <span className={`text-xl ${door.locked ? 'text-green-500' : 'text-red-500'}`} aria-hidden>{door.icon}</span>
                      <span className="font-medium text-gray-800">{door.label}</span>
                    </div>
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${door.locked ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {door.locked ? 'Locked' : 'Unlocked'}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-white rounded-xl p-5 shadow-lg">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800 mb-4">
                <span aria-hidden>📡</span>Motion Sensors
              </div>
              <div className="space-y-3">
                {SENSORS.map(sensor => (
                  <div
                    key={sensor.id}
                    className={`flex items-center justify-between p-3 rounded-lg border ${sensor.hasMotion ? 'bg-orange-50 border-orange-200' : 'bg-gray-50 border-gray-100'}`}
                  >
                    <div className="flex items-center gap-3">
                      <span className={`text-xl ${sensor.hasMotion ? 'text-orange-500' : 'text-green-500'}`} aria-hidden>
                        {sensor.hasMotion ? '👤' : '✓'}
                      </span>
                      <span className="font-medium text-gray-800">{sensor.location}</span>
                    </div>
                    <div className="text-right">
                      <div className={`text-xs font-medium ${sensor.hasMotion ? 'text-orange-600' : 'text-green-600'}`}>
                        {sensor.hasMotion ? 'Motion Detected' : 'Clear'}
                      </div>
                      {sensor.lastTriggered && (
                        <div className="text-xs text-gray-400 mt-0.5">{sensor.lastTriggered}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl p-5 shadow-lg md:col-span-2">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800 mb-4">
                <span aria-hidden>📋</span>Security Event Log
              </div>
              <div className="space-y-2">
                {[
                  { time: '09:42', event: 'Motion detected — Kitchen', severity: 'info' },
                  { time: '08:15', event: 'Front door unlocked via keypad', severity: 'info' },
                  { time: '07:30', event: 'Away Mode deactivated', severity: 'info' },
                  { time: '23:05', event: 'Side Gate unlocked — verify manually', severity: 'warn' },
                ].map((evt, idx) => (
                  <div key={idx} className={`flex items-start gap-3 p-3 rounded-lg ${evt.severity === 'warn' ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-50'}`}>
                    <time className="text-xs text-gray-400 font-mono mt-0.5 whitespace-nowrap">{evt.time}</time>
                    <span className={`text-sm ${evt.severity === 'warn' ? 'text-yellow-700 font-medium' : 'text-gray-700'}`}>{evt.event}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ================================================================ */}
        {/* SYSTEM TAB                                                         */}
        {/* ================================================================ */}
        {activeTab === 'System' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {SERVICES.map(svc => (
              <div key={svc.id} className="bg-white rounded-xl p-5 shadow-lg">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <span className={statusDot(svc.status)} />
                    <Tooltip content={svc.description} position="right" maxWidth="max-w-sm">
                      <span className="text-base font-semibold text-gray-800 cursor-help underline decoration-dotted decoration-gray-400">{svc.name}</span>
                    </Tooltip>
                  </div>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                    svc.status === 'online' ? 'bg-green-100 text-green-700' :
                    svc.status === 'warning' ? 'bg-orange-100 text-orange-700' :
                    'bg-red-100 text-red-700'
                  }`}>{svc.statusText}</span>
                </div>
                {svc.cpu !== undefined && (
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span>CPU</span><span>{svc.cpu}%</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${svc.cpu > 70 ? 'bg-orange-400' : 'bg-blue-400'}`}
                          style={{ width: `${svc.cpu}%` }}
                        />
                      </div>
                    </div>
                    {svc.memory !== undefined && (
                      <div>
                        <div className="flex justify-between text-xs text-gray-500 mb-1">
                          <span>Memory</span><span>{svc.memory}%</span>
                        </div>
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all ${svc.memory > 80 ? 'bg-orange-400' : 'bg-indigo-400'}`}
                            style={{ width: `${svc.memory}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* ================================================================ */}
        {/* REMOTE CONNECT TAB                                                 */}
        {/* ================================================================ */}
        {activeTab === 'Remote Connect' && (
          <div className="space-y-8">

            {/* ── VPN Tunnels ──────────────────────────────────────────────── */}
            <section aria-labelledby="vpn-heading">
              <h2 id="vpn-heading" className="text-white font-semibold text-lg mb-3 flex items-center gap-2">
                <span aria-hidden>🔒</span>
                <Tooltip
                  content="A VPN (Virtual Private Network) creates an encrypted tunnel from your device to your homelab network, allowing secure remote access as if you were on the LAN — without exposing services to the public internet."
                  position="right"
                  maxWidth="max-w-sm"
                >
                  <span className="cursor-help underline decoration-dotted decoration-white/60">VPN Tunnels</span>
                </Tooltip>
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {VPN_TUNNELS.map(tunnel => (
                  <div key={tunnel.id} className="bg-white rounded-xl p-5 shadow-lg">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <span className={statusDot(tunnel.status)} />
                        <Tooltip content={tunnel.protocolDescription} position="right" maxWidth="max-w-sm">
                          <span className="font-semibold text-gray-800 cursor-help underline decoration-dotted decoration-gray-400">
                            {tunnel.name}
                          </span>
                        </Tooltip>
                      </div>
                      <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full capitalize ${
                        tunnel.status === 'connected' ? 'bg-green-100 text-green-700' :
                        tunnel.status === 'connecting' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-500'
                      }`}>{tunnel.status}</span>
                    </div>
                    <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
                      <div>
                        <dt className="text-xs text-gray-400 mb-0.5">Peer</dt>
                        <dd className="font-mono text-xs text-gray-700 truncate">{tunnel.peer}</dd>
                      </div>
                      <div>
                        <dt className="text-xs text-gray-400 mb-0.5">
                          <Tooltip content="The IP address assigned to your device within the VPN subnet. Use this address to reach the tunnel interface from either side." position="top">
                            <span className="cursor-help underline decoration-dotted decoration-gray-400">Tunnel IP</span>
                          </Tooltip>
                        </dt>
                        <dd className="font-mono text-xs text-gray-700">{tunnel.tunnelIp}</dd>
                      </div>
                      <div>
                        <dt className="text-xs text-gray-400 mb-0.5">↓ Received</dt>
                        <dd className="text-xs text-gray-700">{tunnel.rxBytes}</dd>
                      </div>
                      <div>
                        <dt className="text-xs text-gray-400 mb-0.5">↑ Sent</dt>
                        <dd className="text-xs text-gray-700">{tunnel.txBytes}</dd>
                      </div>
                      <div className="col-span-2">
                        <dt className="text-xs text-gray-400 mb-0.5">
                          <Tooltip content="WireGuard performs a cryptographic handshake every 180 seconds to rotate session keys. A recent handshake confirms the tunnel is active." position="top">
                            <span className="cursor-help underline decoration-dotted decoration-gray-400">Last Handshake</span>
                          </Tooltip>
                        </dt>
                        <dd className="text-xs text-gray-700">{tunnel.lastHandshake}</dd>
                      </div>
                    </dl>
                  </div>
                ))}
              </div>
            </section>

            {/* ── SSH Quick Connect ─────────────────────────────────────────── */}
            <section aria-labelledby="ssh-heading">
              <h2 id="ssh-heading" className="text-white font-semibold text-lg mb-3 flex items-center gap-2">
                <span aria-hidden>💻</span>
                <Tooltip
                  content="SSH (Secure Shell) — encrypted protocol for remote CLI access. Authentication uses Ed25519 public-key pairs; no passwords sent over the wire. All traffic is encrypted with AES-256-GCM or ChaCha20-Poly1305."
                  position="right"
                  maxWidth="max-w-sm"
                >
                  <span className="cursor-help underline decoration-dotted decoration-white/60">SSH Quick Connect</span>
                </Tooltip>
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {SSH_HOSTS.map(host => {
                  const cmd = `ssh ${host.user}@${host.hostname} -p ${host.port}`
                  const copyId = `ssh-${host.id}`
                  return (
                    <div key={host.id} className="bg-white rounded-xl p-5 shadow-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className={statusDot(host.status)} />
                          <Tooltip content={host.description} position="right" maxWidth="max-w-xs">
                            <span className="font-semibold text-gray-800 cursor-help underline decoration-dotted decoration-gray-400">
                              {host.name}
                            </span>
                          </Tooltip>
                        </div>
                        <span className="font-mono text-xs text-gray-400">{host.ip}:{host.port}</span>
                      </div>
                      <div className="flex items-center gap-2 bg-gray-900 rounded-lg px-3 py-2.5">
                        <span className="text-gray-500 text-xs font-mono select-none">$</span>
                        <code className="flex-1 text-green-400 text-xs font-mono truncate">{cmd}</code>
                        <Tooltip content={copiedId === copyId ? 'Copied!' : 'Copy command'} position="top">
                          <button
                            onClick={() => copyToClipboard(cmd, copyId)}
                            aria-label={`Copy SSH command for ${host.name}`}
                            className={`ml-1 text-xs px-2.5 py-1 rounded transition-colors ${
                              copiedId === copyId
                                ? 'bg-green-600 text-white'
                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                            }`}
                          >
                            {copiedId === copyId ? '✓ Done' : 'Copy'}
                          </button>
                        </Tooltip>
                      </div>
                    </div>
                  )
                })}
              </div>
            </section>

            {/* ── Web Management UIs ────────────────────────────────────────── */}
            <section aria-labelledby="webui-heading">
              <h2 id="webui-heading" className="text-white font-semibold text-lg mb-3 flex items-center gap-2">
                <span aria-hidden>🌐</span>Web Management UIs
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {WEB_UIS.map(ui => {
                  const copyId = `webui-${ui.id}`
                  return (
                    <div key={ui.id} className="bg-white rounded-xl p-4 shadow-lg">
                      <div className="flex items-start gap-3 mb-3">
                        <span className="text-2xl mt-0.5" aria-hidden>{ui.icon}</span>
                        <div className="flex-1 min-w-0">
                          <Tooltip content={ui.description} position="bottom" maxWidth="max-w-xs">
                            <div className="font-semibold text-gray-800 text-sm cursor-help underline decoration-dotted decoration-gray-400 truncate">
                              {ui.name}
                            </div>
                          </Tooltip>
                          <div className="flex items-center gap-1.5 mt-1">
                            <span className={statusDot(ui.status)} />
                            <span className={`text-xs ${statusTextCls(ui.status)} capitalize`}>{ui.status}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <a
                          href={ui.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          aria-label={`Open ${ui.name} in new tab`}
                          className="flex-1 text-center py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white text-xs font-medium rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all"
                        >
                          Open UI ↗
                        </a>
                        <Tooltip content={copiedId === copyId ? 'Copied!' : 'Copy URL'} position="top">
                          <button
                            onClick={() => copyToClipboard(ui.url, copyId)}
                            aria-label={`Copy URL for ${ui.name}`}
                            className={`py-2 px-3 rounded-lg text-xs transition-colors border ${
                              copiedId === copyId
                                ? 'bg-green-100 text-green-700 border-green-200'
                                : 'border-gray-200 text-gray-500 hover:border-gray-300 hover:text-gray-700'
                            }`}
                          >
                            {copiedId === copyId ? '✓' : '📋'}
                          </button>
                        </Tooltip>
                      </div>
                    </div>
                  )
                })}
              </div>
            </section>

            {/* ── Protocol Legend ───────────────────────────────────────────── */}
            <section aria-labelledby="legend-heading" className="bg-white/10 backdrop-blur-sm rounded-xl p-5">
              <h2 id="legend-heading" className="text-white font-semibold mb-4 flex items-center gap-2">
                <span aria-hidden>📖</span>Protocol &amp; Technology Reference
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {PROTOCOL_LEGEND.map(({ term, desc }) => (
                  <div key={term} className="bg-white/10 rounded-lg p-3">
                    <div className="text-white font-mono text-sm font-semibold mb-1">{term}</div>
                    <div className="text-white/75 text-xs leading-relaxed">{desc}</div>
                  </div>
                ))}
              </div>
            </section>

          </div>
        )}

        {/* ================================================================ */}
        {/* SETTINGS TAB                                                       */}
        {/* ================================================================ */}
        {activeTab === 'Settings' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 max-w-3xl">

            {/* Display */}
            <div className="bg-white rounded-xl p-5 shadow-lg">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800 mb-5">
                <span aria-hidden>🖥️</span>Display
              </div>
              <div className="space-y-5">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-700">Temperature Unit</div>
                    <div className="text-xs text-gray-400 mt-0.5">Fahrenheit or Celsius</div>
                  </div>
                  <div className="flex rounded-lg border border-gray-200 overflow-hidden">
                    <button
                      onClick={() => updateSetting('temperatureUnit', 'F')}
                      className={`px-3 py-1.5 text-sm transition-colors ${settings.temperatureUnit === 'F' ? 'bg-blue-400 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
                    >°F</button>
                    <button
                      onClick={() => updateSetting('temperatureUnit', 'C')}
                      className={`px-3 py-1.5 text-sm transition-colors ${settings.temperatureUnit === 'C' ? 'bg-blue-400 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
                    >°C</button>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <div>
                    <div className="text-sm font-medium text-gray-700">Show Energy Card</div>
                    <div className="text-xs text-gray-400 mt-0.5">Display daily energy usage widget</div>
                  </div>
                  <Toggle
                    checked={settings.showEnergyCard}
                    onChange={() => updateSetting('showEnergyCard', !settings.showEnergyCard)}
                    label="Toggle energy card"
                  />
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <div>
                    <div className="text-sm font-medium text-gray-700">Show Media Player</div>
                    <div className="text-xs text-gray-400 mt-0.5">Display now-playing widget</div>
                  </div>
                  <Toggle
                    checked={settings.showMediaCard}
                    onChange={() => updateSetting('showMediaCard', !settings.showMediaCard)}
                    label="Toggle media player card"
                  />
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <div>
                    <div className="text-sm font-medium text-gray-700">Compact Mode</div>
                    <div className="text-xs text-gray-400 mt-0.5">Reduce padding for dense layouts</div>
                  </div>
                  <Toggle
                    checked={settings.compactMode}
                    onChange={() => updateSetting('compactMode', !settings.compactMode)}
                    label="Toggle compact mode"
                  />
                </div>
              </div>
            </div>

            {/* Refresh & Alerts */}
            <div className="bg-white rounded-xl p-5 shadow-lg">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800 mb-5">
                <span aria-hidden>🔄</span>Refresh &amp; Alerts
              </div>
              <div className="space-y-5">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-700">Auto-Refresh</div>
                    <div className="text-xs text-gray-400 mt-0.5">Poll sensor &amp; service data automatically</div>
                  </div>
                  <Toggle
                    checked={settings.autoRefresh}
                    onChange={() => updateSetting('autoRefresh', !settings.autoRefresh)}
                    label="Toggle auto-refresh"
                  />
                </div>

                {settings.autoRefresh && (
                  <div className="pt-4 border-t border-gray-100">
                    <div className="flex justify-between text-xs text-gray-500 mb-2">
                      <span>Refresh Interval</span>
                      <span className="font-medium">{settings.refreshIntervalSeconds}s</span>
                    </div>
                    <input
                      type="range"
                      min={10}
                      max={300}
                      step={10}
                      value={settings.refreshIntervalSeconds}
                      onChange={e => updateSetting('refreshIntervalSeconds', Number(e.target.value))}
                      aria-label="Refresh interval in seconds"
                      className="w-full accent-blue-400"
                    />
                    <div className="flex justify-between text-xs text-gray-400 mt-1">
                      <span>10 s</span><span>5 min</span>
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t border-gray-100">
                  <div className="flex justify-between text-xs text-gray-500 mb-2">
                    <Tooltip
                      content="Trigger a warning indicator when any homelab service's CPU or memory utilisation exceeds this percentage. Matches the orange threshold bars in the System tab."
                      position="right"
                      maxWidth="max-w-xs"
                    >
                      <span className="cursor-help underline decoration-dotted decoration-gray-400">High-Load Alert Threshold</span>
                    </Tooltip>
                    <span className="font-medium">{settings.alertThreshold}%</span>
                  </div>
                  <input
                    type="range"
                    min={50}
                    max={100}
                    step={5}
                    value={settings.alertThreshold}
                    onChange={e => updateSetting('alertThreshold', Number(e.target.value))}
                    aria-label="Alert threshold percentage"
                    className="w-full accent-orange-400"
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>50%</span><span>100%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Energy Monitoring */}
            <div className="bg-white rounded-xl p-5 shadow-lg">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800 mb-5">
                <span aria-hidden>⚡</span>Energy Monitoring
              </div>
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5" htmlFor="cost-per-kwh">
                    Cost per{' '}
                    <Tooltip
                      content="Kilowatt-hour (kWh): unit of electrical energy. 1 kWh equals using a 1,000 W device for exactly one hour. Check your monthly utility bill for your per-kWh rate."
                      position="top"
                      maxWidth="max-w-xs"
                    >
                      <span className="cursor-help underline decoration-dotted decoration-gray-400">kWh</span>
                    </Tooltip>
                  </label>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-500 text-sm">$</span>
                    <input
                      id="cost-per-kwh"
                      type="number"
                      min={0}
                      max={2}
                      step={0.01}
                      value={settings.costPerKwh}
                      onChange={e => updateSetting('costPerKwh', Number(e.target.value))}
                      className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm w-24 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                    />
                    <span className="text-gray-500 text-sm">per kWh</span>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-100">
                  <label className="block text-sm font-medium text-gray-700 mb-1.5" htmlFor="currency-select">
                    Display Currency
                  </label>
                  <select
                    id="currency-select"
                    value={settings.currency}
                    onChange={e => updateSetting('currency', e.target.value)}
                    className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                  >
                    <option value="USD">USD — US Dollar ($)</option>
                    <option value="EUR">EUR — Euro (€)</option>
                    <option value="GBP">GBP — British Pound (£)</option>
                    <option value="CAD">CAD — Canadian Dollar (C$)</option>
                    <option value="AUD">AUD — Australian Dollar (A$)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* About & Reset */}
            <div className="bg-white rounded-xl p-5 shadow-lg">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800 mb-5">
                <span aria-hidden>ℹ️</span>About
              </div>
              <dl className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <dt className="text-gray-500">Dashboard Version</dt>
                  <dd className="text-gray-800 font-mono">1.2.0</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500">
                    <Tooltip
                      content="Home Assistant (HA) is an open-source home automation platform running locally on your server. This custom dashboard integrates with the HA WebSocket API and REST API."
                      position="top"
                      maxWidth="max-w-xs"
                    >
                      <span className="cursor-help underline decoration-dotted decoration-gray-400">HA Core</span>
                    </Tooltip>
                  </dt>
                  <dd className="text-gray-800 font-mono">2024.12.1</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500">Last Config Backup</dt>
                  <dd className="text-gray-800">Today, 03:00</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500">Settings Storage</dt>
                  <dd className="text-gray-800 text-xs">
                    <Tooltip
                      content="Dashboard preferences are saved in your browser's localStorage — they persist across page reloads but are local to this browser. No server-side storage is used."
                      position="top"
                      maxWidth="max-w-xs"
                    >
                      <span className="cursor-help underline decoration-dotted decoration-gray-400">localStorage</span>
                    </Tooltip>
                  </dd>
                </div>
              </dl>
              <button
                onClick={resetSettings}
                className="mt-5 w-full py-2 rounded-lg border border-red-200 text-red-500 text-sm hover:bg-red-50 transition-colors"
              >
                Reset to Defaults
              </button>
            </div>

          </div>
        )}

      </main>
    </div>
  )
}

/**
 * Home Assistant Dashboard Page
 *
 * Interactive smart home dashboard showing lights, climate, security, and more
 */

import React, { useState } from 'react'

interface Light {
  id: string
  name: string
  status: string
  isOn: boolean
}

interface Sensor {
  id: string
  location: string
  status: string
  hasMotion: boolean
}

interface Service {
  id: string
  name: string
  status: 'online' | 'warning' | 'offline'
  statusText: string
}

export const HomeAssistant: React.FC = () => {
  const [lights, setLights] = useState<Light[]>([
    { id: '1', name: 'Living Room', status: '85% · Warm White', isOn: true },
    { id: '2', name: 'Bedroom', status: 'Off', isOn: false },
    { id: '3', name: 'Kitchen', status: '60% · Cool White', isOn: true },
    { id: '4', name: 'Office', status: 'Off', isOn: false },
  ])

  const [temperature, setTemperature] = useState(72)
  const [climateMode, setClimateMode] = useState<'off' | 'heat' | 'cool' | 'auto'>('heat')
  const [isPlaying, setIsPlaying] = useState(true)
  const [activeTab, setActiveTab] = useState('Overview')

  const sensors: Sensor[] = [
    { id: '1', location: 'Living Room', status: 'Clear', hasMotion: false },
    { id: '2', location: 'Kitchen', status: 'Motion detected', hasMotion: true },
    { id: '3', location: 'Bedroom', status: 'Clear', hasMotion: false },
    { id: '4', location: 'Garage', status: 'Clear', hasMotion: false },
  ]

  const services: Service[] = [
    { id: '1', name: 'Proxmox VE', status: 'online', statusText: 'Online' },
    { id: '2', name: 'TrueNAS', status: 'online', statusText: 'Online' },
    { id: '3', name: 'PostgreSQL', status: 'online', statusText: 'Online' },
    { id: '4', name: 'Backup Server', status: 'warning', statusText: 'High Load' },
  ]

  const tabs = ['Overview', 'Lights', 'Climate', 'Security', 'System']

  const toggleLight = (id: string) => {
    setLights(lights.map(light =>
      light.id === id ? { ...light, isOn: !light.isOn } : light
    ))
  }

  const adjustTemperature = (delta: number) => {
    setTemperature(prev => Math.max(60, Math.min(85, prev + delta)))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-purple-700">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md shadow-md">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-5">
              <div className="text-2xl text-blue-400">🏠</div>
              <div className="text-xl font-medium text-gray-800">Home</div>
              <nav className="ml-8 flex gap-6">
                {tabs.map(tab => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`pb-2 text-sm border-b-2 transition-colors ${
                      activeTab === tab
                        ? 'text-blue-400 border-blue-400'
                        : 'text-gray-600 border-transparent hover:text-blue-400'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <div className="relative cursor-pointer text-xl text-gray-600">
                🔔
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full px-1.5 py-0.5">
                  1
                </span>
              </div>
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-700 text-white flex items-center justify-center font-semibold cursor-pointer">
                S
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">

          {/* Quick Actions Card */}
          <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800">
                <span className="text-xl">⚡</span>
                Quick Actions
              </div>
            </div>
            <div className="flex gap-3 overflow-x-auto">
              <button className="bg-gradient-to-br from-indigo-500 to-purple-700 text-white px-5 py-3 rounded-lg flex items-center gap-2 text-sm whitespace-nowrap hover:scale-105 transition-transform">
                <span>🌙</span>
                <span>All Lights Off</span>
              </button>
              <button className="bg-gradient-to-br from-indigo-500 to-purple-700 text-white px-5 py-3 rounded-lg flex items-center gap-2 text-sm whitespace-nowrap hover:scale-105 transition-transform">
                <span>😴</span>
                <span>Goodnight</span>
              </button>
              <button className="bg-gradient-to-br from-indigo-500 to-purple-700 text-white px-5 py-3 rounded-lg flex items-center gap-2 text-sm whitespace-nowrap hover:scale-105 transition-transform">
                <span>🔒</span>
                <span>Away Mode</span>
              </button>
            </div>
          </div>

          {/* Climate Card */}
          <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800">
                <span className="text-xl">🌡️</span>
                Climate Control
              </div>
              <div className="text-gray-400 cursor-pointer text-lg">⋮</div>
            </div>
            <div className="text-center">
              <div className="text-5xl font-light text-blue-400 my-4">{temperature}°F</div>
              <div className="flex items-center justify-center gap-5 my-4">
                <button
                  onClick={() => adjustTemperature(-1)}
                  className="w-10 h-10 border-2 border-blue-400 bg-white text-blue-400 rounded-full text-xl flex items-center justify-center hover:bg-blue-400 hover:text-white transition-colors"
                >
                  −
                </button>
                <div className="text-lg font-medium">{temperature}</div>
                <button
                  onClick={() => adjustTemperature(1)}
                  className="w-10 h-10 border-2 border-blue-400 bg-white text-blue-400 rounded-full text-xl flex items-center justify-center hover:bg-blue-400 hover:text-white transition-colors"
                >
                  +
                </button>
              </div>
              <div className="text-sm text-gray-600">Current: 68°F · Heating</div>
              <div className="flex gap-2 justify-center mt-3">
                {(['off', 'heat', 'cool', 'auto'] as const).map(mode => (
                  <button
                    key={mode}
                    onClick={() => setClimateMode(mode)}
                    className={`px-3 py-1.5 border rounded text-xs capitalize transition-colors ${
                      climateMode === mode
                        ? 'bg-blue-400 text-white border-blue-400'
                        : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
                    }`}
                  >
                    {mode}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Lights Card */}
          <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800">
                <span className="text-xl">💡</span>
                Lights
              </div>
              <div className="text-gray-400 cursor-pointer text-lg">⋮</div>
            </div>
            <div className="space-y-0">
              {lights.map((light, index) => (
                <div
                  key={light.id}
                  className={`flex items-center justify-between py-3 ${
                    index !== lights.length - 1 ? 'border-b border-gray-100' : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`text-2xl ${light.isOn ? 'filter drop-shadow-[0_0_8px_rgba(253,184,19,0.5)]' : 'opacity-30'}`}>
                      💡
                    </div>
                    <div>
                      <div className="font-medium text-gray-800">{light.name}</div>
                      <div className="text-xs text-gray-500">{light.status}</div>
                    </div>
                  </div>
                  <button
                    onClick={() => toggleLight(light.id)}
                    className={`relative w-12 h-6 rounded-full transition-colors ${
                      light.isOn ? 'bg-blue-400' : 'bg-gray-300'
                    }`}
                  >
                    <div
                      className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                        light.isOn ? 'translate-x-6' : ''
                      }`}
                    />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Security Card */}
          <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800">
                <span className="text-xl">🔐</span>
                Security
              </div>
              <div className="text-gray-400 cursor-pointer text-lg">⋮</div>
            </div>
            <div className="space-y-0">
              <div className="flex items-center justify-between py-3 border-b border-gray-100">
                <div className="flex items-center gap-3">
                  <div className="text-2xl text-green-500">🔒</div>
                  <div>
                    <div className="font-medium text-gray-800">Front Door</div>
                    <div className="text-xs text-gray-500">Locked</div>
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between py-3 border-b border-gray-100">
                <div className="flex items-center gap-3">
                  <div className="text-2xl text-green-500">🔒</div>
                  <div>
                    <div className="font-medium text-gray-800">Garage Door</div>
                    <div className="text-xs text-gray-500">Closed</div>
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between py-3">
                <div className="flex items-center gap-3">
                  <div className="text-2xl">📡</div>
                  <div>
                    <div className="font-medium text-gray-800">Motion Sensors</div>
                    <div className="text-xs text-gray-500">2 active</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Motion Sensors Card */}
          <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800">
                <span className="text-xl">📡</span>
                Motion Sensors
              </div>
              <div className="text-gray-400 cursor-pointer text-lg">⋮</div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {sensors.map(sensor => (
                <div key={sensor.id} className="bg-gray-50 p-3 rounded-lg flex items-center gap-3">
                  <div className={`text-2xl ${sensor.hasMotion ? 'text-orange-500' : 'text-green-500'}`}>
                    {sensor.hasMotion ? '👤' : '✓'}
                  </div>
                  <div>
                    <div className="text-sm font-medium">{sensor.location}</div>
                    <div className="text-xs text-gray-500">{sensor.status}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Energy Card */}
          <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800">
                <span className="text-xl">⚡</span>
                Energy Today
              </div>
              <div className="text-gray-400 cursor-pointer text-lg">⋮</div>
            </div>
            <div className="h-30 my-4">
              <div className="flex items-end h-full gap-1">
                {[30, 25, 45, 60, 75, 65, 50, 40].map((height, index) => (
                  <div
                    key={index}
                    className="flex-1 bg-gradient-to-t from-blue-600 to-blue-400 rounded-t"
                    style={{ height: `${height}%` }}
                  />
                ))}
              </div>
            </div>
            <div className="flex justify-between mt-3">
              <div className="flex flex-col items-center">
                <div className="text-xl font-medium text-blue-400">12.3</div>
                <div className="text-xs text-gray-500">kWh Used</div>
              </div>
              <div className="flex flex-col items-center">
                <div className="text-xl font-medium text-blue-400">$2.15</div>
                <div className="text-xs text-gray-500">Cost</div>
              </div>
              <div className="flex flex-col items-center">
                <div className="text-xl font-medium text-blue-400">0</div>
                <div className="text-xs text-gray-500">Solar</div>
              </div>
            </div>
          </div>

          {/* Media Player Card */}
          <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800">
                <span className="text-xl">🎵</span>
                Now Playing
              </div>
              <div className="text-gray-400 cursor-pointer text-lg">⋮</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex gap-4 mb-3">
                <div className="w-15 h-15 bg-gradient-to-br from-indigo-500 to-purple-700 rounded-lg flex items-center justify-center text-white text-2xl">
                  🎵
                </div>
                <div className="flex-1">
                  <div className="font-medium mb-1">Bohemian Rhapsody</div>
                  <div className="text-sm text-gray-600">Queen</div>
                  <div className="text-xs text-gray-500 mt-1">Spotify · Living Room</div>
                </div>
              </div>
              <div className="flex gap-3 items-center justify-center">
                <button className="w-9 h-9 bg-white rounded-full shadow flex items-center justify-center text-base hover:bg-gray-100">
                  ⏮
                </button>
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="w-12 h-12 bg-blue-400 text-white rounded-full shadow flex items-center justify-center text-xl hover:bg-blue-500"
                >
                  {isPlaying ? '⏸' : '▶'}
                </button>
                <button className="w-9 h-9 bg-white rounded-full shadow flex items-center justify-center text-base hover:bg-gray-100">
                  ⏭
                </button>
              </div>
            </div>
          </div>

          {/* System Status Card */}
          <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-base font-medium text-gray-800">
                <span className="text-xl">🖥️</span>
                Homelab Services
              </div>
              <div className="text-gray-400 cursor-pointer text-lg">⋮</div>
            </div>
            <ul className="space-y-2">
              {services.map(service => (
                <li key={service.id} className="bg-gray-50 p-3 rounded-lg flex items-center justify-between">
                  <div className="flex items-center">
                    <span className={`w-2 h-2 rounded-full mr-3 ${
                      service.status === 'online' ? 'bg-green-500 shadow-[0_0_8px_rgba(76,175,80,0.5)]' :
                      service.status === 'warning' ? 'bg-orange-500 shadow-[0_0_8px_rgba(255,152,0,0.5)]' :
                      'bg-red-500 shadow-[0_0_8px_rgba(244,67,54,0.5)]'
                    }`} />
                    <span className="text-sm">{service.name}</span>
                  </div>
                  <span className={`text-xs ${
                    service.status === 'online' ? 'text-green-500' :
                    service.status === 'warning' ? 'text-orange-500' :
                    'text-red-500'
                  }`}>
                    {service.statusText}
                  </span>
                </li>
              ))}
            </ul>
          </div>

        </div>
      </main>
    </div>
  )
}

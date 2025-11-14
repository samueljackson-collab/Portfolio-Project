import React, { useEffect, useMemo, useState } from 'react'
import Calendar from 'react-calendar'
import { format, parseISO, startOfMonth } from 'date-fns'
import type { CalendarMonthResponse, Photo } from '../../api/types'
import { photoService } from '../../api/services'
import 'react-calendar/dist/Calendar.css'

interface Props {
  onDateSelect?: (date: Date, photos: Photo[]) => void
}

export const PhotoCalendar: React.FC<Props> = ({ onDateSelect }) => {
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [activeMonth, setActiveMonth] = useState(startOfMonth(new Date()))
  const [monthData, setMonthData] = useState<CalendarMonthResponse | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      setLoading(true)
      try {
        const data = await photoService.getCalendar(activeMonth.getFullYear(), activeMonth.getMonth() + 1)
        if (!cancelled) {
          setMonthData(data)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [activeMonth])

  const dateMap = useMemo(() => {
    if (!monthData) {
      return new Map<string, { count: number; photos: Photo[] }>()
    }
    const map = new Map<string, { count: number; photos: Photo[] }>()
    monthData.dates.forEach((entry) => {
      const key = format(parseISO(entry.date), 'yyyy-MM-dd')
      map.set(key, { count: entry.photo_count, photos: entry.preview_photos })
    })
    return map
  }, [monthData])

  const handleDateClick = (date: Date) => {
    setSelectedDate(date)
    const key = format(date, 'yyyy-MM-dd')
    const entry = dateMap.get(key)
    if (entry && entry.count > 0) {
      onDateSelect?.(date, entry.photos)
    }
  }

  const tileContent = ({ date, view }: { date: Date; view: string }) => {
    if (view !== 'month') return null
    const key = format(date, 'yyyy-MM-dd')
    const entry = dateMap.get(key)
    if (!entry || entry.count === 0) return null
    return (
      <span className="mt-1 inline-block rounded-full bg-blue-700 px-2 py-0.5 text-xs font-bold text-white">
        {entry.count}
      </span>
    )
  }

  return (
    <div className="photo-calendar space-y-4">
      {loading && <p className="text-gray-600">Loading calendar…</p>}
      <Calendar
        value={selectedDate}
        onClickDay={handleDateClick}
        onActiveStartDateChange={({ activeStartDate }) => {
          if (activeStartDate) {
            setActiveMonth(startOfMonth(activeStartDate))
          }
        }}
        tileContent={tileContent}
        className="rounded-2xl border-2 border-gray-200 p-4 text-lg"
      />
      {monthData && (
        <p className="text-xl text-gray-700">
          <span className="font-semibold">{monthData.total_photos}</span> photos in {format(activeMonth, 'MMMM yyyy')}
        </p>
      )}
    </div>
  )
}

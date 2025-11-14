/**
 * PhotoCalendar - Calendar view with photo counts
 *
 * Features:
 * - Large calendar display
 * - Photo counts on dates
 * - Preview thumbnails on hover
 * - Easy navigation
 */

import React, { useMemo, useState, useEffect } from 'react'
import Calendar from 'react-calendar'
import 'react-calendar/dist/Calendar.css'
import { photoService } from '../../api/services'
import type { CalendarMonthResponse, CalendarDateResponse, Photo } from '../../api/types'
import { format, parseISO, startOfMonth } from 'date-fns'
import './PhotoCalendar.css'

interface PhotoCalendarProps {
  onDateSelect?: (date: Date, photos: Photo[]) => void
  className?: string
}

export const PhotoCalendar: React.FC<PhotoCalendarProps> = ({
  onDateSelect,
  className = '',
}) => {
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [activeMonth, setActiveMonth] = useState(startOfMonth(new Date()))
  const [monthData, setMonthData] = useState<CalendarMonthResponse | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadMonthData(activeMonth)
  }, [activeMonth])

  const loadMonthData = async (date: Date) => {
    setLoading(true)
    try {
      const data = await photoService.getCalendarMonth(
        date.getFullYear(),
        date.getMonth() + 1
      )
      setMonthData(data)
    } catch (error) {
      console.error('Failed to load calendar data:', error)
    } finally {
      setLoading(false)
    }
  }

  const dateLookup = useMemo(() => {
    const map = new Map<string, CalendarDateResponse>()
    if (!monthData) {
      return map
    }

    monthData.dates.forEach((dateEntry) => {
      const key = format(parseISO(dateEntry.date), 'yyyy-MM-dd')
      map.set(key, dateEntry)
    })
    return map
  }, [monthData])

  const getPhotosForDate = (date: Date): number => {
    const dateStr = format(date, 'yyyy-MM-dd')
    return dateLookup.get(dateStr)?.photo_count ?? 0
  }

  const handleDateClick = (date: Date) => {
    setSelectedDate(date)
    const dateStr = format(date, 'yyyy-MM-dd')
    const dateData = dateLookup.get(dateStr)

    if (dateData && dateData.photo_count > 0) {
      onDateSelect?.(date, dateData.preview_photos)
    }
  }

  const tileContent = ({ date, view }: { date: Date; view: string }) => {
    if (view !== 'month') return null

    const count = getPhotosForDate(date)
    if (count === 0) return null

    return (
      <div className="mt-1">
        <span className="inline-block bg-blue-900 text-white text-xs font-bold px-2 py-1 rounded-full">
          {count}
        </span>
      </div>
    )
  }

  return (
    <div className={`photo-calendar ${className}`}>
      <Calendar
        value={selectedDate}
        onClickDay={handleDateClick}
        onActiveStartDateChange={({ activeStartDate }) => {
          if (activeStartDate) {
            const normalized = startOfMonth(activeStartDate)
            setActiveMonth(normalized)
            setSelectedDate(normalized)
          }
        }}
        tileContent={tileContent}
        className="text-lg"
      />

      {loading && (
        <p className="mt-4 text-center text-gray-500" aria-live="polite">
          Loading calendar...
        </p>
      )}

      {monthData && (
        <div className="mt-6 p-6 bg-gray-50 rounded-lg">
          <p className="text-xl text-gray-700">
            <span className="font-semibold">{monthData.total_photos}</span> photos in{' '}
            {format(activeMonth, 'MMMM yyyy')}
          </p>
        </div>
      )}
    </div>
  )
}

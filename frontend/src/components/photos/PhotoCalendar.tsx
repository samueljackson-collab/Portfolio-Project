/**
 * PhotoCalendar - Calendar view with photo counts
 *
 * Features:
 * - Large calendar display
 * - Photo counts on dates
 * - Preview thumbnails on hover
 * - Easy navigation
 */

import React, { useState, useEffect, useMemo } from 'react'
import Calendar from 'react-calendar'
import 'react-calendar/dist/Calendar.css'
import './PhotoCalendar.css'
import { photoService } from '../../api/services'
import type { CalendarMonthResponse, Photo, CalendarDateResponse } from '../../api/types'
import { format, parseISO, startOfMonth } from 'date-fns'

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

  const datePhotoMap = useMemo(() => {
    if (!monthData) return new Map<string, CalendarDateResponse>()

    return new Map(
      monthData.dates.map((d) => [format(parseISO(d.date), 'yyyy-MM-dd'), d])
    )
  }, [monthData])

  const getPhotosForDate = (date: Date): number => {
    if (!monthData) return 0

    const dateStr = format(date, 'yyyy-MM-dd')
    const dateData = datePhotoMap.get(dateStr)

    return dateData?.photo_count || 0
  }

  const handleDateClick = (date: Date) => {
    setSelectedDate(date)
    if (!monthData) return

    const dateStr = format(date, 'yyyy-MM-dd')
    const dateData = datePhotoMap.get(dateStr)

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
            setSelectedDate(activeStartDate)
          }
        }}
        tileContent={tileContent}
        className="text-lg"
      />

      {loading && (
        <p className="mt-4 text-lg text-gray-600" role="status">
          Loading calendar data...
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

/**
 * PhotoCalendar - Calendar view with photo counts
 *
 * Features:
 * - Large calendar display
 * - Photo counts on dates
 * - Preview thumbnails on hover
 * - Easy navigation
 */

import React, { useState, useEffect } from 'react'
import Calendar from 'react-calendar'
import 'react-calendar/dist/Calendar.css'
import { photoService } from '../../api/services'
import type { CalendarMonthResponse, Photo } from '../../api/types'
import { format, parseISO } from 'date-fns'

interface PhotoCalendarProps {
  onDateSelect?: (date: Date, photos: Photo[]) => void
  className?: string
}

export const PhotoCalendar: React.FC<PhotoCalendarProps> = ({
  onDateSelect,
  className = '',
}) => {
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [monthData, setMonthData] = useState<CalendarMonthResponse | null>(null)
  const [, setLoading] = useState(false)

  useEffect(() => {
    loadMonthData(selectedDate)
  }, [selectedDate])

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

  const getPhotosForDate = (date: Date): number => {
    if (!monthData) return 0

    const dateStr = format(date, 'yyyy-MM-dd')
    const dateData = monthData.dates.find((d) => {
      const dStr = format(parseISO(d.date), 'yyyy-MM-dd')
      return dStr === dateStr
    })

    return dateData?.photo_count || 0
  }

  const handleDateClick = (date: Date) => {
    if (!monthData) return

    const dateStr = format(date, 'yyyy-MM-dd')
    const dateData = monthData.dates.find((d) => {
      const dStr = format(parseISO(d.date), 'yyyy-MM-dd')
      return dStr === dateStr
    })

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
        <span className="inline-block bg-blue-800 text-white text-xs font-bold px-2 py-1 rounded-full">
          {count}
        </span>
      </div>
    )
  }

  return (
    <div className={`photo-calendar ${className}`}>
      <style>{`
        .photo-calendar .react-calendar {
          width: 100%;
          border: 2px solid #e5e7eb;
          border-radius: 0.75rem;
          font-family: inherit;
          line-height: 1.5;
        }
        .photo-calendar .react-calendar__tile {
          padding: 1.25rem 0.5rem;
          font-size: 1.125rem;
          min-height: 80px;
        }
        .photo-calendar .react-calendar__tile:enabled:hover {
          background-color: #eff6ff;
        }
        .photo-calendar .react-calendar__tile--active {
          background-color: #1e40af !important;
          color: white;
        }
        .photo-calendar .react-calendar__month-view__weekdays {
          font-size: 1.125rem;
          font-weight: 600;
          text-transform: uppercase;
        }
        .photo-calendar .react-calendar__navigation button {
          font-size: 1.25rem;
          min-height: 48px;
        }
      `}</style>

      <Calendar
        value={selectedDate}
        onClickDay={handleDateClick}
        onActiveStartDateChange={({ activeStartDate }) =>
          activeStartDate && setSelectedDate(activeStartDate)
        }
        tileContent={tileContent}
        className="text-lg"
      />

      {monthData && (
        <div className="mt-6 p-6 bg-gray-50 rounded-lg">
          <p className="text-xl text-gray-700">
            <span className="font-semibold">{monthData.total_photos}</span> photos in{' '}
            {format(selectedDate, 'MMMM yyyy')}
          </p>
        </div>
      )}
    </div>
  )
}

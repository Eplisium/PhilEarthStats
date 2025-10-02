import React, { useEffect, useState } from 'react';
import { Calendar, ChevronLeft, ChevronRight, AlertCircle, TrendingUp, Download, RefreshCw, CalendarClock } from 'lucide-react';
import useCalendarStore from '../store/useCalendarStore';
import CustomTooltip from './CustomTooltip';

const EarthquakeCalendar = () => {
  // Use Zustand store
  const {
    currentDate,
    calendarData,
    selectedDate,
    setSelectedDate,
    loading,
    worstYears,
    changeMonth,
    getEventsForDate,
    initialize,
    setCurrentDate,
    syncing,
    syncStatus,
    syncDateRange,
  } = useCalendarStore();

  // Local state for month/year picker
  const [showMonthPicker, setShowMonthPicker] = useState(false);
  const [showYearPicker, setShowYearPicker] = useState(false);

  useEffect(() => {
    initialize();
  }, [initialize]);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showMonthPicker || showYearPicker) {
        const target = event.target;
        const isMonthButton = target.closest('button')?.textContent === currentDate.toLocaleDateString('en-US', { month: 'long' });
        const isYearButton = target.closest('button')?.textContent === String(currentDate.getFullYear());
        const isInDropdown = target.closest('.month-picker-dropdown') || target.closest('.year-picker-dropdown');
        
        if (!isMonthButton && !isYearButton && !isInDropdown) {
          setShowMonthPicker(false);
          setShowYearPicker(false);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showMonthPicker, showYearPicker, currentDate]);

  const getDaysInMonth = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    return { daysInMonth, startingDayOfWeek };
  };

  const getMagnitudeColor = (magnitude) => {
    if (magnitude >= 7.0) return 'bg-red-600';
    if (magnitude >= 6.0) return 'bg-red-500';
    if (magnitude >= 5.0) return 'bg-orange-500';
    if (magnitude >= 4.0) return 'bg-yellow-500';
    if (magnitude >= 3.0) return 'bg-green-500';
    return 'bg-gray-400';
  };

  const getSeverityBadge = (damageLevel) => {
    const colors = {
      'Severe': 'bg-red-600 text-white',
      'High': 'bg-orange-500 text-white',
      'Moderate': 'bg-yellow-500 text-gray-900',
      'Low': 'bg-green-500 text-white'
    };
    return colors[damageLevel] || 'bg-gray-400 text-white';
  };

  const renderCalendarDays = () => {
    const { daysInMonth, startingDayOfWeek } = getDaysInMonth();
    const days = [];
    
    // Empty cells for days before the first of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(<div key={`empty-${i}`} className="h-20 border border-gray-200 bg-gray-50"></div>);
    }
    
    // Days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const dayEvents = getEventsForDate(day);
      const hasEvents = dayEvents && dayEvents.event_count > 0;
      
      days.push(
        <div
          key={day}
          onClick={() => hasEvents && setSelectedDate(dayEvents)}
          className={`h-20 border border-gray-200 p-2 transition-all duration-200 ${
            hasEvents ? 'cursor-pointer hover:bg-purple-50 hover:shadow-md' : 'bg-white'
          }`}
        >
          <div className="flex flex-col h-full">
            <span className="text-sm font-semibold text-gray-700">{day}</span>
            {hasEvents && (
              <div className="mt-auto">
                <div className={`w-full h-2 rounded-full ${getMagnitudeColor(dayEvents.max_magnitude)}`}></div>
                <div className="text-xs text-gray-600 mt-1">
                  {dayEvents.event_count} event{dayEvents.event_count > 1 ? 's' : ''}
                </div>
                <div className="text-xs font-bold text-gray-800">
                  M{dayEvents.max_magnitude.toFixed(1)}
                </div>
              </div>
            )}
          </div>
        </div>
      );
    }
    
    return days;
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  };

  const handleMonthSelect = (monthIndex) => {
    const newDate = new Date(currentDate.getFullYear(), monthIndex, 1);
    setCurrentDate(newDate);
    setShowMonthPicker(false);
  };

  const handleYearSelect = (year) => {
    const newDate = new Date(year, currentDate.getMonth(), 1);
    setCurrentDate(newDate);
    setShowYearPicker(false);
  };

  const generateYearRange = () => {
    const currentYear = new Date().getFullYear();
    const years = [];
    for (let i = currentYear; i >= 1900; i--) {
      years.push(i);
    }
    return years;
  };

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  return (
    <div className="space-y-6">
      {/* Worst Years Section */}
      <div className="bg-gradient-to-r from-red-50 to-orange-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <AlertCircle className="h-6 w-6 text-red-600" />
          Worst Earthquake Years in Philippine History
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {worstYears.slice(0, 6).map((yearData, index) => (
            <div
              key={yearData.year}
              className="bg-white rounded-lg p-4 shadow-md hover:shadow-lg transition-shadow duration-200"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <span className="text-2xl font-bold text-gray-900">{yearData.year}</span>
                  <span className={`ml-2 px-2 py-1 text-xs rounded-full ${getSeverityBadge(yearData.damage_level)}`}>
                    {yearData.damage_level}
                  </span>
                </div>
                <span className="text-xs text-gray-500">#{index + 1}</span>
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Max Magnitude:</span>
                  <span className="font-bold text-red-600">M{yearData.max_magnitude.toFixed(1)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Events:</span>
                  <span className="font-semibold">{yearData.total_events}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Major Events:</span>
                  <span className="font-semibold">{yearData.major_events}</span>
                </div>
                {yearData.deaths_estimated > 0 && (
                  <div className="flex justify-between text-red-600">
                    <span>Est. Deaths:</span>
                    <span className="font-semibold">{yearData.deaths_estimated.toLocaleString()}</span>
                  </div>
                )}
                <div className="mt-2 pt-2 border-t">
                  <span className="text-xs text-gray-500">Severity Score: {yearData.severity_score}</span>
                </div>
              </div>
              {yearData.notable_events && yearData.notable_events.length > 0 && (
                <div className="mt-3 pt-3 border-t">
                  <p className="text-xs font-semibold text-gray-700 mb-1">Notable Event:</p>
                  <p className="text-xs text-gray-600">
                    {yearData.notable_events[0].description}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Calendar Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Calendar className="h-6 w-6 text-purple-600" />
            Earthquake Calendar & Timeline
          </h3>
          <div className="flex items-center gap-4 relative">
            <CustomTooltip text="Previous month" position="bottom">
              <button
                onClick={() => changeMonth(-1)}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
            </CustomTooltip>
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  setShowMonthPicker(!showMonthPicker);
                  setShowYearPicker(false);
                }}
                className="text-lg font-semibold text-gray-800 hover:text-purple-600 transition-colors px-2 py-1 rounded hover:bg-purple-50 cursor-pointer"
              >
                {currentDate.toLocaleDateString('en-US', { month: 'long' })}
              </button>
              <button
                onClick={() => {
                  setShowYearPicker(!showYearPicker);
                  setShowMonthPicker(false);
                }}
                className="text-lg font-semibold text-gray-800 hover:text-purple-600 transition-colors px-2 py-1 rounded hover:bg-purple-50 cursor-pointer"
              >
                {currentDate.getFullYear()}
              </button>
            </div>
            <CustomTooltip text="Next month" position="bottom">
              <button
                onClick={() => changeMonth(1)}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <ChevronRight className="h-5 w-5" />
              </button>
            </CustomTooltip>
            
            {/* Go to Today Button */}
            <CustomTooltip text="Go to current month" position="bottom">
              <button
                onClick={() => setCurrentDate(new Date())}
                className="ml-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all font-medium text-sm flex items-center gap-2 hover:shadow-md"
              >
                <CalendarClock className="h-4 w-4" />
                Today
              </button>
            </CustomTooltip>
            
            {/* Manual Refresh Button */}
            <CustomTooltip text="Refresh/fetch data for this month" position="bottom">
              <button
              onClick={() => {
                const year = currentDate.getFullYear();
                const month = currentDate.getMonth() + 1;
                const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
                const lastDay = new Date(year, month, 0).getDate();
                const endDate = `${year}-${String(month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;
                syncDateRange(startDate, endDate);
              }}
              disabled={syncing}
              className={`ml-2 px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-all ${
                syncing
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-purple-600 text-white hover:bg-purple-700 hover:shadow-md'
              }`}
              >
                <RefreshCw className={`h-4 w-4 ${syncing ? 'animate-spin' : ''}`} />
                {syncing ? 'Syncing...' : 'Refresh'}
              </button>
            </CustomTooltip>

            {/* Month Picker Dropdown */}
            {showMonthPicker && (
              <div className="month-picker-dropdown absolute top-12 right-0 bg-white border-2 border-purple-300 rounded-lg shadow-xl p-4 z-50 w-64">
                <div className="grid grid-cols-3 gap-2">
                  {months.map((month, index) => (
                    <button
                      key={month}
                      onClick={() => handleMonthSelect(index)}
                      className={`px-3 py-2 rounded text-sm font-medium transition-all ${
                        currentDate.getMonth() === index
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-100 hover:bg-purple-100 text-gray-700 hover:text-purple-700'
                      }`}
                    >
                      {month.substring(0, 3)}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Year Picker Dropdown */}
            {showYearPicker && (
              <div className="year-picker-dropdown absolute top-12 right-0 bg-white border-2 border-purple-300 rounded-lg shadow-xl p-4 z-50 w-64 max-h-80 overflow-y-auto">
                <div className="grid grid-cols-3 gap-2">
                  {generateYearRange().map((year) => (
                    <button
                      key={year}
                      onClick={() => handleYearSelect(year)}
                      className={`px-3 py-2 rounded text-sm font-medium transition-all ${
                        currentDate.getFullYear() === year
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-100 hover:bg-purple-100 text-gray-700 hover:text-purple-700'
                      }`}
                    >
                      {year}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Sync Status Banner */}
        {(syncing || syncStatus) && (
          <div className={`mb-4 p-3 rounded-lg border-2 flex items-center gap-3 ${
            syncing 
              ? 'bg-blue-50 border-blue-300 text-blue-800'
              : 'bg-green-50 border-green-300 text-green-800'
          }`}>
            {syncing ? (
              <RefreshCw className="h-5 w-5 animate-spin" />
            ) : (
              <Download className="h-5 w-5" />
            )}
            <span className="font-medium">{syncStatus}</span>
          </div>
        )}

        {/* No Data Message with Sync Option */}
        {!loading && !syncing && calendarData.length === 0 && (() => {
          const now = new Date();
          const year = currentDate.getFullYear();
          const month = currentDate.getMonth() + 1;
          const isFutureMonth = year > now.getFullYear() || 
                               (year === now.getFullYear() && month > now.getMonth() + 1);
          const isPastMonth = year < now.getFullYear() || 
                             (year === now.getFullYear() && month < now.getMonth() + 1);
          
          return (
            <div className="mb-4 p-4 bg-yellow-50 border-2 border-yellow-300 rounded-lg">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-yellow-800 mb-2">
                    No earthquake data available for {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                  </p>
                  {isFutureMonth ? (
                    <p className="text-xs text-yellow-700">
                      This is a future month. No data is available yet.
                    </p>
                  ) : year < 2000 ? (
                    <p className="text-xs text-yellow-700">
                      USGS historical data is limited before year 2000.
                    </p>
                  ) : (
                    <>
                      <p className="text-xs text-yellow-700 mb-3">
                        Historical data can be fetched from USGS for past months and years.
                      </p>
                      <button
                        onClick={() => {
                          const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
                          const lastDay = new Date(year, month, 0).getDate();
                          const endDate = `${year}-${String(month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;
                          syncDateRange(startDate, endDate);
                        }}
                        className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors text-sm font-medium flex items-center gap-2"
                      >
                        <Download className="h-4 w-4" />
                        Fetch Historical Data
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          );
        })()}

        {/* Calendar Legend */}
        <div className="mb-4 flex flex-wrap gap-3 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded bg-gray-400"></div>
            <span>M &lt; 3.0</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded bg-green-500"></div>
            <span>M 3.0-3.9</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded bg-yellow-500"></div>
            <span>M 4.0-4.9</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded bg-orange-500"></div>
            <span>M 5.0-5.9</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded bg-red-500"></div>
            <span>M 6.0-6.9</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded bg-red-600"></div>
            <span>M ≥ 7.0</span>
          </div>
        </div>

        {/* Day headers */}
        <div className="grid grid-cols-7 mb-2">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="text-center font-semibold text-gray-600 text-sm py-2">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-purple-600"></div>
          </div>
        ) : (
          <div className="grid grid-cols-7 gap-1">
            {renderCalendarDays()}
          </div>
        )}
      </div>

      {/* Event Details Panel */}
      {selectedDate && (
        <div className="bg-white border border-purple-200 rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900">
              Events on {selectedDate.date}
            </h3>
            <button
              onClick={() => setSelectedDate(null)}
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              Close
            </button>
          </div>
          <div className="space-y-3">
            {selectedDate.events.map((event, index) => (
              <div
                key={event.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <span className={`inline-block px-3 py-1 rounded-full text-white font-bold ${getMagnitudeColor(event.magnitude)}`}>
                      M{event.magnitude.toFixed(1)}
                    </span>
                    <span className="ml-2 text-gray-600 text-sm">
                      {formatTime(event.time)}
                    </span>
                  </div>
                </div>
                <p className="text-sm font-semibold text-gray-800 mb-1">{event.place}</p>
                <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                  <div>Depth: {event.depth.toFixed(1)} km</div>
                  <div>Lat: {event.latitude.toFixed(3)}</div>
                  <div>Significance: {event.significance || 'N/A'}</div>
                  <div>Lon: {event.longitude.toFixed(3)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>Historical Tracking:</strong> This system stores earthquake data from USGS and can fetch historical events from past years.
          Calendar shows events by date with color-coded magnitude indicators. 
          Click on any date with events to see detailed information with precise timestamps.
          When browsing past months, the system automatically fetches historical data if not yet stored.
        </p>
      </div>
    </div>
  );
};

export default EarthquakeCalendar;

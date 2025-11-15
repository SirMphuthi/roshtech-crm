import React, { useState, useEffect } from 'react';
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { parse, startOfWeek, getDay, format } from 'date-fns';
import EventModal from '../components/Calendar/EventModal';

const locales = {
  'en-US': require('date-fns/locale/en-US'),
};
const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek: () => startOfWeek(new Date(), { weekStartsOn: 1 }),
  getDay,
  locales,
});

const BACKEND_API = 'http://localhost:5000';

const CalendarPage = () => {
  const [events, setEvents] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [eventToEdit, setEventToEdit] = useState(null);
  const [slotInfo, setSlotInfo] = useState(null);

  const fetchEvents = () => {
    fetch(`${BACKEND_API}/api/calendar-events`)
      .then(res => res.json())
      .then(data => {
        if (data.items) {
          setEvents(data.items.map(ev => ({
            ...ev,
            start: new Date(ev.start),
            end: new Date(ev.end),
          })));
        } else {
          setEvents([]);
        }
      })
      .catch(err => console.error('Failed to fetch events:', err));
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleSelectSlot = (slot) => {
    setSlotInfo(slot);
    setEventToEdit(null);
    setIsModalOpen(true);
  };

  const handleSelectEvent = (event) => {
    setEventToEdit(event);
    setSlotInfo(null);
    setIsModalOpen(true);
  };

  return (
    <div className="calendar-page">
      <h1 className="page-title">Calendar</h1>
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 600 }}
        selectable
        onSelectSlot={handleSelectSlot}
        onSelectEvent={handleSelectEvent}
      />
      <EventModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        eventToEdit={eventToEdit}
        slotInfo={slotInfo}
        onSave={fetchEvents}
      />
    </div>
  );
};

export default CalendarPage;
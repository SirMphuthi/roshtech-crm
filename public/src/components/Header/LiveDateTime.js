import React, { useState, useEffect } from 'react';
import { FiClock, FiCalendar } from 'react-icons/fi';
import './Header.css'; // We'll add a style to Header.css

const LiveDateTime = () => {
  const [dateTime, setDateTime] = useState(new Date());

  useEffect(() => {
    // Update the time every second
    const timer = setInterval(() => {
      setDateTime(new Date());
    }, 1000);

    // Clean up the interval on component unmount
    return () => clearInterval(timer);
  }, []);

  const formatDate = (date) => {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString(undefined, options);
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString();
  };

  return (
    <div className="live-datetime">
      <div className="live-date">
        <FiCalendar className="datetime-icon" />
        <span>{formatDate(dateTime)}</span>
      </div>
      <div className="live-time">
        <FiClock className="datetime-icon" />
        <span>{formatTime(dateTime)}</span>
      </div>
    </div>
  );
};

// **ADD THIS CSS TO `Header.css`**
/*
.live-datetime {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.live-date, .live-time {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.datetime-icon {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
}

@media (max-width: 1024px) {
  .live-datetime {
    display: none;
  }
}
*/
export default LiveDateTime;
import React from 'react';

export default function StatsCard({ title, value, subtitle }) {
  return (
    <div className="card stats-card">
      <div className="stats-card__title">{title}</div>
      <div className="stats-card__value">{value}</div>
      {subtitle ? <div className="stats-card__subtitle">{subtitle}</div> : null}
    </div>
  );
}

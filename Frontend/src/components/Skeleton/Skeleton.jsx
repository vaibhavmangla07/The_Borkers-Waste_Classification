import React from 'react';
import './Skeleton.css';

export function Skeleton({ width = '100%', height = '20px', borderRadius = 'var(--radius-sm)', className = '' }) {
  return (
    <div
      className={`skeleton-loader ${className}`}
      style={{
        width,
        height,
        borderRadius
      }}
      aria-hidden="true"
    />
  );
}

export default Skeleton;

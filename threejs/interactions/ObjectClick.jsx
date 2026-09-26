import React from 'react';

/**
 * ObjectClick wrapper
 * Captures pointer clicks with event propagation stopping
 */
export default function ObjectClick({ children, onClick }) {
  const handleClick = (e) => {
    e.stopPropagation();
    if (onClick) onClick(e);
  };

  return (
    <group onClick={handleClick}>
      {children}
    </group>
  );
}

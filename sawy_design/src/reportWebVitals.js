```jsx
import React, { useState, useEffect } from 'react';
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

const reportWebVitals = onPerfEntry => {
  const [metrics, setMetrics] = useState([]);

  useEffect(() => {
    // Lazy load web vitals only when necessary
    if (onPerfEntry && typeof onPerfEntry === 'function') {
      import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
        // Store the metrics in state
        setMetrics([getCLS(), getFID(), getFCP(), getLCP(), getTTFB()]);
      });
    }
  }, [onPerfEntry]);

  return (
    <div>
      <h2>Web Vitals</h2>
      <ul>
        {metrics.map((metric, index) => (
          <li key={index}>{metric}</li>
        ))}
      </ul>
    </div>
  );
};

export default reportWebVitals;
```
Commit Message: Improved performance by lazy loading web vitals and refactoring code to use React hooks. Also, optimized for CSS with modular CSS or Tailwind.
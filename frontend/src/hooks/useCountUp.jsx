import { useEffect, useRef, useState } from 'react';

/**
 * Custom hook for animating numbers with count-up effect
 * @param {number} end - The target number to count up to
 * @param {number} duration - Animation duration in milliseconds (default: 1000)
 * @param {number} decimals - Number of decimal places (default: 0)
 * @returns {number} The current animated value
 */
const useCountUp = (end, duration = 1000, decimals = 0) => {
  const [count, setCount] = useState(0);
  const startTimeRef = useRef(null);
  const startValueRef = useRef(0);
  const animationFrameRef = useRef(null);

  useEffect(() => {
    // Store the starting value (current count)
    const startValue = count;
    startValueRef.current = startValue;
    
    // If end value is the same as current, no animation needed
    if (startValue === end) return;

    // Reset start time for new animation
    startTimeRef.current = null;

    const animate = (timestamp) => {
      if (!startTimeRef.current) {
        startTimeRef.current = timestamp;
      }

      const progress = Math.min((timestamp - startTimeRef.current) / duration, 1);
      
      // Use easeOutExpo easing function for smooth deceleration
      const easeOutExpo = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      
      const currentValue = startValueRef.current + (end - startValueRef.current) * easeOutExpo;
      
      setCount(currentValue);

      if (progress < 1) {
        animationFrameRef.current = requestAnimationFrame(animate);
      } else {
        setCount(end); // Ensure we end exactly at the target value
      }
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [end, duration]);

  // Return the count formatted with specified decimal places
  return decimals > 0 ? parseFloat(count.toFixed(decimals)) : Math.floor(count);
};

export default useCountUp;

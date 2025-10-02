import { useRef } from 'react';

/**
 * Custom hook for shallow equality comparison in Zustand
 * Prevents unnecessary re-renders when objects have the same values
 * @param {Function} selector - Selector function
 * @returns {any} The selected value
 */
export const useShallow = (selector) => {
  const prev = useRef();
  
  return (state) => {
    const next = selector(state);
    
    if (shallowEqual(prev.current, next)) {
      return prev.current;
    }
    
    prev.current = next;
    return next;
  };
};

/**
 * Shallow equality check
 */
function shallowEqual(objA, objB) {
  if (objA === objB) {
    return true;
  }

  if (!objA || !objB) {
    return false;
  }

  const keysA = Object.keys(objA);
  const keysB = Object.keys(objB);

  if (keysA.length !== keysB.length) {
    return false;
  }

  // Test for A's keys different from B.
  for (let i = 0; i < keysA.length; i++) {
    if (!objB.hasOwnProperty(keysA[i]) || objA[keysA[i]] !== objB[keysA[i]]) {
      return false;
    }
  }

  return true;
}

export default useShallow;

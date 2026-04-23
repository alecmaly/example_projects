import React, { useState } from 'react';

export function Counter() {
    const [count, setCount] = useState(0);
    function handleIncrement() { setCount(count + 1); }
    function handleReset() { setCount(0); }
    return (
        <div>
            <button onClick={handleIncrement}>+1</button>
            <button onClick={handleReset}>reset</button>
            <span>{count}</span>
        </div>
    );
}

export function App() {
    return <Counter />;
}

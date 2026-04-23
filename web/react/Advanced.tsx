import React, {
    useState,
    useEffect,
    useReducer,
    useContext,
    useMemo,
    useCallback,
    useRef,
    memo,
    createContext,
    Component,
    forwardRef,
    useImperativeHandle,
} from 'react';

// --- Context + provider + consumer via useContext.
interface Theme { bg: string; fg: string; }
const ThemeCtx = createContext<Theme>({ bg: '#fff', fg: '#000' });

// --- useReducer / discriminated-union actions.
type Action = { type: 'inc' } | { type: 'dec' } | { type: 'set'; value: number };
function reducer(state: { count: number }, action: Action): { count: number } {
    switch (action.type) {
        case 'inc':  return { count: state.count + 1 };
        case 'dec':  return { count: state.count - 1 };
        case 'set':  return { count: action.value };
    }
}

// --- Custom hook.
export function useDoubled(n: number): number {
    return useMemo(() => n * 2, [n]);
}

// --- forwardRef + useImperativeHandle.
interface InputHandle { focus: () => void; }
export const FocusableInput = forwardRef<InputHandle, { placeholder: string }>((props, ref) => {
    const inputRef = useRef<HTMLInputElement>(null);
    useImperativeHandle(ref, () => ({
        focus: () => inputRef.current?.focus(),
    }));
    return <input ref={inputRef} placeholder={props.placeholder} />;
});

// --- Class component (legacy API still parsed by LSP).
interface TimerProps { initial: number; }
interface TimerState { seconds: number; }
export class Timer extends Component<TimerProps, TimerState> {
    timer?: ReturnType<typeof setInterval>;
    constructor(props: TimerProps) {
        super(props);
        this.state = { seconds: props.initial };
    }
    componentDidMount() {
        this.timer = setInterval(() => this.setState(s => ({ seconds: s.seconds + 1 })), 1000);
    }
    componentWillUnmount() { if (this.timer) clearInterval(this.timer); }
    render() { return <span>{this.state.seconds}</span>; }
}

// --- memo-wrapped pure child.
export const ExpensiveRow = memo(function ExpensiveRow({ label }: { label: string }) {
    return <li>{label}</li>;
});

// --- Full feature demo.
export function Advanced() {
    const [state, dispatch] = useReducer(reducer, { count: 0 });
    const theme = useContext(ThemeCtx);
    const [name, setName] = useState('world');
    const doubled = useDoubled(state.count);
    const handleInc = useCallback(() => dispatch({ type: 'inc' }), []);
    const inputRef = useRef<InputHandle>(null);

    useEffect(() => {
        document.title = `count=${state.count}`;
        return () => { /* cleanup on unmount / re-run */ };
    }, [state.count]);

    return (
        <ThemeCtx.Provider value={theme}>
            <div style={{ background: theme.bg, color: theme.fg }}>
                <button onClick={handleInc}>+1 ({doubled})</button>
                <button onClick={() => dispatch({ type: 'set', value: 0 })}>reset</button>
                <input value={name} onChange={e => setName(e.target.value)} />
                <FocusableInput ref={inputRef} placeholder="focus me" />
                <button onClick={() => inputRef.current?.focus()}>focus</button>
                <ul>
                    {['a', 'b', 'c'].map(x => <ExpensiveRow key={x} label={x} />)}
                </ul>
                <Timer initial={0} />
            </div>
        </ThemeCtx.Provider>
    );
}

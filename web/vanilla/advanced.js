// Vanilla JS — events, async/await, fetch, DOM, ES modules, classes.

// 1. ES module export (so the LSP sees export tracking).
export class CounterStore extends EventTarget {
    constructor(initial = 0) {
        super();
        this._count = initial;
    }
    get count() { return this._count; }
    increment() {
        this._count++;
        this.dispatchEvent(new CustomEvent('changed', { detail: this._count }));
    }
    reset() {
        this._count = 0;
        this.dispatchEvent(new CustomEvent('changed', { detail: 0 }));
    }
}

// 2. async/await + fetch.
export async function loadWidget(url) {
    try {
        const res = await fetch(url, {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error('loadWidget failed:', err);
        return null;
    }
}

// 3. DOM event wiring — addEventListener with closure capture.
export function wire(store, buttonEl, displayEl) {
    buttonEl.addEventListener('click', () => store.increment());
    store.addEventListener('changed', (e) => {
        displayEl.textContent = String(e.detail);
    });
}

// 4. Promise.all fan-out.
export function loadAll(urls) {
    return Promise.all(urls.map(u => loadWidget(u)));
}

// 5. Proxy for reactive property access (low-level JS).
export function reactiveCounter() {
    const target = { n: 0 };
    return new Proxy(target, {
        set(obj, prop, value) {
            console.log(`set ${String(prop)}=${value}`);
            obj[prop] = value;
            return true;
        },
    });
}

// 6. Generator.
export function* naturalNumbers() {
    let i = 0;
    while (true) yield i++;
}

// 7. WeakMap for private state.
const _private = new WeakMap();
export class SecretBox {
    constructor(secret) { _private.set(this, secret); }
    reveal() { return _private.get(this); }
}

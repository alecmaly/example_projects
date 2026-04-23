// Vue Composition-API composable — the "custom hook" of the Vue world.
import { ref, computed, watch, onMounted, onUnmounted, type Ref } from 'vue';

export interface UseCounter {
    count: Ref<number>;
    doubled: Readonly<Ref<number>>;
    increment: () => void;
    reset: () => void;
}

export function useCounter(initial = 0): UseCounter {
    const count = ref(initial);
    const doubled = computed(() => count.value * 2);

    function increment() { count.value++; }
    function reset()     { count.value = 0; }

    watch(count, (n, prev) => {
        console.log(`count changed from ${prev} to ${n}`);
    });

    onMounted(() => console.log('mounted'));
    onUnmounted(() => console.log('unmounted'));

    return { count, doubled, increment, reset };
}

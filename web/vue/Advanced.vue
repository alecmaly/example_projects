<template>
    <div>
        <button @click="increment">+1 ({{ doubled }})</button>
        <button @click="reset">reset</button>
        <input v-model="name" />
        <ul>
            <li v-for="item in items" :key="item">{{ item }}</li>
        </ul>
        <span v-if="count > 5">big</span>
        <span v-else>small</span>
        <slot name="footer" />
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, provide, inject } from 'vue';
import { useCounter } from './useCounter';

// --- Props + emits.
interface Props { label?: string; items?: string[]; }
const props = withDefaults(defineProps<Props>(), {
    label: 'counter',
    items: () => ['a', 'b', 'c'],
});
const emit = defineEmits<{
    (e: 'changed', value: number): void;
}>();

// --- Custom composable.
const { count, doubled, increment, reset } = useCounter();

// --- Plain reactive local.
const name = ref('world');

// --- computed.
const summary = computed(() => `${name.value}: ${count.value}`);

// --- provide / inject (context).
provide('theme', { bg: '#fff', fg: '#000' });

// --- lifecycle.
onMounted(() => emit('changed', count.value));

console.log(summary.value, props.label);
</script>

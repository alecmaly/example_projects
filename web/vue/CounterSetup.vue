<template>
    <button @click="increment">+1</button>
    <button @click="reset">reset</button>
    <span>{{ count }}</span>
</template>

<script setup>
import { ref } from 'vue';
const count = ref(0);
function increment() { count.value++; }
function reset() { count.value = 0; }
</script>

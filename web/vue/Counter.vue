<template>
    <div>
        <button @click="increment">+1</button>
        <button v-on:click="reset">reset</button>
        <span>{{ count }}</span>
    </div>
</template>

<script>
export default {
    data() { return { count: 0 }; },
    methods: {
        increment() { this.count++; },
        reset() { this.count = 0; },
    }
};
</script>

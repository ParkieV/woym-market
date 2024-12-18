<script lang="ts">
    export let size: `${number}px`;
</script>

<span style:--size={size} />

<style lang="scss">
    span {
        display: inline-block;
        width: var(--size, 24px);
        height: var(--size, 24px);
        border-radius: calc(var(--size, 24px) / 2);

        border-color: black;
        border-style: solid;
        border-bottom-color: transparent;

        animation: rotation 1s linear infinite;
    }

    @keyframes rotation {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }
</style>

<script lang="ts">
    export let value: boolean = false;
    export let image: string;
    export let alt: string = "";
</script>

<button on:click={() => (value = !value)} title={alt} class:enabled={value}>
    <img src={image} {alt} />
</button>

<style lang="scss">
    @use "./style.scss" as *;
    button {
        @include filter-btn;
        @include square;
        padding: 4px;
        border: 0;
        border-radius: 4px;

        &.enabled {
            > img {
                filter: invert(1);
            }
        }
        > img {
            height: 24px;
            width: 24px;
        }
    }
</style>
